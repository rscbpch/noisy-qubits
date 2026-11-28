import type { RunResponse } from '../../api/types'
import { percent } from '../../lib/format'
import StatTiles from '../ui/StatTiles'

export default function ScoreTiles({ result }: { result: RunResponse | null }) {
  const show = (value: number | undefined) => (value === undefined ? undefined : percent(value))
  return (
    <StatTiles stats={[
      { label: 'Measured success rate', value: show(result?.score) },
      { label: 'Ideal success rate (no noise)', value: show(result?.idealScore) },
      { label: "Pass line (50% of ideal, 75% for Simon's)", value: result ? `≥ ${percent(result.passLine)}` : undefined },
      { label: 'Classical baseline', value: show(result?.baseline) },
    ]} />
  )
}
