import type { ReactNode } from 'react'
import './Collapsible.css'

interface Props {
  title: string
  note?: string
  children: ReactNode
}

/** A box the user can open and close. It starts open. */
export default function Collapsible({ title, note, children }: Props) {
  return (
    <details className="collapsible" open>
      <summary>
        {title}
        {note && <span>{note}</span>}
      </summary>
      <div className="collapsible-inner">{children}</div>
    </details>
  )
}
