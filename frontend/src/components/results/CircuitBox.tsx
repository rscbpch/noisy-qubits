// CircuitDiagram.tsx will replace the placeholder (Member 2, next step).
import Collapsible from '../ui/Collapsible'
import Legend from '../ui/Legend'
import Placeholder from '../ui/Placeholder'

export default function CircuitBox() {
  return (
    <Collapsible title="Circuit">
      <Placeholder title="Circuit diagram" owner="Member 2, next step" />
      <Legend items={[
        { label: 'Gate', color: 'var(--accent)' },
        { label: 'Controlled phase / controlled-U', color: 'var(--controlled)' },
        { label: 'Measurement', color: 'var(--ideal)' },
      ]} />
    </Collapsible>
  )
}
