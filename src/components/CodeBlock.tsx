import { isValidElement, type ReactNode } from 'react'
import hljs from 'highlight.js/lib/common'
import { Mermaid } from './Mermaid'

interface CodeElementProps {
  className?: string
  children?: ReactNode
}

// 接管 MDX 的 <pre>:```mermaid 轉成圖表,其餘做語法上色
export function CodeBlock({ children }: { children?: ReactNode }) {
  if (!isValidElement(children)) {
    return <pre>{children}</pre>
  }

  const { className = '', children: raw } = children.props as CodeElementProps
  const lang = /language-([\w-]+)/.exec(className)?.[1]
  const text = String(raw ?? '').replace(/\n$/, '')

  if (lang === 'mermaid') {
    return <Mermaid chart={text} />
  }

  if (!lang || !hljs.getLanguage(lang)) {
    return (
      <pre>
        <code className="hljs">{text}</code>
      </pre>
    )
  }

  const html = hljs.highlight(text, { language: lang }).value
  return (
    <pre>
      <code className="hljs" dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  )
}
