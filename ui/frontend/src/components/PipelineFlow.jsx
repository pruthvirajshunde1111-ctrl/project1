import { InboxIcon, SearchIcon, TagIcon, SummaryIcon } from '../icons'

export default function PipelineFlow({ spans }) {
  const steps = [
    { name: 'Intake', key: 'intake', icon: InboxIcon },
    { name: 'Extraction', key: 'extraction', icon: SearchIcon },
    { name: 'Classification', key: 'classification', icon: TagIcon },
    { name: 'Summarization', key: 'summarization', icon: SummaryIcon },
  ]

  const nodeColors = { success: '#10B981', failure: '#EF4444', degraded: '#F59E0B' }
  const nodeBg = { success: 'rgba(16,185,129,0.12)', failure: 'rgba(239,68,68,0.12)', degraded: 'rgba(245,158,11,0.12)' }

  const nodes = []
  steps.forEach((sd, i) => {
    const span = spans.find(s => s.step_name === sd.key)
    const color = span ? nodeColors[span.status] || '#64748B' : '#334155'
    const bg = span ? nodeBg[span.status] || 'rgba(100,116,139,0.08)' : 'rgba(51,65,85,0.08)'
    const conf = span ? span.confidence : 0
    const statusTxt = span ? span.status : 'skipped'
    const SvgIcon = sd.icon

    nodes.push(
      <div key={sd.key} className="pipeline-node" style={{ background: bg, border: `1px solid ${color}40`, animationDelay: `${i * 0.12}s` }}>
        <div className="node-icon" style={{ color }}><SvgIcon size={22} /></div>
        <div className="node-label">{sd.name}</div>
        <div className="node-confidence" style={{ color }}>
          {conf === 0 && !span ? '\u2014' : `${(conf * 100).toFixed(0)}%`}
        </div>
        <div className="node-status" style={{ color }}>{statusTxt}</div>
      </div>
    )
    if (i < steps.length - 1) {
      nodes.push(<div key={`a-${sd.key}`} className="pipeline-arrow">▸</div>)
    }
  })

  return <div className="pipeline-flow">{nodes}</div>
}
