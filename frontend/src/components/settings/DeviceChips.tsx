import { useState } from 'react'
import type { DeviceInfo } from '../../api/types'
import { MAX_TARGETS, targetLabel, type TargetId } from '../../settings'
import Chip from '../ui/Chip'
import type { ControlProps } from './types'
import '../ui/form.css'
import './DeviceChips.css'

export default function DeviceChips({ settings, onChange, devices }: ControlProps & { devices: DeviceInfo[] }) {
  const [full, setFull] = useState(false)
  const selected = settings.targets
  const choices: { id: TargetId; title: string }[] = [
    { id: 'uniform', title: 'Same error on every gate' },
    ...devices.map((d) => ({ id: d.id, title: `${d.numQubits} qubits` })),
  ]

  function toggle(id: TargetId) {
    const isSelected = selected.includes(id)
    const tooMany = !isSelected && selected.length >= MAX_TARGETS
    setFull(tooMany)
    if (tooMany || (isSelected && selected.length === 1)) return // keep 1 to 3
    onChange({ targets: isSelected ? selected.filter((t) => t !== id) : [...selected, id] })
  }

  return (
    <fieldset className="field">
      <legend>Devices (pick 1 to {MAX_TARGETS})</legend>
      <div className="chips">
        {choices.map(({ id, title }) => (
          <Chip key={id} label={targetLabel(id)} title={title} selected={selected.includes(id)}
            onClick={() => toggle(id)} />
        ))}
      </div>
      <span className="hint" aria-live="polite">
        {full
          ? `Up to ${MAX_TARGETS} per run. Click a selected one to swap.`
          : `The same circuit runs on each device. The main result shows ${targetLabel(selected[0])}.`}
      </span>
    </fieldset>
  )
}
