// A labelled form control with an optional hint underneath.
import type { ReactNode } from 'react'
import './form.css'

interface Props {
  label: ReactNode
  hint?: ReactNode
  children: ReactNode
}

export default function Field({ label, hint, children }: Props) {
  return (
    <div className="field">
      <label>
        {label}
        {children}
      </label>
      {hint && <span className="hint">{hint}</span>}
    </div>
  )
}
