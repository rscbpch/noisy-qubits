import type { AlgorithmInfo } from '../../api/types'
import { defaultInputs } from '../../settings'
import Field from '../ui/Field'
import type { ControlProps } from './types'

export default function QubitSlider({ settings, onChange, algorithm }: ControlProps & { algorithm?: AlgorithmInfo }) {
  return (
    <Field label={`Qubits: ${settings.nQubits}`}>
      <input type="range" min={algorithm?.minQubits ?? 2} max={algorithm?.maxQubits ?? 10}
        value={settings.nQubits}
        onChange={(e) => {
          const nQubits = Number(e.target.value)
          // The typed inputs depend on the size, so reset them to match.
          onChange({ nQubits, ...defaultInputs(nQubits), djTruthTable: '' })
        }} />
    </Field>
  )
}
