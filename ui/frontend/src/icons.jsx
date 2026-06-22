const strokeProps = { fill: 'none', stroke: 'currentColor', strokeWidth: '2', strokeLinecap: 'round', strokeLinejoin: 'round' }

export function ListIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
}

export function SearchIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
}

export function ChartIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
}

export function PlayIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><polygon points="5 3 19 12 5 21 5 3"/></svg>
}

export function InboxIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>
}

export function EyeIcon({ size = 18 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
}

export function RefreshIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
}

export function FlagIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>
}

export function CheckIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><polyline points="20 6 9 17 4 12"/></svg>
}

export function XIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
}

export function FileIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
}

export function EditIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
}

export function LinkIcon({ size = 20 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
}

export function DocIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
}

export function TextIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>
}

export function TagIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
}

export function SummaryIcon({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" {...strokeProps}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><line x1="9" y1="10" x2="15" y2="10"/><line x1="12" y1="7" x2="12" y2="13"/></svg>
}

export function DotSuccess({ size = 10 }) {
  return <svg width={size} height={size} viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#10B981"/></svg>
}

export function DotFailure({ size = 10 }) {
  return <svg width={size} height={size} viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#EF4444"/></svg>
}

export function DotDegraded({ size = 10 }) {
  return <svg width={size} height={size} viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#F59E0B"/></svg>
}

export function DotNeutral({ size = 10 }) {
  return <svg width={size} height={size} viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="#64748B"/></svg>
}
