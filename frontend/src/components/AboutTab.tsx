import { ALGORITHM_ABOUT, NOISE_TYPES, type AlgorithmId } from '../data/aboutContent'

interface AboutTabProps {
  algorithm: AlgorithmId
}

export default function AboutTab({ algorithm }: AboutTabProps) {
  const about = ALGORITHM_ABOUT[algorithm]
  return (
    <section aria-label="About the selected algorithm">
      <h2>{about.title}</h2>
      <p>{about.what}</p>
      <h3>How noise affects it</h3>
      <p>{about.noise}</p>

      <h3>The noise types</h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Noise</th>
              <th>What it does</th>
              <th>Zero-noise extrapolation</th>
            </tr>
          </thead>
          <tbody>
            {NOISE_TYPES.map((n) => (
              <tr key={n.name}>
                <td>{n.name}</td>
                <td>{n.what}</td>
                <td>{n.zne}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p>
        Fake devices copy the calibration data of a real IBM machine, so they already mix gate errors, T1 decay and
        readout error, with different values for each qubit.
      </p>
    </section>
  )
}
