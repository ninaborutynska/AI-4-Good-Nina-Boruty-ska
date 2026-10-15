"""Local transformer inference and interruption-safe CSV storage."""
from __future__ import annotations

import csv
import hashlib
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
LABELS = ("Negative", "Neutral", "Positive")
RESULT_COLUMNS = ["comment_id", "sentiment", "confidence", "model_version", "analysed_at"]
STATUS_COLUMNS = ["comment_id", "status", "reason", "language", "quality_flags", "text_hash", "checked_at"]


def now():
    return datetime.now(timezone.utc).isoformat()


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_rows(path, required):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError(f"Invalid columns in {path.name}; required: {', '.join(required)}")
        rows = {}
        for row in reader:
            identifier = (row.get("comment_id") or "").strip()
            if not identifier or identifier in rows:
                raise ValueError(f"Missing or duplicate comment_id in {path.name}")
            rows[identifier] = row
        return rows


def atomic_csv(path, columns, rows):
    """An interrupted write leaves the previous complete checkpoint intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate(text):
    """Language/relevance checks are heuristics, not verified annotations."""
    from langdetect import DetectorFactory, detect_langs, LangDetectException
    DetectorFactory.seed = 0
    flags = ["relevance_not_verified"]
    if not text.strip():
        return "empty", "Comment text is empty", "", flags
    if "\x00" in text or "\ufffd" in text:
        return "malformed", "Comment contains invalid text characters", "", flags
    letters = sum(character.isalpha() for character in text)
    language = "und"
    if letters < 60:
        flags.append("short_text_language_uncertain")
    else:
        try:
            languages = detect_langs(text)
            language = languages[0].lang
            if language != "en" and languages[0].prob >= .98:
                return "unsupported_language", "English model: detected another language", language, flags
            if language != "en" or languages[0].prob < .90:
                flags.append("language_uncertain")
        except LangDetectException:
            flags.append("language_uncertain")
    if re.search(r"https?://", text) or re.search(r"(.)\1{9,}", text):
        flags.append("possible_spam")
    return "eligible", "", language, flags


def preprocess(text):
    return " ".join("@user" if word.startswith("@") and len(word) > 1 else
                    "http" if word.startswith("http") else word for word in text.split())


class Classifier:
    def __init__(self, cache_dir, revision="main", device="auto", threads=4):
        import torch
        from huggingface_hub import try_to_load_from_cache
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        torch.set_num_threads(threads)
        self.torch = torch
        self.device = "cuda" if device == "auto" and torch.cuda.is_available() else "cpu" if device == "auto" else device
        options = dict(cache_dir=str(cache_dir), revision=revision, trust_remote_code=False)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, **options)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, **options).to(self.device).eval()
        cached_config = try_to_load_from_cache(MODEL_ID, "config.json", cache_dir=str(cache_dir), revision=revision)
        commit = Path(cached_config).parent.name if isinstance(cached_config, str) else getattr(self.model.config, "_commit_hash", None) or revision
        self.version = f"{MODEL_ID}@{commit}"
        self.max_length = min(512, self.tokenizer.model_max_length, self.model.config.max_position_embeddings - 2)
        self.labels = [str(self.model.config.id2label[i]).capitalize() for i in range(3)]
        if set(self.labels) != set(LABELS):
            raise ValueError("Model label mapping does not match Positive, Neutral, Negative")

    def predict(self, texts):
        tokens = self.tokenizer([preprocess(text) for text in texts], padding=True, truncation=True,
                                max_length=self.max_length, return_tensors="pt")
        with self.torch.inference_mode():
            probabilities = self.model(**{key: value.to(self.device) for key, value in tokens.items()}).logits.softmax(-1)
            scores, indices = probabilities.max(-1)
        predictions = [(self.labels[index], float(score)) for index, score in zip(indices.cpu().tolist(), scores.cpu().tolist())]
        if any(not math.isfinite(score) or not 0 <= score <= 1 for _, score in predictions):
            raise ValueError("Model returned an invalid confidence score")
        return predictions
