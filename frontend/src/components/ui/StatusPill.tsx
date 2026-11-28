import type { Verdict } from '../../api/types'
import './StatusPill.css'

export default function StatusPill({ verdict }: { verdict: Verdict | null }) {
  return <div className={`pill pill-${verdict ?? 'idle'}`}>{verdict ?? 'READY'}</div>
}
