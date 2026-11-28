import './Legend.css'

export interface LegendItem {
  label: string
  /** A CSS colour, normally a token such as var(--ideal). */
  color: string
}

export default function Legend({ items }: { items: LegendItem[] }) {
  return (
    <div className="legend">
      {items.map((item) => (
        <span key={item.label}><i style={{ background: item.color }} />{item.label}</span>
      ))}
    </div>
  )
}
