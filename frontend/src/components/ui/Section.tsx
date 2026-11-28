// A titled block inside a tab. Move these around to rearrange a tab.
import type { ReactNode } from 'react'
import './Section.css'

export default function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="section">
      <h3>{title}</h3>
      {children}
    </section>
  )
}
