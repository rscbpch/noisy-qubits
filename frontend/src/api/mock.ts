// FAKE data so the website can be built before the API exists.
// No simulation happens here: the numbers only show what the layout looks like.
import { sliderLabel } from '../lib/sliderLabel'
import type { RunRequest, RunResponse, Verdict } from './types'

/** The classical baselines, as in the Python modules. */
function baselineFor(params: RunRequest['params']): number {
  switch (params.algorithm) {
    case 'qft': return 1 / 2 ** params.nQubits
    case 'qpe': return 1 / 2 ** (params.nQubits - 1)
    case 'superposition': return 0 // placeholder in superposition.py
    default: return 0.5 // Deutsch-Jozsa and Simon's
  }
}

export async function mockRun(request: RunRequest): Promise<RunResponse> {
  await new Promise((resolve) => setTimeout(resolve, 400))

  const { params, slider } = request
  const score = Math.exp(-slider / 40)
  // Pass line: 50% of an ideal score of 1, or 75% for Simon's.
  const passLine = params.algorithm === 'simon' ? 0.75 : 0.5
  let verdict: Verdict = score >= passLine ? 'PASS' : 'FAIL'
  if (verdict === 'FAIL' && request.zne && score >= passLine / 2) verdict = 'RECOVERED'

  return {
    circuit: { numQubits: 0, ops: [] },
    sliderLabel: sliderLabel(request.mode, slider),
    shots: request.shots,
    counts: {},
    idealScore: 1,
    score,
    baseline: baselineFor(params),
    passLine,
    verdict,
    // Filled only when ZNE ran, which is when the raw test failed.
    mitigation:
      request.zne && score < passLine
        ? {
            factors: [1, 2, 3],
            scores: [score, score ** 2, score ** 3],
            raw: score,
            mitigated: Math.min(1, score * 2),
            method: 'exponential',
            curve: [],
            reliable: true,
          }
        : null,
    perQubit: [],
  }
}
