import type { RunRequest, RunResponse } from '../../api/types'
import { algorithmLabel } from '../../data/algorithms'
import { percent } from '../../lib/format'
import { targetLabel } from '../../settings'
import StatusPill from '../ui/StatusPill'
import './ResultBanner.css'

interface Props {
  /** The result and the request that produced it, or null before a run. */
  run: { request: RunRequest; result: RunResponse } | null
  running: boolean
}

function message({ request, result }: { request: RunRequest; result: RunResponse }): string {
  const line = percent(result.passLine)
  const raw = percent(result.score)
  const mitigated = result.mitigation ? percent(result.mitigation.mitigated) : null
  if (result.verdict === 'PASS') return `Success rate ${raw} is above the pass line (${line}), with no help.`
  if (result.verdict === 'RECOVERED') return `Failed first (${raw}), passed after ZNE (${mitigated}). Pass line: ${line}.`
  if (request.zne) return `Below the pass line (${line}) even with ZNE (${mitigated}).`
  return `Below the pass line (${line}) at ${raw}. Turn on ZNE and run again to try to recover it.`
}

export default function ResultBanner({ run, running }: Props) {
  return (
    <div className="result-banner" aria-live="polite">
      <StatusPill verdict={run?.result.verdict ?? null} />
      <div className="result-text">
        {run ? (
          <>
            <b>{algorithmLabel(run.request.params.algorithm)}</b> on{' '}
            <b>{targetLabel(run.request.device ?? 'uniform')}</b> at noise <b>{run.request.slider}</b>.
            <br />
            {message(run)}
          </>
        ) : running ? (
          'Running the test...'
        ) : (
          <>Choose a setup on the left and press <b>Run test</b>.</>
        )}
      </div>
    </div>
  )
}
