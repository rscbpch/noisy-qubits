import Section from '../ui/Section'

const STEPS = [
  'Pick an algorithm and the number of qubits. Start with a simple one, such as Deutsch-Jozsa or QFT.',
  'Fill the algorithm inputs. Invalid input shows a message and does not run.',
  'Choose the noise: a fake device or uniform noise.',
  'Set the noise slider and check the shots (default 1024).',
  'Leave ZNE off for the first run, then press Run test.',
  'Read the success rate and the outcomes histogram.',
  'If it failed, turn on ZNE and run again to see RECOVERED or FAIL and the before/after charts.',
  'Run more algorithms to add rows to the Compare grid and see the highest passing noise level for each algorithm and noise option. Press Reset comparison to start a new set.',
]

export default function HowToUse() {
  return (
    <Section title="How to use this page">
      <ol>
        {STEPS.map((step) => <li key={step}>{step}</li>)}
      </ol>
    </Section>
  )
}
