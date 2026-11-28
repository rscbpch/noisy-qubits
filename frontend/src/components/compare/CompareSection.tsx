// Frame of the comparison section. Member 3 builds the grid and the reset.
import Button from '../ui/Button'
import Card from '../ui/Card'
import Legend from '../ui/Legend'
import Placeholder from '../ui/Placeholder'
import './CompareSection.css'

export default function CompareSection() {
  return (
    <Card>
      <div className="compare-head">
        <h2>Compare algorithms</h2>
        {/* Disabled while the grid has no rows. */}
        <Button disabled>Reset comparison</Button>
      </div>
      <p className="compare-note">
        Highest slider value (1 to 100) each algorithm passes, shown as <b>without → with ZNE (gain)</b>.
        A row is added each time you press <b>Run test</b> for an algorithm. Run another algorithm to
        add it, or run the same one again to refresh its row. Columns are always all
        four noise options: uniform noise and the three fake devices. Click a cell to open that run in
        the Circuit &amp; results tab. Press <b>Reset comparison</b> to start a new set.
      </p>
      <Placeholder title="Comparison grid" owner="Member 3" />
      <Legend items={[
        { label: 'Above 66 with ZNE', color: 'var(--pass-bg)' },
        { label: '33 to 66', color: 'var(--recovered-bg)' },
        { label: 'Below 33', color: 'var(--fail-bg)' },
      ]} />
      <p className="compare-note">
        ± a few points from shot noise (1024 shots). The Uniform noise column uses the noise type
        chosen when that row was run; hover a cell to see it.
      </p>
    </Card>
  )
}
