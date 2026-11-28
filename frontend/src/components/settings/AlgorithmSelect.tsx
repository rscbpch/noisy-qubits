import type { AlgorithmId, AlgorithmInfo } from '../../api/types'
import { ALGORITHM_DESCRIPTIONS } from '../../data/algorithms'
import Field from '../ui/Field'
import type { ControlProps } from './types'

export default function AlgorithmSelect({ settings, onChange, algorithms }: ControlProps & { algorithms: AlgorithmInfo[] }) {
  return (
    <Field label="Algorithm" hint={ALGORITHM_DESCRIPTIONS[settings.algorithm]}>
      <select value={settings.algorithm}
        onChange={(e) => onChange({ algorithm: e.target.value as AlgorithmId })}>
        {algorithms.map((a) => <option key={a.id} value={a.id}>{a.label}</option>)}
      </select>
    </Field>
  )
}
