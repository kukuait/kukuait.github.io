import { useEffect, useId, useState } from 'react'
import mermaid from 'mermaid'

mermaid.initialize({ startOnLoad: false, theme: 'dark', fontFamily: 'inherit' })

export function Mermaid({ chart }: { chart: string }) {
  const renderId = useId().replace(/[^a-zA-Z0-9]/g, '')
  const [svg, setSvg] = useState('')
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    mermaid
      .render(`mmd${renderId}`, chart)
      .then((result) => {
        if (!cancelled) setSvg(result.svg)
      })
      .catch(() => {
        if (!cancelled) setFailed(true)
      })
    return () => {
      cancelled = true
    }
  }, [chart, renderId])

  if (failed) {
    return (
      <pre>
        <code className="hljs">{chart}</code>
      </pre>
    )
  }

  return <div className="mermaid-diagram" dangerouslySetInnerHTML={{ __html: svg }} />
}
