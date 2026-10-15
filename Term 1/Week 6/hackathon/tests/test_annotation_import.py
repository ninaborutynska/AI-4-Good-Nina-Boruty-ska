import json
import tempfile
import unittest
from pathlib import Path
from import_manual_labels import import_labels
from document_failures import document
from sentiment.core import atomic_csv, read_rows, RESULT_COLUMNS

class AnnotationImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.comments=self.root/'comments.csv'
        self.output=self.root/'labels.csv'
        self.extracted=self.root/'extracted.json'
        self.record=dict(comment_id='synthetic-test',text='Synthetic fixture, not a research annotation.',manual_sentiment='Positive')
        atomic_csv(self.comments,['comment_id','text'],[self.record])
        self.extracted.write_text(json.dumps({'source':'synthetic-test.xlsx','rows':[self.record]}),encoding='utf-8')
    def tearDown(self): self.temp.cleanup()
    def test_import_and_preserve_existing_explanation(self):
        first={**self.record,'notes':'Synthetic explanation used only in an offline test.'}
        atomic_csv(self.output,['comment_id','text','manual_sentiment','notes'],[first])
        import_labels(self.extracted,self.comments,self.output)
        self.assertEqual(read_rows(self.output,['comment_id','manual_sentiment'])['synthetic-test']['notes'],first['notes'])
        self.assertEqual(len(list((self.root/'annotation_history').glob('*.csv'))),1)
    def test_changed_text_rejected_without_overwriting(self):
        atomic_csv(self.output,['comment_id','text','manual_sentiment'],[self.record])
        before=self.output.read_bytes()
        self.extracted.write_text(json.dumps({'source':'synthetic-test.xlsx','rows':[{**self.record,'text':'Changed fixture'}]}),encoding='utf-8')
        with self.assertRaises(ValueError): import_labels(self.extracted,self.comments,self.output)
        self.assertEqual(self.output.read_bytes(),before)
    def test_conflicting_completion_rejected(self):
        with self.assertRaises(ValueError): import_labels(self.extracted,self.comments,self.output,{'synthetic-test':'Negative'})
        self.assertFalse(self.output.exists())
    def test_explanation_requires_real_label_disagreement(self):
        atomic_csv(self.output,['comment_id','text','manual_sentiment'],[self.record])
        predictions=self.root/'predictions.csv'
        atomic_csv(predictions,RESULT_COLUMNS,[dict(comment_id='synthetic-test',sentiment='Positive',confidence='0.9',model_version='test-double',analysed_at='2026-10-14T00:00:00Z')])
        explanations=self.root/'explanations.json'
        explanations.write_text(json.dumps({'explanations':{'synthetic-test':{'explanation':'Test explanation'}}}),encoding='utf-8')
        before=self.output.read_bytes()
        with self.assertRaises(ValueError): document(self.output,predictions,explanations)
        self.assertEqual(self.output.read_bytes(),before)

if __name__=='__main__': unittest.main()
