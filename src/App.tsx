import { useEffect, useState } from 'react'
import { toc, getNoteComponent, findNote, countNotes, totalNotes } from './lib/content'
import { mdxComponents } from './lib/mdx-components'

function readHash(): string | null {
  const hash = decodeURIComponent(window.location.hash.replace(/^#\/?/, ''))
  return hash || null
}

function initialDomainId(file: string | null): string {
  if (file) {
    const location = findNote(file)
    if (location) return location.domainId
  }
  const saved = localStorage.getItem('active-domain')
  if (saved && toc.domains.some((d) => d.id === saved)) return saved
  return toc.domains[0].id
}

export default function App() {
  const [file, setFile] = useState<string | null>(readHash)
  const [domainId, setDomainId] = useState<string>(() => initialDomainId(readHash()))

  useEffect(() => {
    const onHashChange = () => setFile(readHash())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const location = file ? findNote(file) : null
  const Note = file ? getNoteComponent(file) : null

  // 透過筆記內連結跳到另一個 domain 的筆記時,側欄跟著切換
  useEffect(() => {
    if (location && location.domainId !== domainId) setDomainId(location.domainId)
  }, [location?.domainId])

  const switchDomain = (id: string) => {
    setDomainId(id)
    localStorage.setItem('active-domain', id)
  }

  const domain = toc.domains.find((d) => d.id === domainId) ?? toc.domains[0]
  const domainNotes = countNotes(domain)

  return (
    <div className="layout">
      <aside className="sidebar">
        <a className="brand" href="#/">
          <span className="brand-icon">TN</span>
          技術學習筆記
          <span className="brand-count">{totalNotes}</span>
        </a>
        <div className="domain-tabs">
          {toc.domains.map((d) => (
            <button
              key={d.id}
              className={d.id === domain.id ? 'domain-tab active' : 'domain-tab'}
              title={d.description}
              onClick={() => switchDomain(d.id)}
            >
              {d.title}
              <span className="domain-count">{countNotes(d)}</span>
            </button>
          ))}
        </div>
        <nav>
          {domainNotes === 0 && <p className="empty-hint">此領域尚無筆記</p>}
          {domain.chapters.map((chapter, i) => (
            <details key={chapter.id} open className="chapter">
              <summary>
                <span className="chapter-num">{String(i + 1).padStart(2, '0')}</span>
                {chapter.title}
              </summary>
              {chapter.sections.length === 0 && <p className="empty-hint">尚無筆記</p>}
              {chapter.sections.map((section) => (
                <div key={section.id} className="section">
                  <h3>{section.title}</h3>
                  <ul>
                    {section.notes.map((note) => (
                      <li key={note.id}>
                        <a
                          href={`#/${note.file}`}
                          className={note.file === file ? 'active' : ''}
                        >
                          {note.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </details>
          ))}
        </nav>
      </aside>
      <main className="main">
        {location && Note ? (
          <article className="note">
            <div className="crumbs">
              <span>{location.domainTitle}</span>
              <span className="crumb-sep">›</span>
              <span>{location.chapterTitle}</span>
              <span className="crumb-sep">›</span>
              <span>{location.sectionTitle}</span>
              {location.note.tags && location.note.tags.length > 0 && (
                <span className="tags">
                  {location.note.tags.map((tag) => (
                    <span key={tag} className="tag-chip">{tag}</span>
                  ))}
                </span>
              )}
              <span className="date">{location.note.date}</span>
            </div>
            <div className="markdown">
              <Note components={mdxComponents} />
            </div>
          </article>
        ) : file ? (
          <div className="welcome">
            <h1>找不到這篇筆記</h1>
            <p>
              目錄索引裡沒有 <code>{file}</code>，請從左側目錄重新選擇。
            </p>
          </div>
        ) : (
          <div className="welcome">
            <h1>技術學習筆記</h1>
            <p>
              目前共 {totalNotes} 篇筆記，涵蓋 LLM、SWE、SRE 三個領域。從左側切換領域、
              挑一篇開始；或在 Claude Code 裡直接問一個技術問題，講解會自動歸檔到對應章節。
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
