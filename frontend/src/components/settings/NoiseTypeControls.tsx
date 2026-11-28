import type { NoiseType } from '../../api/types'
import CheckField from '../ui/CheckField'
import Field from '../ui/Field'
import type { ControlProps } from './types'

const NOISE_TYPE_LABELS: Record<NoiseType, string> = {
  depolarizing: 'Depolarizing (main)',
  bit_flip: 'Bit-flip',
  phase_flip: 'Phase-flip',
  amplitude_damping: 'Amplitude damping (T1)',
}

export default function NoiseTypeControls({ settings, onChange }: ControlProps) {
  if (settings.targets[0] !== 'uniform') {
    return (
      <p className="hint">
        Fake devices use noise copied from a real IBM machine, so there is no noise type to choose.
      </p>
    )
  }
  return (
    <>
      <Field label="Noise type">
        <select value={settings.noiseType}
          onChange={(e) => onChange({ noiseType: e.target.value as NoiseType })}>
          {Object.entries(NOISE_TYPE_LABELS).map(([id, label]) => (
            <option key={id} value={id}>{label}</option>
          ))}
        </select>
      </Field>
      <CheckField label="Add readout error" checked={settings.readoutError}
        onChange={(readoutError) => onChange({ readoutError })} />
    </>
  )
}
