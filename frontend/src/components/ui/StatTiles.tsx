// A row of numbers with captions.
import './StatTiles.css'

export interface Stat {
  label: string
  /** Already formatted. A dash is shown when it is missing. */
  value?: string
}

export default function StatTiles({ stats }: { stats: Stat[] }) {
  return (
    <div className="stats">
      {stats.map((stat) => (
        <div key={stat.label} className="stat">
          <b>{stat.value ?? '-'}</b>
          <span>{stat.label}</span>
        </div>
      ))}
    </div>
  )
}
