import type { AlgorithmId } from '../../api/types'
import AboutTab from '../AboutTab' // Member 5's component, left as it is
import HowToUse from './HowToUse'
import PassRules from './PassRules'
import './AboutPanel.css'

export default function AboutPanel({ algorithm }: { algorithm: AlgorithmId }) {
  return (
    <div className="about">
      <AboutTab algorithm={algorithm} />
      <PassRules />
      <HowToUse />
    </div>
  )
}
