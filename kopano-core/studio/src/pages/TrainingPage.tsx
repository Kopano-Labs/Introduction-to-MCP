import { motion } from 'framer-motion';
import { useEffect, useMemo, useState } from 'react';
import { getApiBase } from '../apiBase';

type KcStatusName = 'assigned' | 'in_progress' | 'submitted' | 'reviewed' | 'promoted';

interface KcRecord {
  id: string;
  title: string;
  teacher_context: string;
  student_response: string | null;
  teacher_review: string | null;
  status: KcStatusName;
  created_at: number;
  updated_at: number;
}

interface KcStatus {
  store_path: string;
  total_contexts: number;
  status_counts: Record<KcStatusName, number>;
  latest_context: Pick<KcRecord, 'id' | 'title' | 'status' | 'updated_at'> | null;
  owner_proof: string;
}

interface KcTrainingPayload {
  status: KcStatus;
  records: KcRecord[];
}

const emptyCounts: Record<KcStatusName, number> = {
  assigned: 0,
  in_progress: 0,
  submitted: 0,
  reviewed: 0,
  promoted: 0,
};

const fallbackStatus: KcStatus = {
  store_path: 'loading',
  total_contexts: 0,
  status_counts: emptyCounts,
  latest_context: null,
  owner_proof: 'local_only_domain_first_unproven',
};

const statusOrder: KcStatusName[] = ['assigned', 'in_progress', 'submitted', 'reviewed', 'promoted'];

const statusLabel: Record<KcStatusName, string> = {
  assigned: 'Assigned',
  in_progress: 'In progress',
  submitted: 'Submitted',
  reviewed: 'Reviewed',
  promoted: 'Promoted',
};

const apiRoot = getApiBase();

const postJson = async (url: string, body: object) => {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json();
};

const formatMillis = (value: number) => new Date(value).toLocaleString();

const defaultStudentResponse = [
  'Read source and store.',
  'Submit bounded evidence only.',
  'Owner-proof remains local_only_domain_first_unproven.',
].join(' ');

const defaultTeacherReview = [
  'Review: local proof only.',
  'No promotion.',
  'No owner-proof claim.',
].join(' ');

