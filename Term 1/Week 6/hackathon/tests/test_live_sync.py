"""Synthetic isolated bridge tests; never alter research output or contact GitHub."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sync_github_live import sync_once, SyncError, unpack_artifact

SOURCE = b'comment_id,video_id,text,published_at,collected_at\na,video,Synthetic test comment,2026-10-14T00:00:00Z,2026-10-14T01:00:00Z\n'
LATEST = SOURCE + b'b,video,New synthetic comment,2026-10-14T02:00:00Z,2026-10-14T03:00:00Z\n'


class Client:
    commit = 'b' * 40
    broken = False
    def __init__(self):
        files = {
            'sentiment_results.csv': 'comment_id,sentiment,confidence,model_version,analysed_at\na,Neutral,0.7,synthetic-test,2026-10-14T01:00:00Z\n',
            'processing_status.csv': 'comment_id,status,reason,language,quality_flags,text_hash,checked_at\na,analysed,,en,,,2026-10-14T01:00:00Z\n',
            'validation.json': json.dumps(dict(source_unchanged=True, counts=dict(failed=0), source_commit='a'*40, source_sha256=hashlib.sha256(SOURCE).hexdigest(), total_predictions=1, total_statuses=1))}
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as archive:
            for name, value in files.items(): archive.writestr(name,value)
        self.archive=stream.getvalue()
    def get(self, route, raw=False, optional=False):
        if route == '/commits/main': return {'sha': self.commit}
        if '/workflows/' in route: return {'workflow_runs':[dict(id=1,head_branch='main',head_repository={'full_name':'LuukAalders/Hackathons'})]}
        if route.endswith('/artifacts'): return {'artifacts':[dict(id=2,name='sentiment-checkpoints-1-1',expired=False,digest='sha256:'+hashlib.sha256(self.archive).hexdigest())]}
        if route.endswith('/zip'): return self.archive
        raise AssertionError(route)
    def source(self, commit, name, optional=False):
        if self.broken: raise SyncError('Synthetic source failure')
        return (SOURCE if commit == 'a'*40 else LATEST) if name == 'youtube_comments.csv' else None


class LiveSyncTests(unittest.TestCase):
    def test_new_comments_and_older_predictions_share_one_complete_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            result=sync_once(Client(),root,root/'absent-labels.csv')
            data=Path(result['data_directory'])
            self.assertEqual((data/'youtube_comments.csv').read_bytes(),LATEST)
            self.assertEqual(len((data/'sentiment_results.csv').read_text().splitlines()),2)
            self.assertEqual(json.loads((root/'current.json').read_text()),result)
            # An unchanged cycle reuses the complete generation.
            self.assertEqual(sync_once(Client(),root,root/'absent-labels.csv'),result)
    def test_interrupted_download_keeps_previous_generation_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); client=Client()
            sync_once(client,root,root/'absent-labels.csv')
            previous=(root/'current.json').read_bytes()
            client.commit='c'*40; client.broken=True
            with self.assertRaises(SyncError): sync_once(client,root,root/'absent-labels.csv')
            self.assertEqual((root/'current.json').read_bytes(),previous)
    def test_corrupted_artifact_is_rejected_before_publication(self):
        client=Client()
        with self.assertRaises(SyncError): unpack_artifact(client.archive,'sha256:'+'0'*64)


if __name__ == '__main__': unittest.main()
