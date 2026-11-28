import { MAX_SHOTS, MIN_SHOTS } from '../../lib/validation'
import Field from '../ui/Field'
import type { ControlProps } from './types'

export default function ShotsInput({ settings, onChange }: ControlProps) {
  return (
    <Field label="Shots">
      <input type="number" min={MIN_SHOTS} max={MAX_SHOTS} step={100} value={settings.shots}
        onChange={(e) => onChange({ shots: e.target.value })} />
    </Field>
  )
}
