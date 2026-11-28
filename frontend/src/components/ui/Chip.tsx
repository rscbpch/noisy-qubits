// A button that is either selected or not.
import './Chip.css'

interface Props {
  label: string
  selected: boolean
  title?: string
  onClick: () => void
}

export default function Chip({ label, selected, title, onClick }: Props) {
  return (
    <button type="button" className="chip" aria-pressed={selected} title={title} onClick={onClick}>
      {label}
    </button>
  )
}
