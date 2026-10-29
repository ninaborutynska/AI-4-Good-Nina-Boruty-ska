"""BinWatch – spots rubbish dumped beside underground bins and bags torn open by gulls.

Upload one or more photos of underground bins. The app sends each photo to our
Roboflow object-detection model, draws what it found, and ranks the bins so a
collection crew knows which ones to clear first.
"""

import base64
import html
import io

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------------------------------------------------------------- settings
API_URL = st.secrets.get("ROBOFLOW_API_URL", "https://serverless.roboflow.com")  # Roboflow hosted inference
MODEL_ID = st.secrets.get("ROBOFLOW_MODEL_ID", "")  # plain model, e.g. "bin-bags/1"
WORKSPACE = st.secrets.get("ROBOFLOW_WORKSPACE", "")  # workflow endpoint (Deploy > Cloud API)
WORKFLOW_ID = st.secrets.get("ROBOFLOW_WORKFLOW_ID", "")
API_KEY = st.secrets.get("ROBOFLOW_API_KEY", "")
MAX_SIDE = 1280  # shrink big phone photos before sending

CLASS_STYLE = {  # class -> (box colour, label shown to the user)
    "torn_bag": ("#C8352B", "Torn bag"),
    "loose_litter": ("#E07A1F", "Loose litter"),
    "bag": ("#2F6FD0", "Bag"),
    "dumped_item": ("#8B5FBF", "Dumped item"),
}

# Priority rules: torn bags / loose litter mean gulls (or wind) are already
# spreading rubbish, so those bins go first.
PRIORITY = [  # (rank, label, explanation, css class)
    (3, "Clear first", "Rubbish is already spreading: a torn bag or loose litter was found.", "urgent"),
    (2, "Clear on next round", "Bags or other items are beside the bin. Gulls can tear bags open, and big items may need a bulky-waste (grofvuil) pickup.", "soon"),
    (1, "Clean", "Nothing found beside the bin. No action needed.", "clean"),
]


# ---------------------------------------------------------------- helpers
def prepare(file) -> Image.Image:
    """Open an upload, apply the phone's rotation, and shrink it."""
    img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return img


def find_predictions(node) -> list[dict]:
    """Dig the list of detections out of a workflow response, whatever its nesting."""
    if isinstance(node, dict):
        preds = node.get("predictions")
        if isinstance(preds, list) and all(isinstance(p, dict) and "class" in p for p in preds):
            return preds
        for value in node.values():
            found = find_predictions(value)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_predictions(item)
            if found:
                return found
    return []


