import './Header.css'

export default function Header({ sampleData }: { sampleData: boolean }) {
  return (
    <header className="header">
      <h1>Noisy Qubits</h1>
      <span className="header-tagline">
        How much noise can a quantum algorithm take before it stops working, and can error handling rescue it?
      </span>
      {sampleData && <span className="header-badge">Sample data: nothing is simulated yet</span>}
    </header>
  )
}
