import { useState } from 'react'
import { runPipeline, batchRunPipeline } from '../api'
import { PlayIcon, FileIcon, EditIcon, DocIcon, XIcon, CheckIcon } from '../icons'

export default function PipelineRunner({ sampleDocs, failureTypes, onTraceComplete }) {
  const [textSource, setTextSource] = useState('sample')
  const [selectedDoc, setSelectedDoc] = useState(sampleDocs[0]?.source || '')
  const [customText, setCustomText] = useState('')
  const [customSource, setCustomSource] = useState('user-provided')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const [batchRunning, setBatchRunning] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const [batchResults, setBatchResults] = useState([])

  const doc = sampleDocs.find(d => d.source === selectedDoc)
  const activeText = textSource === 'sample' ? (doc?.text || '') : customText

  async function handleRun() {
    if (!activeText.trim()) return
    setRunning(true)
    setResult(null)
    setError(null)
    try {
      const res = await runPipeline(activeText, textSource === 'sample' ? selectedDoc : customSource)
      setResult(res)
      onTraceComplete(res.trace_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  async function handleBatch() {
    setBatchRunning(true)
    setBatchProgress(0)
    setBatchResults([])
    try {
      const res = await batchRunPipeline(sampleDocs.map(d => ({ id: d.id, source: d.source, text: d.text })))
      setBatchResults(res.results || [])
      setBatchProgress(1)
    } catch (e) {
      setError(`Batch failed: ${e.message}`)
    } finally {
      setBatchRunning(false)
    }
  }

  return (
    <div>
      <p className="section-subtitle">Select a sample document or paste your own to execute the 4-step pipeline.</p>

      <div className="radio-group">
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <input type="radio" name="source" checked={textSource === 'sample'} onChange={() => setTextSource('sample')} />
          <DocIcon size={14} /> Sample document
        </label>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <input type="radio" name="source" checked={textSource === 'custom'} onChange={() => setTextSource('custom')} />
          <EditIcon size={14} /> Paste your own
        </label>
      </div>

      {textSource === 'sample' ? (
        <div style={{ marginBottom: 16 }}>
          <select className="select" value={selectedDoc} onChange={e => setSelectedDoc(e.target.value)}>
            {sampleDocs.map(d => (
              <option key={d.id || d.source} value={d.source}>{d.source} &middot; {d.id}</option>
            ))}
          </select>
          {doc && (
            <div className="preview-block">
              {doc.text?.length > 800 ? doc.text.slice(0, 800) + '...' : doc.text}
            </div>
          )}
        </div>
      ) : (
        <div style={{ marginBottom: 16 }}>
          <input className="input" placeholder="Source label" value={customSource}
            onChange={e => setCustomSource(e.target.value)} style={{ marginBottom: 8 }} />
          <textarea className="input textarea" placeholder="Paste your document text here..."
            value={customText} onChange={e => setCustomText(e.target.value)} />
        </div>
      )}

      {!activeText.trim() && (
        <div className="empty-state" style={{ padding: 30 }}>
          <div className="text">Select or paste a document to begin.</div>
        </div>
      )}

      {activeText.trim() && (
        <>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 16 }}>
            <button className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }} onClick={handleRun} disabled={running}>
              {running ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Running...</> : <><PlayIcon size={16} /> Run Pipeline</>}
            </button>
            <span style={{ color: '#475569', fontSize: 12 }}>Executes Intake \u2192 Extraction \u2192 Classification \u2192 Summarization</span>
          </div>

          {error && <div className="error-banner" style={{ display: 'flex', alignItems: 'center', gap: 6 }}><XIcon size={14} /> {error}</div>}

          {result && (
            <>
              <div className="success-banner" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <CheckIcon size={16} /> Pipeline completed &mdash; <strong>{result.status?.toUpperCase()}</strong> &middot; Score: <strong>{(result.final_score * 100).toFixed(0)}%</strong>
              </div>

              {(result.spans || []).filter(s => s.step_name !== 'intake').length > 0 && (
                <div className="metrics-row">
                  {result.spans.filter(s => s.step_name !== 'intake').map(s => {
                    const color = s.confidence >= 0.7 ? '#34D399' : s.confidence >= 0.4 ? '#FBBF24' : '#F87171'
                    return (
                      <div key={s.step_name} className="metric-card">
                        <div className="metric-label">{s.step_name}</div>
                        <div className="metric-value" style={{ color }}>{(s.confidence * 100).toFixed(0)}%</div>
                      </div>
                    )
                  })}
                </div>
              )}

              <details className="expander">
                <summary>View Full Trace Data</summary>
                <div className="expander-content">
                  <div className="json-block" style={{ maxHeight: 400 }}>
                    {JSON.stringify({ ...result, spans: undefined }, null, 2)}
                  </div>
                </div>
              </details>
            </>
          )}
        </>
      )}

      <hr className="divider" />

      <div className="section-title">Batch Processing</div>
      <p style={{ color: '#64748B', fontSize: 13, marginBottom: 16 }}>
        Process all {sampleDocs.length} sample documents to generate evaluation data.
      </p>

      <button className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }} onClick={handleBatch} disabled={batchRunning}>
        {batchRunning ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Processing...</> : <><PlayIcon size={16} /> Process All Documents</>}
      </button>

      {batchRunning && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${batchProgress * 100}%` }} />
        </div>
      )}

      {batchResults.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <table className="batch-table">
            <thead>
              <tr><th>ID</th><th>Source</th><th>Status</th><th>Score</th></tr>
            </thead>
            <tbody>
              {batchResults.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.source}</td>
                  <td><span className={`badge badge-${r.status}`}>{r.status}</span></td>
                  <td>{r.final_score != null ? `${(r.final_score * 100).toFixed(0)}%` : '\u2014'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
