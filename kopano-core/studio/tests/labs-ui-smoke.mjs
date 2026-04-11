import assert from 'node:assert/strict';

function appendStreamChunk(current, chunk) {
  if (chunk.type !== 'chunk' || !chunk.content) {
    return current;
  }
  return current + chunk.content;
}

function toEditableTask(task) {
  return { ...task };
}

function toEditableArtifact(artifact) {
  return { ...artifact };
}

let current = '';
current = appendStreamChunk(current, { type: 'chunk', content: 'Hello ' });
current = appendStreamChunk(current, { type: 'chunk', content: 'world' });
current = appendStreamChunk(current, { type: 'final' });
assert.equal(current, 'Hello world');

const task = { id: 7, title: 'Ship connector cards', description: 'Add live actions.', owner: 'DEV_1', priority: 'high' };
const editableTask = toEditableTask(task);
assert.deepEqual(editableTask, task);
assert.notEqual(editableTask, task);

const artifact = { id: 3, artifact_type: 'api', title: 'Azure Playbook', summary: 'Demo day flow', status: 'draft', link: 'Orch Forge' };
const editableArtifact = toEditableArtifact(artifact);
assert.deepEqual(editableArtifact, artifact);
assert.notEqual(editableArtifact, artifact);

console.log('labs-ui smoke tests passed');
