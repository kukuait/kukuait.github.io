# 技術學習筆記站（LLM / SWE / SRE）

這個 repo 是一個獨立的 Vite + React + MDX 技術筆記站，唯一用途就是撰寫與發布
技術學習筆記，線上版本部署在 GitHub Pages。

## 發布方式：push 即部署

push 到 `master` 後，GitHub Actions（`.github/workflows/deploy.yml`）會自動
build 並部署到 GitHub Pages，**不需要在本地端把站跑起來**。

- 一篇筆記的線上網址：`<Pages 網址>/#/<file>`（`<file>` 是 toc 的 `file`
  欄位，如 `llm/03-inference/what-is-kv-cache.mdx`）。
- MDX 語法錯誤會讓 CI build 失敗、筆記不會上線（舊版站會保留）。push 前先用
  下方的 podman build 驗證。

## 架構：內容與程式碼分離

```
├── content/
│   ├── toc.json                            # 唯一的目錄索引(domain → 大章節 → 小章節 → 筆記)
│   └── <domain-id>/<chapter-id>/<slug>.mdx # 每篇筆記一個 MDX 檔;domain-id ∈ llm / swe / sre
└── src/
    ├── components/             # Mermaid、CodeBlock 與日後的互動演示元件
    └── lib/mdx-components.tsx  # MDX 筆記內可直接使用的元件註冊表
```

- 筆記是 MDX，支援：GFM 表格、`mermaid` code block 圖表、KaTeX 公式
  （`$...$` / `$$...$$`）、程式碼語法上色（highlight.js）。
- 新增/修改筆記只動 `content/`；互動演示元件放 `src/components/` 並在
  `mdx-components.tsx` 註冊後，MDX 內可直接使用（不需 import）。
- 撰寫與歸檔規則以 `.claude/skills/tech-note/SKILL.md` 為準，特別是其中的
  「MDX 語法陷阱」——內文出現裸的 `<`、`{` 會讓整站編譯失敗。
- `toc.json` 結構：`domains[] → chapters[] → sections[] → notes[]`;note 欄位
  `{ id, title, file, date, tags }`,`file` 是相對 `content/` 的路徑(含 domain
  目錄)，沒列入 toc 的筆記不會顯示在站上。
- 筆記內互連用 in-app hash 路由：`[標題](#/<file>)`,`<file>` 同 toc 的 `file`
  欄位，可跨 domain 連結。

## 常用指令

主機**沒有** Node.js/npm，不要直接在主機跑 npm/node/python；跑腳本與 build
一律透過容器（本機用 podman，有 docker 的環境把 podman 換成 docker 即可）。
以下指令在 repo 根目錄執行：

```bash
# push 前的 build 驗證(typecheck + vite 打包;失敗通常是 MDX 語法錯誤)
docker build -t tech-notes .

# 中文排版檢查/修正(規則見 .claude/skills/tech-note/SKILL.md 文體規範)
# --fix 直接改檔;去掉 --fix 改成 dry-run（印 diff）;--check 讓 CI 偵測未格式化
docker run --rm -v "$PWD":/work -w /work python:3.12-alpine \
  sh -c "pip install -q pangu && python3 scripts/zh-punct.py --fix content/<檔案>"

# (可選)本地預覽 → http://127.0.0.1:3000;平常不需要,線上版看 GitHub Pages
docker compose up -d --build
```
