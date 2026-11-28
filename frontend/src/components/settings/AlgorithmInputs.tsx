// The typed input of the selected algorithm.
import { secretLength, type OracleChoice } from '../../settings'
import Field from '../ui/Field'
import type { ControlProps } from './types'

export default function AlgorithmInputs({ settings, onChange }: ControlProps) {
  const { algorithm, nQubits } = settings

  switch (algorithm) {
    case 'superposition':
      return <p className="hint">No extra input for this algorithm.</p>

    case 'qft':
      return (
        <Field label={`Input state (${nQubits} bits)`}>
          <input type="text" className="mono" value={settings.qftInput}
            onChange={(e) => onChange({ qftInput: e.target.value })} />
        </Field>
      )

    case 'qpe': {
      const size = 2 ** (nQubits - 1)
      const k = Number(settings.qpeK)
      const valid = /^\d+$/.test(settings.qpeK) && k < size
      return (
        <Field label={`Phase k/${size} (k = 0 to ${size - 1})`}
          hint={valid ? `The phase is k/${size}, so ${k} means ${k / size}.` : undefined}>
          <input type="text" inputMode="numeric" value={settings.qpeK}
            onChange={(e) => onChange({ qpeK: e.target.value })} />
        </Field>
      )
    }

    case 'deutsch_jozsa':
      return (
        <>
          <Field label="Oracle">
            <select value={settings.djOracle}
              onChange={(e) => onChange({ djOracle: e.target.value as OracleChoice })}>
              <option value="balanced">balanced</option>
              <option value="constant-0">constant-0</option>
              <option value="constant-1">constant-1</option>
              {/* Not in the sample UI, but the project description requires it. */}
              <option value="typed">typed truth table</option>
            </select>
          </Field>
          {settings.djOracle === 'typed' && (
            <Field label={`Truth table (${2 ** (nQubits - 1)} characters)`}>
              <textarea className="mono" rows={3} value={settings.djTruthTable}
                onChange={(e) => onChange({ djTruthTable: e.target.value })} />
            </Field>
          )}
        </>
      )

    case 'simon':
      return (
        <Field label={`Secret string (${secretLength(nQubits)} bits, not all zeros)`}>
          <input type="text" className="mono" value={settings.simonSecret}
            onChange={(e) => onChange({ simonSecret: e.target.value })} />
        </Field>
      )
  }
}
