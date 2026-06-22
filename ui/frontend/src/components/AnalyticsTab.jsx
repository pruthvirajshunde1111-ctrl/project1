import { ChartIcon, DotSuccess, DotFailure, DotDegraded, DotNeutral, CheckIcon } from '../icons'

export default function AnalyticsTab({ data, evalCases, loading }) {
  if (loading) return <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" /></div>

  if (!data || data.total_traces === 0) {
    return (
      <div className="empty-state">
        <div className="icon" style={{ opacity: 0.4 }}><ChartIcon size={48} /></div>
        <div className="text">No data yet.</div>
        <div className="sub">Run the pipeline to populate analytics.</div>
      </div>
    )
  }

  return (
    <div>
      <p className="section-subtitle">Failure analytics and evaluation dataset overview.</p>

      <div className="metrics-row" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="metric-card">
          <div className="metric-label">Total Traces</div>
          <div className="metric-value">{data.total_traces}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Failure Rate</div>
          <div className="metric-value" style={data.failure_rate > 50 ? { color: '#F87171' } : { color: '#34D399' }}>
            {data.failure_rate}%
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Avg Score</div>
          <div className="metric-value">{(data.avg_final_score * 100).toFixed(0)}%</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Eval Cases</div>
          <div className="metric-value">{data.eval_cases || 0}</div>
        </div>
      </div>

      {data.eval_cases > 0 && (
        <div className="metrics-row" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <div className="metric-card">
            <div className="metric-label">Resolved</div>
            <div className="metric-value">{data.resolved_cases || 0}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Resolution Rate</div>
            <div className="metric-value">{data.resolution_rate || 0}%</div>
          </div>
        </div>
      )}

      {data.failure_types && Object.keys(data.failure_types).length > 0 && (
        <>
          <div className="section-title">Failure Types</div>
          <div className="metrics-row">
            {Object.entries(data.failure_types).map(([ft, info]) => (
              <div key={ft} className="metric-card">
                <div className="metric-label">{ft}</div>
                <div className="metric-value">{info.count}</div>
                <div className="metric-sub">{info.pct}%</div>
              </div>
            ))}
          </div>
        </>
      )}

      {data.failing_steps && Object.keys(data.failing_steps).length > 0 && (
        <>
          <div className="section-title">Failing Steps</div>
          <div className="metrics-row">
            {Object.entries(data.failing_steps).map(([step, count]) => (
              <div key={step} className="metric-card">
                <div className="metric-label">{step}</div>
                <div className="metric-value">{count}</div>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="section-title">Status Distribution</div>
      <div className="metrics-row">
        {data.by_status && Object.entries(data.by_status).map(([status, count]) => {
          const DotIcon = { success: DotSuccess, failure: DotFailure, degraded: DotDegraded }[status] || DotNeutral
          return (
            <div key={status} className="metric-card" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <DotIcon size={14} />
              <div>
                <div className="metric-label">{status}</div>
                <div className="metric-value" style={{ fontSize: 22 }}>{count}</div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="section-title">Recent Eval Cases</div>
      {evalCases.length > 0 ? (
        [...evalCases].reverse().slice(-5).map((c, i) => (
          <div key={i} className="eval-case">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontWeight: 600, color: '#E2E8F0' }}>{c.failing_step || 'N/A'}</span>
                <span style={{ color: '#64748B', fontSize: 13, marginLeft: 10 }}>{c.failure_category || 'unknown'}</span>
              </div>
              <div>
                {c.still_failing ? (
                  <span style={{ color: '#F87171', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                    <DotFailure size={10} /> Failing
                  </span>
                ) : (
                  <span style={{ color: '#34D399', fontWeight: 600, fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                    <CheckIcon size={12} /> Resolved
                  </span>
                )}
                <span style={{ color: '#475569', fontSize: 12, marginLeft: 12 }}>{(c.timestamp || '').slice(0, 10)}</span>
              </div>
            </div>
          </div>
        ))
      ) : (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <p style={{ color: '#475569', fontSize: 14 }}>No eval cases yet. Flag traces to generate eval cases.</p>
        </div>
      )}
    </div>
  )
}
