// "Circuit & results" tab, shared with Member 1. Move the lines below to change
// the order of the blocks.
import type { RunRequest, RunResponse } from '../../api/types'
import CircuitBox from './CircuitBox'
import OutcomesSection from './OutcomesSection'
import QubitGraphSection from './QubitGraphSection'
import ResultBanner from './ResultBanner'
import ScoreTiles from './ScoreTiles'

export interface ResultsTabProps {
  request: RunRequest | null
  result: RunResponse | null
  error: string | null
  running: boolean
}

export default function ResultsTab({ request, result, error, running }: ResultsTabProps) {
  return (
    <>
      <ResultBanner run={request && result ? { request, result } : null} running={running} />
      {error && <p className="error" role="alert">{error}</p>}
      <ScoreTiles result={result} />
      <QubitGraphSection />
      <OutcomesSection />
      <CircuitBox />
    </>
  )
}
