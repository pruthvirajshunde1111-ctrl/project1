import { useState, useEffect } from 'react'
import { fetchTraces, fetchTrace, fetchAnalytics, fetchEvalCases, fetchSampleDocuments, fetchFailureTypes } from './api'
import TracesTab from './components/TracesTab'
import TraceDetail from './components/TraceDetail'
import AnalyticsTab from './components/AnalyticsTab'
import PipelineRunner from './components/PipelineRunner'
import { ListIcon, SearchIcon, ChartIcon, PlayIcon } from './icons'

const TABS = [
  { key: 'traces', label: 'Traces' },
  { key: 'detail', label: 'Trace Detail' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'runner', label: 'Run Pipeline' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('traces')
  const [selectedTraceId, setSelectedTraceId] = useState(null)
  const [traces, setTraces] = useState([])
  const [traceDetail, setTraceDetail] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [evalCases, setEvalCases] = useState([])
  const [sampleDocs, setSampleDocs] = useState([])
  const [failureTypes, setFailureTypes] = useState({})
  const [loading, setLoading] = useState({})

  function loadTraces() {
    setLoading(p => ({ ...p, traces: true }))
    fetchTraces()
      .then(d => { setTraces(d.traces || []) })
      .catch(() => { setTraces([]) })
      .finally(() => setLoading(p => ({ ...p, traces: false })))
  }

  function loadTraceDetail(id) {
    if (!id) return
    setLoading(p => ({ ...p, detail: true }))
    fetchTrace(id)
      .then(d => setTraceDetail(d))
      .catch(() => setTraceDetail(null))
      .finally(() => setLoading(p => ({ ...p, detail: false })))
  }

  function loadAnalytics() {
    setLoading(p => ({ ...p, analytics: true }))
    Promise.all([fetchAnalytics(), fetchEvalCases()])
      .then(([a, e]) => { setAnalytics(a); setEvalCases(e.cases || []) })
      .catch(() => { setAnalytics(null); setEvalCases([]) })
      .finally(() => setLoading(p => ({ ...p, analytics: false })))
  }

  function loadSampleDocs() {
    fetchSampleDocuments()
      .then(d => setSampleDocs(d.documents || []))
      .catch(() => setSampleDocs([]))
    fetchFailureTypes()
      .then(d => setFailureTypes(d.types || {}))
      .catch(() => setFailureTypes({}))
  }

  useEffect(() => { loadTraces(); loadSampleDocs() }, [])

  function handleSelectTrace(id) {
    setSelectedTraceId(id)
    setActiveTab('detail')
  }

  function handleTraceUpdated() {
    if (selectedTraceId) loadTraceDetail(selectedTraceId)
    loadTraces()
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
            </svg>
          </div>
          <div>
            <h1>Failure Forensics</h1>
            <div className="subtitle">Observability layer for multi-step AI pipelines</div>
          </div>
        </div>
        <div className="header-badge">trace · diagnose · improve</div>
      </header>

      {/* Tabs */}
      <nav className="tabs">
        {TABS.map(t => (
          <button
            key={t.key}
            className={`tab-btn ${activeTab === t.key ? 'active' : ''}`}
            onClick={() => {
              setActiveTab(t.key)
              if (t.key === 'analytics') loadAnalytics()
              if (t.key === 'detail' && selectedTraceId) loadTraceDetail(selectedTraceId)
              if (t.key === 'traces') loadTraces()
            }}
          >
            <span style={{ display: 'inline-flex', marginRight: 6 }}>
              {t.label === 'Traces' && <ListIcon />}
              {t.label === 'Trace Detail' && <SearchIcon />}
              {t.label === 'Analytics' && <ChartIcon />}
              {t.label === 'Run Pipeline' && <PlayIcon />}
            </span>
            {t.label}
          </button>
        ))}
      </nav>

      {/* Content */}
      {activeTab === 'traces' && (
        <TracesTab
          traces={traces}
          loading={loading.traces}
          onSelectTrace={handleSelectTrace}
          onRefresh={loadTraces}
        />
      )}

      {activeTab === 'detail' && (
        <TraceDetail
          traceId={selectedTraceId}
          data={traceDetail}
          loading={loading.detail}
          onLoad={loadTraceDetail}
          onUpdated={handleTraceUpdated}
        />
      )}

      {activeTab === 'analytics' && (
        <AnalyticsTab
          data={analytics}
          evalCases={evalCases}
          loading={loading.analytics}
        />
      )}

      {activeTab === 'runner' && (
        <PipelineRunner
          sampleDocs={sampleDocs}
          failureTypes={failureTypes}
          onTraceComplete={(id) => {
            setSelectedTraceId(id)
            loadTraces()
          }}
        />
      )}
    </div>
  )
}
