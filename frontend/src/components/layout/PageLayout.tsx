// Where the four areas of the page go. To rearrange the page, change this file
// and its CSS; the areas themselves do not need to change.
import type { ReactNode } from 'react'
import './PageLayout.css'

interface Props {
  header: ReactNode
  sidebar: ReactNode
  main: ReactNode
  below: ReactNode
}

export default function PageLayout({ header, sidebar, main, below }: Props) {
  return (
    <>
      {header}
      <div className="page-columns">
        <aside className="page-sidebar">{sidebar}</aside>
        <main className="page-main">{main}</main>
      </div>
      <div className="page-below">{below}</div>
    </>
  )
}
