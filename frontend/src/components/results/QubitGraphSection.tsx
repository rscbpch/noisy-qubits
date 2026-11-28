// Member 3 builds the graph that goes here.
import Legend from '../ui/Legend'
import Placeholder from '../ui/Placeholder'
import Section from '../ui/Section'

export default function QubitGraphSection() {
  return (
    <Section title="Chance each qubit reads 1">
      <Legend items={[
        { label: 'Ideal (no noise)', color: 'var(--ideal)' },
        { label: 'Noisy result', color: 'var(--noisy)' },
      ]} />
      <Placeholder title="Per-qubit graph" owner="Member 3" />
    </Section>
  )
}
