import { useState } from 'react'
import { EyeIcon, RefreshIcon, FlagIcon, DocIcon } from '../icons'

export default function TracesTab({ traces, loading, onSelectTrace, onRefresh }) {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [flaggedFilter, setFlaggedFilter] = useState('All')
  const [minScore, setMinScore] = useState(0)

  let filtered = traces
  if (search) filtered = filtered.filter(t => (t.source || '').toLowerCase().includes(search.toLowerCase()))
  if (statusFilter !== 'All') filtered = filtered.filter(t => t.status === statusFilter)
  if (flaggedFilter === 'Flagged') filtered = filtered.filter(t => t.flagged)
  if (flaggedFilter === 'Unflagged') filtered = filtered.filter(t => !t.flagged)
  filtered = filtered.filter(t => (t.final_score || 0) >= minScore)

  return (
    <div>
      <p className="section-subtitle">Browse all pipeline executions. Select a trace to inspect details.</p>

      <div className="filters">
        <input className="input" placeholder="Search by source..." value={search} onChange={e => setSearch(e.target.value)} />
        <select className="select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option>All</option>
          <option>success</option>
          <option>failure</option>
          <option>degraded</option>
        </select>
        <select className="select" value={flaggedFilter} onChange={e => setFlaggedFilter(e.target.value)}>
          <option>All</option>
          <option>Flagged</option>
          <option>Unflagged</option>
        </select>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input className="input" type="range" min="0" max="1" step="0.1"
            value={minScore} onChange={e => setMinScore(parseFloat(e.target.value))} />
          <span style={{ color: '#64748B', fontSize: 13, minWidth: 35 }}>{minScore.toFixed(1)}</span>
        </div>
      </div>

      {loading && <div style={{ textAlign: 'center', padding: 40 }}><div className="spinner" /></div>}

      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          <div className="icon" style={{ opacity: 0.4 }}><DocIcon size={48} /></div>
          <div className="text">{traces.length === 0 ? 'No traces yet.' : 'No traces match your filters.'}</div>
          <div className="sub">Run the pipeline in the <strong>Run Pipeline</strong> tab to get started.</div>
        </div>
      )}

      {filtered.map(t => {
        const scoreColor = t.final_score >= 0.7 ? '#34D399' : t.final_score >= 0.4 ? '#FBBF24' : '#F87171'
        return (
          <div key={t.trace_id} className="card" style={{ cursor: 'pointer' }}>
            <div className="card-header">
              <div>
                <span className="card-source">{t.source || 'unknown'}</span>
                {t.flagged && (
                  <span className="card-flagged">
                    <FlagIcon size={12} style={{ marginRight: 2 }} /> Flagged
                  </span>
                )}
                <div className="card-trace-id">{t.trace_id?.slice(0, 12)}... &middot; {(t.timestamp || '').slice(0, 10)}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className={`badge badge-${t.status}`}>{t.status}</span>
                <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4, color: scoreColor }}>
                  {(t.final_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
              <button className="btn btn-secondary" style={{ fontSize: 13, padding: '6px 16px', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                onClick={() => onSelectTrace(t.trace_id)}>
                <EyeIcon size={14} /> Inspect
              </button>
              <button className="btn btn-secondary" style={{ fontSize: 13, padding: '6px 16px', display: 'inline-flex', alignItems: 'center', gap: 4 }}
                onClick={onRefresh}>
                <RefreshIcon size={14} /> Refresh
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
