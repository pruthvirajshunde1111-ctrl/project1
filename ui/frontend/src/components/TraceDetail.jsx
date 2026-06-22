import { useEffect } from 'react'
import PipelineFlow from './PipelineFlow'
import { flagTrace, overrideDiagnosis } from '../api'
import { SearchIcon, FlagIcon, DotSuccess, DotFailure, DotDegraded, DotNeutral, CheckIcon } from '../icons'

export default function TraceDetail({ traceId, data, loading, onLoad, onUpdated }) {
  useEffect(() => {
    if (traceId) onLoad(traceId)
  }, [traceId])

  if (!traceId) {
    return (
      <div className="empty-state">
        <div className="icon" style={{ opacity: 0.4 }}><SearchIcon size={48} /></div>
        <div className="text">Select a trace from the Traces tab to view details.</div>
      </div>
    )
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" /></div>
  if (!data) return <div className="error-banner">Trace not found.</div>

  const scoreColor = data.final_score >= 0.7 ? '#34D399' : data.final_score >= 0.4 ? '#FBBF24' : '#F87171'
  const statusClass = data.status || 'degraded'

  const statusDot = { success: DotSuccess, failure: DotFailure, degraded: DotDegraded }[statusClass] || DotNeutral
  const StatusDot = statusDot

  return (
    <div>
      <div className="status-bar">
        <div className="status-bar-left">
          <StatusDot size={12} />
          <div>
            <div className="status-label">{data.status?.toUpperCase()}</div>
            <div className="status-meta">{data.trace_id} &middot; {data.source} &middot; {data.timestamp}</div>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="status-score" style={{ color: scoreColor }}>{(data.final_score * 100).toFixed(0)}%</div>
          <div className="metric-label">Score</div>
        </div>
      </div>

      {data.flagged && (
        <div className="alert-flag"><FlagIcon size={14} style={{ marginRight: 4 }} /> Flagged: <span>{data.flag_notes}</span></div>
      )}

      <div className="section-title">Pipeline Flow</div>
      <PipelineFlow spans={data.spans || []} />

      <div className="section-title">Span Details</div>
      {(data.spans || []).map(span => {
        const StatusIcon = { success: CheckIcon, failure: DotFailure, degraded: DotDegraded }[span.status] || DotNeutral
        const statusColor = { success: '#10B981', failure: '#EF4444', degraded: '#F59E0B' }[span.status] || '#64748B'
        const sc = span.confidence >= 0.7 ? '#34D399' : span.confidence >= 0.4 ? '#FBBF24' : '#F87171'
        return (
          <details key={span.span_id} className="expander">
            <summary>
              <StatusIcon size={14} style={{ color: statusColor }} />
              {' '}{span.step_name} &middot; conf: <span style={{ color: sc }}>{(span.confidence * 100).toFixed(0)}%</span> &middot; {span.token_count} tok &middot; {span.latency_ms.toFixed(0)}ms
            </summary>
            <div className="expander-content">
              <div className="data-grid">
                <div>
                  <div className="data-label">Input</div>
                  <div className="json-block">{JSON.stringify(span.input_data, null, 2)}</div>
                </div>
                <div>
                  <div className="data-label">Output</div>
                  <div className="json-block">{JSON.stringify(span.output_data, null, 2)}</div>
                </div>
              </div>
              {span.prompt && (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ color: '#64748B', cursor: 'pointer', fontSize: 13 }}>View Prompt</summary>
                  <div className="json-block" style={{ marginTop: 4, maxHeight: 300 }}>{span.prompt}</div>
                </details>
              )}
              {span.raw_response && (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ color: '#64748B', cursor: 'pointer', fontSize: 13 }}>View Raw Response</summary>
                  <div className="json-block" style={{ marginTop: 4, maxHeight: 300 }}>{span.raw_response}</div>
                </details>
              )}
              {span.error && <div className="error-banner" style={{ marginTop: 8 }}>Error: {span.error}</div>}
            </div>
          </details>
        )
      })}

      {data.diagnosis && <DiagnosisSection diagnosis={data.diagnosis} />}

      <hr className="divider" />

      <FlagSection traceId={data.trace_id} onFlagged={onUpdated} />

      {data.diagnosis && <OverrideSection traceId={data.trace_id} diagnosis={data.diagnosis} onOverridden={onUpdated} />}
    </div>
  )
}