@st.cache_data(show_spinner=False)
def detect(jpeg_bytes: bytes) -> list[dict]:
    """Send one JPEG to the Roboflow model and return its predictions."""
    if WORKFLOW_ID:  # workflow endpoint (what Roboflow's Deploy page gives for this model)
        resp = requests.post(
            f"{API_URL}/infer/workflows/{WORKSPACE}/{WORKFLOW_ID}",
            json={
                "api_key": API_KEY,
                "inputs": {"image": {"type": "base64", "value": base64.b64encode(jpeg_bytes).decode()}},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return find_predictions(resp.json())
    project, version = MODEL_ID.split("/")
    resp = requests.post(
        f"{API_URL}/{project}/{version}",
        # very low server threshold; the slider filters on our side
        params={"api_key": API_KEY, "confidence": 0.05},
        data=base64.b64encode(jpeg_bytes),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("predictions", [])


def draw(img: Image.Image, preds: list[dict]) -> Image.Image:
    out = img.copy()
    d = ImageDraw.Draw(out)
    width = max(2, out.width // 300)
    try:
        font = ImageFont.load_default(size=max(14, out.width // 45))
    except TypeError:  # older Pillow
        font = ImageFont.load_default()
    for p in preds:
        colour, name = CLASS_STYLE.get(p["class"], ("#ffffff", p["class"]))
        x0, y0 = p["x"] - p["width"] / 2, p["y"] - p["height"] / 2
        x1, y1 = p["x"] + p["width"] / 2, p["y"] + p["height"] / 2
        d.rectangle([x0, y0, x1, y1], outline=colour, width=width)
        text = f"{name} {p['confidence']:.0%}"
        tb = d.textbbox((x0, y0), text, font=font)
        ty = max(0, y0 - (tb[3] - tb[1]) - 4)
        d.rectangle([x0, ty, x0 + (tb[2] - tb[0]) + 6, ty + (tb[3] - tb[1]) + 4], fill=colour)
        d.text((x0 + 3, ty), text, fill="white", font=font)
    return out


def verdict(counts: dict) -> tuple:
    if counts.get("torn_bag") or counts.get("loose_litter"):
        return PRIORITY[0]
    if counts.get("bag") or counts.get("dumped_item"):
        return PRIORITY[1]
    return PRIORITY[2]


# ---------------------------------------------------------------- page
st.set_page_config(page_title="BinWatch", page_icon="🗑️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap');

:root {
  --sea-deep: #143857;
  --sea: #1F5583;
  --wing: #A3B1BD;
  --foam: #EEF2F5;
  --bill-yellow: #F2B630;
  --bill-red: #D2322D;
  --ink: #13202C;
}
html, body, .stApp, [data-testid="stMarkdownContainer"], button, input, label, p, li {
  font-family: 'Archivo', system-ui, sans-serif;
}
.stApp { background: var(--foam); }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1200px; }

/* hero: North Sea, with a wave edge along the bottom */
.bw-hero {
  position: relative;
  background: linear-gradient(180deg, var(--sea) 0%, var(--sea-deep) 100%);
  border-radius: 14px 14px 0 0;
  padding: 30px 32px 44px;
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  gap: 32px;
  align-items: center;
  color: #fff;
}
.bw-hero::after {
  content: "";
  position: absolute; left: 0; right: 0; bottom: -1px; height: 14px;
  background: radial-gradient(circle at 14px 0, var(--sea-deep) 13px, var(--foam) 14px) repeat-x;
  background-size: 28px 14px;
}
.bw-title { display: flex; flex-direction: column; gap: 14px; }
.bw-gull { width: 64px; height: 22px; }
.bw-title h1 {
  font-family: 'Archivo', sans-serif;
  font-stretch: 125%;
  font-weight: 900;
  font-size: clamp(2.6rem, 6vw, 4.4rem);
  line-height: .95;
  letter-spacing: -0.02em;
  margin: 0; padding: 0;
  color: #fff;
}
.bw-title p { font-size: 1.05rem; line-height: 1.45; margin: 0; max-width: 46ch; color: #DCE7F0; }
.bw-rules { color: #DCE7F0; display: flex; flex-direction: column; gap: 14px;
  border-left: 1px solid rgba(255,255,255,.18); padding-left: 28px; }
.bw-rules h3 { color: #fff; font-stretch: 112%; font-weight: 700; font-size: 1rem; margin: 0 0 2px; padding: 0; }
.bw-rule { display: grid; grid-template-columns: 14px 1fr; gap: 12px; align-items: start; font-size: .95rem; line-height: 1.35; }
.bw-dot { width: 14px; height: 14px; border-radius: 50%; margin-top: 3px; }
.bw-dot.urgent { background: var(--bill-red); }
.bw-dot.soon { background: var(--bill-yellow); }
.bw-dot.clean { background: #FFFFFF; }
.bw-rule b { color: #fff; font-weight: 700; }

/* result ticket */
.bw-ticket { border-radius: 8px; padding: 18px 20px; background: #fff; border-left: 10px solid var(--wing); }
.bw-ticket.urgent { border-left-color: var(--bill-red); }
.bw-ticket.soon { border-left-color: var(--bill-yellow); }
.bw-ticket.clean { border-left-color: var(--wing); }
.bw-ticket .bw-verdict { font-stretch: 115%; font-weight: 800; font-size: 1.6rem; line-height: 1.1; margin: 0 0 6px; color: var(--ink); }
.bw-ticket .bw-why { margin: 0 0 14px; line-height: 1.45; color: #3A4A58; }
.bw-counts { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; }
.bw-counts li { display: flex; align-items: center; gap: 8px; font-size: .95rem; margin: 0; }
.bw-counts .sw { width: 12px; height: 12px; border-radius: 2px; flex: none; }
.bw-counts .n { margin-left: auto; font-weight: 700; font-variant-numeric: tabular-nums; }
.bw-counts li.zero { color: #8C99A5; }
.bw-file { font-size: .85rem; color: #5D6B78; margin: 10px 0 0; }

h2, h3 { font-family: 'Archivo', sans-serif; font-stretch: 112%; }
[data-testid="stSidebar"] { background: #E0E7ED; }
[data-testid="stFileUploaderDropzone"] { background: #fff; border: 2px dashed var(--wing); }

@media (max-width: 760px) {
  .bw-hero { grid-template-columns: 1fr; padding: 22px 20px 38px; }
  .bw-rules { border-left: 0; padding-left: 0; border-top: 1px solid rgba(255,255,255,.18); padding-top: 18px; }
  .bw-counts { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="bw-hero">
  <div class="bw-title">
    <svg class="bw-gull" viewBox="0 0 64 22" aria-hidden="true"><path d="M3 15 C14 3, 24 3, 32 14 C40 3, 50 3, 61 15" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>
    <h1>BinWatch</h1>
    <p>Spots rubbish dumped beside The Hague's underground bins and bags torn open by gulls,
    so crews clear the worst bins before litter spreads into the dunes, beaches and canals.</p>
  </div>
  <div class="bw-rules">
    <h3>How bins are ranked</h3>
    <div class="bw-rule"><span class="bw-dot urgent"></span><span><b>Clear first.</b> Torn bag or loose litter: rubbish is already spreading.</span></div>
    <div class="bw-rule"><span class="bw-dot soon"></span><span><b>Clear on next round.</b> Closed bags or bulky items beside the bin.</span></div>
    <div class="bw-rule"><span class="bw-dot clean"></span><span><b>Clean.</b> Nothing beside the bin.</span></div>
  </div>
</div>
""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("Settings")
    min_conf = st.slider("Minimum confidence", 0.1, 0.9, 0.4, 0.05,
                         help="Hide detections the model is less sure about than this.")
    st.divider()
    st.caption(
        "**Limits:** trained on ~300 frames from a small number of bins in The Hague, "
        "autumn 2026. It finds *damage*, not *who* caused it: a bag torn by a rat, cat "
        "or person looks the same as one torn by a gull. Treat results as a hint for "
        "route planning, never as proof for fines."
    )

if not (API_KEY and (MODEL_ID or (WORKSPACE and WORKFLOW_ID))):
    st.error("Model not configured. Add ROBOFLOW_API_KEY plus either ROBOFLOW_WORKSPACE and "
             "ROBOFLOW_WORKFLOW_ID, or ROBOFLOW_MODEL_ID, to the app's secrets.")
    st.stop()

tab_upload, tab_camera = st.tabs(["Upload photos", "Take a photo"])
with tab_upload:
    uploads = st.file_uploader("Photos of underground bins", type=["jpg", "jpeg", "png", "webp"],
                               accept_multiple_files=True)
with tab_camera:
    snap = st.camera_input("Point the camera at the bin")

files = list(uploads or []) + ([snap] if snap else [])
if not files:
    st.info("Add one or more photos of bins. Several photos at once gives you a ranked clear-up list.")
    st.stop()

results = []
with st.spinner(f"Checking {len(files)} photo(s)…"):
    for f in files:
        img = prepare(f)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        try:
            preds = detect(buf.getvalue())
        except requests.RequestException as e:
            st.error(f"{f.name}: the model could not be reached ({e}). Check your internet connection and API key.")
            continue
        preds = [p for p in preds if p["confidence"] >= min_conf]
        counts = {}
        for p in preds:
            counts[p["class"]] = counts.get(p["class"], 0) + 1
        results.append({"name": f.name, "img": img, "preds": preds, "counts": counts,
                        "verdict": verdict(counts)})

if not results:
    st.stop()

# Ranked list – most urgent first
results.sort(key=lambda r: (-r["verdict"][0], -sum(r["counts"].values())))
if len(results) > 1:
    st.subheader("Clear-up order")
    st.dataframe(
        [{"Photo": r["name"], "Priority": r["verdict"][1],
          **{CLASS_STYLE[c][1]: r["counts"].get(c, 0) for c in CLASS_STYLE}} for r in results],
        hide_index=True, width="stretch",
    )

for r in results:
    level, label, reason, css = r["verdict"]
    st.write("")
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.image(draw(r["img"], r["preds"]), width="stretch")
    with right:
        rows = "".join(
            f'<li class="{"zero" if not r["counts"].get(c) else ""}"><span class="sw" style="background:{col}"></span>'
            f'{name}<span class="n">{r["counts"].get(c, 0)}</span></li>'
            for c, (col, name) in CLASS_STYLE.items()
        )
        st.markdown(
            f'<div class="bw-ticket {css}"><p class="bw-verdict">{label}</p>'
            f'<p class="bw-why">{reason}</p><ul class="bw-counts">{rows}</ul>'
            f'<p class="bw-file">{html.escape(r["name"])}</p></div>',
            unsafe_allow_html=True,
        )
        if not r["preds"]:
            st.caption("Nothing found above the confidence threshold. If you can see rubbish, "
                       "lower the slider in the sidebar.")