export function TrainingPage() {
  const [payload, setPayload] = useState<KcTrainingPayload>({ status: fallbackStatus, records: [] });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [title, setTitle] = useState('KC - ');
  const [teacherContext, setTeacherContext] = useState('One task. Read first. CRUD only.');
  const [studentResponse, setStudentResponse] = useState(defaultStudentResponse);
  const [teacherReview, setTeacherReview] = useState(defaultTeacherReview);
  const [eventLog, setEventLog] = useState<string[]>(['KC local CRUD ready.']);
  const [error, setError] = useState<string | null>(null);

  const selectedRecord = useMemo(() => {
    if (!payload.records.length) {
      return null;
    }

    return payload.records.find((record) => record.id === selectedId)
      ?? payload.records[0];
  }, [payload.records, selectedId]);

  const activeQueue = payload.records.filter((record) => (
    record.status === 'assigned' || record.status === 'in_progress' || record.status === 'submitted'
  ));
  const historicalRecords = payload.records.filter((record) => !activeQueue.some((activeRecord) => activeRecord.id === record.id));

  const refresh = async () => {
    const response = await fetch(`${apiRoot}/api/kc/training`);
    if (!response.ok) {
      throw new Error(`KC training API returned ${response.status}`);
    }

    const nextPayload = await response.json() as KcTrainingPayload;
    setPayload(nextPayload);
    setSelectedId((current) => {
      if (current && nextPayload.records.some((record) => record.id === current)) {
        return current;
      }
      const activeRecord = nextPayload.records.find((record) => record.status !== 'reviewed' && record.status !== 'promoted');
      return activeRecord?.id ?? nextPayload.records[0]?.id ?? null;
    });
  };

  const pushEvent = (message: string) => {
    setEventLog((prev) => [`${new Date().toLocaleTimeString()} | ${message}`, ...prev].slice(0, 5));
  };

  const runAction = async (label: string, action: () => Promise<unknown>) => {
    setError(null);
    try {
      await action();
      await refresh();
      pushEvent(label);
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : 'KC action failed.');
    }
  };

  useEffect(() => {
    void refresh().catch((refreshError) => {
      setError(refreshError instanceof Error ? refreshError.message : 'KC training API unavailable.');
    });
    const interval = window.setInterval(() => {
      void refresh().catch(() => undefined);
    }, 1800);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    setStudentResponse(selectedRecord?.student_response ?? defaultStudentResponse);
    setTeacherReview(selectedRecord?.teacher_review ?? defaultTeacherReview);
  }, [selectedRecord?.id, selectedRecord?.student_response, selectedRecord?.teacher_review]);

  const createAssignment = () => runAction('Teacher assignment created', async () => {
    const data = await postJson(`${apiRoot}/api/kc/records`, { title, teacher_context: teacherContext }) as { record: KcRecord };
    setSelectedId(data.record.id);
  });

  const submitResponse = () => {
    if (!selectedRecord) {
      return;
    }
    void runAction(`Student response submitted for ${selectedRecord.id}`, () => postJson(`${apiRoot}/api/kc/records/${selectedRecord.id}/submit`, {
      student_response: studentResponse,
    }));
  };

  const addReview = () => {
    if (!selectedRecord) {
      return;
    }
    void runAction(`Teacher review added for ${selectedRecord.id}`, () => postJson(`${apiRoot}/api/kc/records/${selectedRecord.id}/review`, {
      teacher_review: teacherReview,
    }));
  };

  const promote = () => {
    if (!selectedRecord) {
      return;
    }
    void runAction(`${selectedRecord.id} promoted`, () => postJson(`${apiRoot}/api/kc/records/${selectedRecord.id}/promote`, {}));
  };

  const seedStarter = () => runAction('Starter training task seeded', () => postJson(`${apiRoot}/api/kc/seed-training`, {}));

  return (
    <div className="training-layout sovereign-training">
      <motion.section
        className="sovereign-command"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.52 }}
      >
        <div className="sovereign-command-copy">
          <span className="sovereign-kicker">KC local CRUD</span>
          <h2>{selectedRecord?.title ?? 'No KC record selected'}</h2>
          <div className="proof-lock">
            <span>Owner proof</span>
            <strong>{payload.status.owner_proof}</strong>
          </div>
        </div>

        <div className="sovereign-metrics" aria-label="KC local status">
          <div>
            <span>Records</span>
            <strong>{payload.status.total_contexts}</strong>
          </div>
          <div>
            <span>Active</span>
            <strong>{activeQueue.length}</strong>
          </div>
          <div>
            <span>Reviewed</span>
            <strong>{payload.status.status_counts.reviewed ?? 0}</strong>
          </div>
        </div>
      </motion.section>

      <section className="sovereign-workbench">
        <motion.article className="focus-panel" layout>
          <div className="panel-heading active-assignment-heading">
            <div>
              <span className="sovereign-kicker">Active</span>
              <strong>{selectedRecord ? `${selectedRecord.id} | ${selectedRecord.title}` : 'No KC record selected'}</strong>
            </div>
            <span className={`status-token status-${selectedRecord?.status ?? 'assigned'}`}>
              {selectedRecord ? statusLabel[selectedRecord.status] : 'Waiting'}
            </span>
          </div>

          <div className="assignment-rail">
            <section>
              <span>Teacher</span>
              <p>{selectedRecord?.teacher_context ?? 'Create or seed an assignment to begin.'}</p>
            </section>
            <section className={selectedRecord?.student_response ? 'filled' : ''}>
              <span>Student</span>
              <p>{selectedRecord?.student_response ?? 'Awaiting student evidence.'}</p>
            </section>
            <section className={selectedRecord?.teacher_review ? 'filled' : ''}>
              <span>Review</span>
              <p>{selectedRecord?.teacher_review ?? 'Awaiting teacher review.'}</p>
            </section>
          </div>
        </motion.article>

        <motion.aside className="record-panel" layout>
          <div className="panel-heading">
            <span className="sovereign-kicker">Record stack</span>
            <button type="button" className="quiet-button" onClick={() => void refresh()}>Refresh</button>
          </div>

          <div className="status-comb">
            {statusOrder.map((status) => (
              <div key={status}>
                <span>{statusLabel[status]}</span>
                <strong>{payload.status.status_counts[status] ?? 0}</strong>
              </div>
            ))}
          </div>

          <div className="active-queue-stack">
            <div className="mini-section-heading">
              <span>Active now</span>
              <strong>{activeQueue.length}</strong>
            </div>
            {activeQueue.length > 0 ? activeQueue.map((record) => (
              <button
                key={record.id}
                type="button"
                className={`record-line priority-record ${selectedRecord?.id === record.id ? 'active' : ''}`}
                onClick={() => setSelectedId(record.id)}
              >
                <span>{record.id}</span>
                <strong>{record.title}</strong>
                <small>{statusLabel[record.status]} | {formatMillis(record.updated_at)}</small>
              </button>
            )) : (
              <div className="empty-active-record">No assigned, in-progress, or submitted KC task.</div>
            )}
          </div>

          <div className="sovereign-record-list">
            {historicalRecords.map((record) => (
              <button
                key={record.id}
                type="button"
                className={`record-line ${selectedRecord?.id === record.id ? 'active' : ''}`}
                onClick={() => setSelectedId(record.id)}
              >
                <span>{record.id}</span>
                <strong>{record.title}</strong>
                <small>{statusLabel[record.status]} | {formatMillis(record.updated_at)}</small>
              </button>
            ))}
          </div>
        </motion.aside>
      </section>

      <section className="command-dock">
        <motion.article className="dock-panel" layout>
          <div className="panel-heading">
            <span className="sovereign-kicker">KC response</span>
            <span className="dock-id">{selectedRecord?.id ?? 'select record'}</span>
          </div>
          <textarea
            rows={5}
            value={studentResponse}
            onChange={(event) => setStudentResponse(event.target.value)}
            aria-label="Student response"
          />
          <button type="button" className="command-button" disabled={!selectedRecord} onClick={submitResponse}>
            Submit evidence
          </button>
        </motion.article>

        <motion.article className="dock-panel" layout>
          <div className="panel-heading">
            <span className="sovereign-kicker">Teacher review</span>
            <span className="dock-id">{selectedRecord ? statusLabel[selectedRecord.status] : 'waiting'}</span>
          </div>
          <textarea
            rows={5}
            value={teacherReview}
            onChange={(event) => setTeacherReview(event.target.value)}
            aria-label="Teacher review"
          />
          <button type="button" className="command-button primary" disabled={!selectedRecord} onClick={addReview}>
            Review
          </button>
        </motion.article>

        <motion.article className="dock-panel compact-dock" layout>
          <div className="panel-heading">
            <span className="sovereign-kicker">Steward tools</span>
            <span className="dock-id">secondary</span>
          </div>
          <details className="steward-tools">
            <summary>Open assignment controls</summary>
            <label>
              <span>Title</span>
              <input value={title} onChange={(event) => setTitle(event.target.value)} />
            </label>
            <label>
              <span>Teacher assignment</span>
              <textarea rows={4} value={teacherContext} onChange={(event) => setTeacherContext(event.target.value)} />
            </label>
            <div className="dock-actions">
              <button type="button" className="quiet-button" onClick={() => void createAssignment()}>Create</button>
              <button type="button" className="quiet-button" onClick={() => void seedStarter()}>Seed</button>
              <button type="button" className="quiet-button danger" disabled={!selectedRecord} onClick={promote}>Promote</button>
            </div>
          </details>
          <div className="store-proof">
            <span>Store</span>
            <strong>{payload.status.store_path}</strong>
          </div>
        </motion.article>
      </section>

      <section className="proof-strip">
        {error && <div className="admin-error">{error}</div>}
        {eventLog.map((entry) => <span key={entry}>{entry}</span>)}
      </section>
    </div>
  );
}