function DiagnosisSection({ diagnosis }) {
  const dc = diagnosis.confidence || 0
  const dcColor = dc >= 0.7 ? '#34D399' : dc >= 0.4 ? '#FBBF24' : '#F87171'

  return (
    <>
      <div className="section-title">Root Cause Diagnosis</div>
      <div className="metrics-row" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="metric-card">
          <div className="metric-value" style={{ fontSize: 18 }}>{diagnosis.root_cause_step || 'N/A'}</div>
          <div className="metric-label">Root Cause Step</div>
        </div>
        <div className="metric-card">
          <div className="metric-value" style={{ fontSize: 18 }}>{diagnosis.failure_category || 'N/A'}</div>
          <div className="metric-label">Failure Category</div>
        </div>
        <div className="metric-card">
          <div className="metric-value" style={{ fontSize: 18, color: dcColor }}>{(dc * 100).toFixed(0)}%</div>
          <div className="metric-label">Confidence</div>
        </div>
      </div>

      <div className="info-box explanation">{diagnosis.explanation || 'N/A'}</div>
      {diagnosis.suggestion && (
        <div className="info-box suggestion"><strong>Suggestion:</strong> {diagnosis.suggestion}</div>
      )}

      {diagnosis.evidence_chain?.length > 0 && (
        <>
          <div className="section-title" style={{ marginTop: 16, fontSize: 13 }}>Evidence Chain</div>
          {diagnosis.evidence_chain.map((entry, i) => {
            const score = entry.score
            let DotIcon = DotNeutral, scColor = '#64748B'
            if (typeof score === 'number') {
              DotIcon = score >= 4 ? DotSuccess : score >= 2 ? DotDegraded : DotFailure
              scColor = score >= 4 ? '#34D399' : score >= 2 ? '#FBBF24' : '#F87171'
            }
            return (
              <div key={i}>
                <div className="evidence-item">
                  <DotIcon size={10} />
                  <span className="evidence-step">{entry.step}</span>
                  <span className="evidence-score" style={{ color: scColor }}>score: {score}</span>
                </div>
                {(entry.issues || []).slice(0, 3).map((issue, j) => (
                  <div key={j} className="evidence-issues">\u2014 {issue}</div>
                ))}
              </div>
            )
          })}
        </>
      )}
    </>
  )
}

function FlagSection({ traceId, onFlagged }) {
  let notes = ''
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
      <input className="input" placeholder="Why is this output bad?" style={{ flex: 1 }}
        onChange={e => { notes = e.target.value }} />
      <button className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }} onClick={async () => {
        await flagTrace(traceId, notes)
        onFlagged()
      }}>
        <FlagIcon size={14} /> Flag as Bad Output
      </button>
    </div>
  )
}

function OverrideSection({ traceId, diagnosis, onOverridden }) {
  return (
    <details className="override-section">
      <summary>Override Diagnosis</summary>
      <div style={{ marginTop: 12 }}>
        <div className="form-row">
          <input className="input" defaultValue={diagnosis.root_cause_step || ''} placeholder="Root cause step" id="override-step" />
          <input className="input" defaultValue={diagnosis.failure_category || ''} placeholder="Failure category" id="override-cat" />
        </div>
        <textarea className="input textarea" defaultValue={diagnosis.explanation || ''} placeholder="Explanation" id="override-exp" />
        <button className="btn btn-secondary" style={{ marginTop: 8 }} onClick={async () => {
          const step = document.getElementById('override-step').value
          const cat = document.getElementById('override-cat').value
          const exp = document.getElementById('override-exp').value
          await overrideDiagnosis(traceId, { root_cause_step: step, failure_category: cat, explanation: exp })
          onOverridden()
        }}>Save Override</button>
      </div>
    </details>
  )
}
