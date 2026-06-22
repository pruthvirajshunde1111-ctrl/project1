const API_BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API ${res.status}: ${body}`)
  }
  return res.json()
}

export function fetchTraces(limit = 200) {
  return request(`/traces?limit=${limit}`)
}

export function fetchTrace(id) {
  return request(`/traces/${id}`)
}

export function flagTrace(traceId, notes = '') {
  return request(`/traces/${traceId}/flag`, {
    method: 'POST',
    body: JSON.stringify({ trace_id: traceId, notes }),
  })
}

export function overrideDiagnosis(traceId, data) {
  return request(`/traces/${traceId}/override-diagnosis`, {
    method: 'POST',
    body: JSON.stringify({ trace_id: traceId, ...data }),
  })
}

export function fetchAnalytics() {
  return request('/analytics')
}

export function fetchEvalCases(limit = 100) {
  return request(`/eval-cases?limit=${limit}`)
}

export function fetchSampleDocuments() {
  return request('/sample-documents')
}

export function runPipeline(text, source = '') {
  return request('/pipeline/run', {
    method: 'POST',
    body: JSON.stringify({ text, source }),
  })
}

export function batchRunPipeline(documents) {
  return request('/pipeline/batch-run', {
    method: 'POST',
    body: JSON.stringify({ documents }),
  })
}

export function fetchFailureTypes() {
  return request('/failure-types')
}
