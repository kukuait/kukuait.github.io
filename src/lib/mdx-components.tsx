import { CodeBlock } from '../components/CodeBlock'

// 這裡註冊的元件在所有 MDX 筆記內可直接使用,不需 import。
// 新增互動演示元件時:元件寫在 src/components/,然後在此加入註冊。
export const mdxComponents = {
  pre: CodeBlock,
}
