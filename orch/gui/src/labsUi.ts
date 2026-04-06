export interface StreamChunk {
  type: string;
  content?: string;
}

export interface EditableTask {
  id: number;
  title: string;
  description: string;
  owner: string;
  priority: string;
}

export interface EditableArtifact {
  id: number;
  artifact_type: string;
  title: string;
  summary: string;
  status: string;
  link: string | null;
}

export function appendStreamChunk(current: string, chunk: StreamChunk): string {
  if (chunk.type !== 'chunk' || !chunk.content) {
    return current;
  }
  return current + chunk.content;
}

export function toEditableTask(task: EditableTask): EditableTask {
  return { ...task };
}

export function toEditableArtifact(artifact: EditableArtifact): EditableArtifact {
  return { ...artifact };
}
