export interface Note {
  id: string
  title: string
  file: string
  date: string
  tags?: string[]
}

export interface Section {
  id: string
  title: string
  notes: Note[]
}

export interface Chapter {
  id: string
  title: string
  description?: string
  sections: Section[]
}

export interface Domain {
  id: string
  title: string
  description?: string
  chapters: Chapter[]
}

export interface Toc {
  domains: Domain[]
}
