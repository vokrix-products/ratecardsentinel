import {CircleCheckBig, Clock, TriangleAlert} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

// Severity tiers drive badge color. Every status maps to exactly one tier:
//   critical -> red (destructive)   e.g. expired, denied, failed
//   warning  -> amber (warning)     e.g. expiring soon, needs review
//   good     -> green (success)     e.g. valid, approved, done
//   neutral  -> gray (secondary)    e.g. pending, queued, n/a
export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// PRODUCT_CUSTOMIZE: replace this list with the real statuses this product
// produces (must match exactly what the backend poller writes to
// records.status). Every status must declare a severity tier above. Default
// values below are generic placeholders only — do not ship as-is.
// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Valid', value: 'valid:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Missing', value: 'missing:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Expired', value: 'expired:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Flagged', value: 'flagged:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Pending Review', value: 'pending_review:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Dispute Ready', value: 'dispute_ready:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Disputed', value: 'disputed:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Recovered', value: 'recovered:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Unresolved', value: 'unresolved:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Recurring', value: 'recurring:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Margin Leakage', value: 'margin_leakage:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Underbilled', value: 'underbilled:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Duplicate Invoice', value: 'duplicate_invoice:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'No Contract', value: 'no_contract:warning', icon: Clock, severity: 'warning' as Severity },
  { label: 'Tolerance Review', value: 'tolerance_review:neutral', icon: Clock, severity: 'neutral' as Severity },
  { label: 'Approved', value: 'approved:good', icon: CircleCheckBig, severity: 'good' as Severity },
]
// __STATUSES_BLOCK_END__
