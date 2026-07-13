import type { ComponentType } from 'react'
import tocJson from '../../content/toc.json'
import type { Toc, Domain, Note } from '../types'

export const toc = tocJson as unknown as Toc

export type MDXContent = ComponentType<{
  components?: Record<string, ComponentType<any>>
}>

const modules = import.meta.glob('../../content/**/*.mdx', {
  eager: true,
}) as Record<string, { default: MDXContent }>

export function getNoteComponent(file: string): MDXContent | null {
  return modules[`../../content/${file}`]?.default ?? null
}

export interface NoteLocation {
  note: Note
  domainId: string
  domainTitle: string
  chapterTitle: string
  sectionTitle: string
}

export function findNote(file: string): NoteLocation | null {
  for (const domain of toc.domains) {
    for (const chapter of domain.chapters) {
      for (const section of chapter.sections) {
        for (const note of section.notes) {
          if (note.file === file) {
            return {
              note,
              domainId: domain.id,
              domainTitle: domain.title,
              chapterTitle: chapter.title,
              sectionTitle: section.title,
            }
          }
        }
      }
    }
  }
  return null
}

export function countNotes(domain: Domain): number {
  return domain.chapters.reduce(
    (sum, chapter) => sum + chapter.sections.reduce((s, sec) => s + sec.notes.length, 0),
    0,
  )
}

export const totalNotes = toc.domains.reduce((sum, domain) => sum + countNotes(domain), 0)
