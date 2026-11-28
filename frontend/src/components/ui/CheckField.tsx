import './form.css'

interface Props {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

export default function CheckField({ label, checked, onChange }: Props) {
  return (
    <label className="check">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  )
}
