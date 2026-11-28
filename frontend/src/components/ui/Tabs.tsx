import './Tabs.css'

interface Props<Id extends string> {
  tabs: readonly { id: Id; label: string }[]
  active: Id
  onSelect: (id: Id) => void
}

export default function Tabs<Id extends string>({ tabs, active, onSelect }: Props<Id>) {
  return (
    <nav className="tabs" aria-label="Result views">
      {tabs.map((tab) => (
        <button key={tab.id} type="button" className="tab"
          aria-current={tab.id === active ? 'page' : undefined}
          onClick={() => onSelect(tab.id)}>
          {tab.label}
        </button>
      ))}
    </nav>
  )
}
