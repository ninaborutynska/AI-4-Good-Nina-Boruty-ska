"use client";
import Link from "next/link";
import { formatDate, useData } from "./useData";
type Metrics = { accuracy: number; count: number; labels: string[]; confusion_matrix: number[][] };
type Report = {
  status: string; message: string; manual_count: number; evaluated_count?: number; documented_failures?: number;
  evaluated_at?: string; baseline_name?: string; transformer?: Metrics; baseline?: Metrics;
  total_labelled_count?: number; excluded_irrelevant_count?: number;
  failures?: { comment_id: string; text: string; actual: string; predicted: string; explanation: string }[];
};
function Matrix({ title, metrics }: { title: string; metrics: Metrics }) {
  return <section className="panel"><h2>{title}</h2><p className="metric">{(metrics.accuracy * 100).toFixed(1)}% <small>accuracy on {metrics.count} manual labels</small></p>
    <p className="muted">Rows: human label · Columns: model prediction</p><div className="table-scroll"><table><thead><tr><th>Actual / Predicted</th>{metrics.labels.map(label => <th key={label}>{label}</th>)}</tr></thead>
      <tbody>{metrics.confusion_matrix.map((row, i) => <tr key={metrics.labels[i]}><th>{metrics.labels[i]}</th>{row.map((number, j) => <td key={j}>{number}</td>)}</tr>)}</tbody></table></div></section>;
}
export default function Evaluation() {
  const state = useData();
  const report = state?.snapshot?.evaluation as Report | undefined;
  return <main><header><div><p className="eyebrow">AUTONOMOUS DRIVING · SDG 9</p><h1>Model evaluation</h1><p className="subtitle">Compare transformer predictions with independently labelled real comments.</p></div><Link className="button" href="/">← Sentiment monitor</Link></header>
    {state?.error && <div className="alert" role="alert">{state.error}{state.stale && " Previously loaded data is shown and may be outdated."}</div>}
    {!state ? <div className="empty">Loading evaluation data…</div> : !report ? <div className="empty">Evaluation is unavailable until the real dataset can be loaded.</div> : <>
      <section className="panel"><h2>Evidence requirements</h2><p>{report.message}</p><div className="metrics-row"><p><strong>{report.total_labelled_count ?? report.manual_count}</strong> comments annotated</p><p><strong>{report.evaluated_count ?? 0}</strong> matched sentiment predictions</p><p><strong>{report.excluded_irrelevant_count ?? 0}</strong> not relevant comments excluded</p><p><strong>{report.documented_failures ?? 0}</strong> documented failures</p></div><p className="muted">Status: {report.status.replaceAll("_", " ")} · Last evaluation: {formatDate(report.evaluated_at)}</p></section>
      {report.transformer && report.baseline && <div className="chart-grid"><Matrix title="CardiffNLP RoBERTa" metrics={report.transformer} /><Matrix title={report.baseline_name || "VADER baseline"} metrics={report.baseline} /></div>}
      {!!report.failures?.length && <section className="panel"><h2>Observed classification failures</h2><div className="table-scroll"><table><thead><tr><th>Real comment</th><th>Human label</th><th>Model label</th><th>Human explanation</th></tr></thead><tbody>{report.failures.map(row => <tr key={row.comment_id}><td>{row.text}</td><td>{row.actual}</td><td>{row.predicted}</td><td>{row.explanation || "An annotator has not documented this failure yet."}</td></tr>)}</tbody></table></div></section>}
    </>}
    <section className="panel"><h2>Annotation protocol</h2><ol><li>Use the blind real-comment sample. Only the manual sentiment label needs to be filled in; keep comment text and ID unchanged.</li><li>Label the attitude toward autonomous driving as Positive, Neutral, or Negative before viewing model predictions. A relevant factual statement or question can be Neutral. Use Not relevant when the comment is off-topic; those comments are excluded from the sentiment comparison.</li><li>Complete at least 50 relevant comments. Names, timestamps, and notes are optional.</li><li>Run the evaluation script. After comparison, document at least three observed classification failures with a human explanation.</li></ol><p className="muted">The models classify general text sentiment, which can differ from attitudes toward autonomous driving. Small samples have substantial uncertainty. A random sample estimates performance on collected comments, not all public opinion. Model confidence is a probability assigned by the model; it is not verified accuracy. VADER scores are lexicon scores, not confidence probabilities.</p></section>
  </main>;
}
