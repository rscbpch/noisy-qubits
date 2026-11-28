// Marks a part that is not built yet, and who builds it.
import './Placeholder.css'

export default function Placeholder({ title, owner }: { title: string; owner: string }) {
  return (
    <div className="placeholder">
      <b>{title}</b>
      <span>Not built yet ({owner})</span>
    </div>
  )
}
