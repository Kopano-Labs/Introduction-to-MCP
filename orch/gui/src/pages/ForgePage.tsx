import { AnimatePresence, motion } from 'framer-motion';
import { toEditableArtifact, toEditableTask } from '../labsUi';
import type { CoworkRoom, CoworkRoomSummary } from '../types';

interface ForgePageProps {
  coworkRooms: CoworkRoomSummary[];
  activeRoom: CoworkRoom | null;
  roomName: string;
  roomMission: string;
  taskTitle: string;
  taskDescription: string;
  taskOwner: string;
  taskPriority: string;
  artifactTitle: string;
  artifactSummary: string;
  artifactType: string;
  editingTaskId: number | null;
  editingArtifactId: number | null;
  laneOrder: string[];
  ownerOptions: string[];
  onRoomNameChange: (value: string) => void;
  onRoomMissionChange: (value: string) => void;
  onTaskTitleChange: (value: string) => void;
  onTaskDescriptionChange: (value: string) => void;
  onTaskOwnerChange: (value: string) => void;
  onTaskPriorityChange: (value: string) => void;
  onArtifactTitleChange: (value: string) => void;
  onArtifactSummaryChange: (value: string) => void;
  onArtifactTypeChange: (value: string) => void;
  onCreateRoom: () => void;
  onSelectRoom: (roomId: number) => void;
  onCreateOrUpdateTask: () => void;
  onCreateArtifact: () => void;
  onUpdateTaskStatus: (taskId: number, status: string) => void;
  onUpdateTaskOwner: (taskId: number, owner: string) => void;
  onMoveTaskToLane: (taskId: number, lane: string) => void;
  onEditTask: (task: ReturnType<typeof toEditableTask>) => void;
  onEditArtifact: (artifact: ReturnType<typeof toEditableArtifact>) => void;
}

export function ForgePage({
  coworkRooms,
  activeRoom,
  roomName,
  roomMission,
  taskTitle,
  taskDescription,
  taskOwner,
  taskPriority,
  artifactTitle,
  artifactSummary,
  artifactType,
  editingTaskId,
  editingArtifactId,
  laneOrder,
  ownerOptions,
  onRoomNameChange,
  onRoomMissionChange,
  onTaskTitleChange,
  onTaskDescriptionChange,
  onTaskOwnerChange,
  onTaskPriorityChange,
  onArtifactTitleChange,
  onArtifactSummaryChange,
  onArtifactTypeChange,
  onCreateRoom,
  onSelectRoom,
  onCreateOrUpdateTask,
  onCreateArtifact,
  onUpdateTaskStatus,
  onUpdateTaskOwner,
  onMoveTaskToLane,
  onEditTask,
  onEditArtifact,
}: ForgePageProps) {
  return (
    <div className="page-layout forge-layout">
      <motion.section className="hero-panel hero-forge" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72 }}>
        <div className="hero-copy">
          <span className="eyebrow">Forge</span>
          <div className="headline-stack">
            <span className="headline-line">Build in public.</span>
            <span className="headline-line">Route with intent.</span>
            <span className="headline-line">Ship with receipts.</span>
          </div>
          <p className="hero-copy-text">
            Forge is the execution view in the safe route: open the active room, show tasks and artifacts, and only edit if you need an optional proof point.
          </p>
        </div>
        <div className="quick-launch-grid compact">
          <article className="quick-launch-card static">
            <span className="stat-label">Rooms</span>
            <strong>{coworkRooms.length}</strong>
            <p>Prepared workspaces ready for demo routing.</p>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Tasks</span>
            <strong>{activeRoom?.dispatch_summary.total_tasks ?? 0}</strong>
            <p>Current room workload visible without requiring live edits.</p>
          </article>
          <article className="quick-launch-card static">
            <span className="stat-label">Artifacts</span>
            <strong>{activeRoom?.artifact_summary.total_artifacts ?? 0}</strong>
            <p>Outputs stay attached to the room so the story has receipts.</p>
          </article>
        </div>
      </motion.section>

      <section className="feature-grid forge-grid-top">
        <motion.article className="glass-card composer-card" layout>
          <div className="card-topline">
            <span className="eyebrow">New room</span>
            <span className="signal-chip neutral">optional</span>
          </div>
          <h2>Optional room creation</h2>
          <label className="field-shell">
            <span>Name</span>
            <input value={roomName} onChange={(event) => onRoomNameChange(event.target.value)} />
          </label>
          <label className="field-shell">
            <span>Mission</span>
            <textarea rows={3} value={roomMission} onChange={(event) => onRoomMissionChange(event.target.value)} />
          </label>
          <button type="button" className="action-button primary" onClick={onCreateRoom}>Launch room</button>
        </motion.article>

        <motion.article className="glass-card room-rail-card" layout>
          <div className="card-topline">
            <span className="eyebrow">Rooms</span>
            <span className="signal-chip neutral">{coworkRooms.length}</span>
          </div>
          <h2>Open the active room</h2>
          <div className="room-rail">
            {coworkRooms.map((room) => (
              <button key={room.id} type="button" className={`room-chip ${activeRoom?.id === room.id ? 'active' : ''}`} onClick={() => onSelectRoom(room.id)}>
                <span>{room.name}</span>
                <small>{room.status}</small>
              </button>
            ))}
          </div>
        </motion.article>
      </section>

      {activeRoom && (
        <>
          <section className="feature-grid forge-editor-grid">
            <motion.article className="glass-card composer-card" layout>
              <div className="card-topline">
                <span className="eyebrow">Task composer</span>
                <span className="signal-chip neutral">{editingTaskId ? 'edit' : 'optional'}</span>
              </div>
              <h2>{editingTaskId ? 'Edit task' : 'Optional task edit'}</h2>
              <label className="field-shell">
                <span>Title</span>
                <input value={taskTitle} onChange={(event) => onTaskTitleChange(event.target.value)} />
              </label>
              <label className="field-shell">
                <span>Description</span>
                <textarea rows={3} value={taskDescription} onChange={(event) => onTaskDescriptionChange(event.target.value)} />
              </label>
              <div className="field-row">
                <label className="field-shell">
                  <span>Owner</span>
                  <select value={taskOwner} onChange={(event) => onTaskOwnerChange(event.target.value)}>
                    {ownerOptions.map((owner) => <option key={owner} value={owner}>{owner}</option>)}
                  </select>
                </label>
                <label className="field-shell">
                  <span>Priority</span>
                  <select value={taskPriority} onChange={(event) => onTaskPriorityChange(event.target.value)}>
                    <option value="critical">critical</option>
                    <option value="high">high</option>
                    <option value="building">building</option>
                  </select>
                </label>
              </div>
              <button type="button" className="action-button primary" onClick={onCreateOrUpdateTask}>
                {editingTaskId ? 'Save task' : 'Add task'}
              </button>
            </motion.article>

            <motion.article className="glass-card composer-card" layout>
              <div className="card-topline">
                <span className="eyebrow">Artifact composer</span>
                <span className="signal-chip neutral">{editingArtifactId ? 'edit' : 'optional'}</span>
              </div>
              <h2>{editingArtifactId ? 'Edit artifact' : 'Optional artifact edit'}</h2>
              <label className="field-shell">
                <span>Type</span>
                <select value={artifactType} onChange={(event) => onArtifactTypeChange(event.target.value)}>
                  <option value="prompt">prompt</option>
                  <option value="api">api</option>
                  <option value="screen">screen</option>
                  <option value="note">note</option>
                </select>
              </label>
              <label className="field-shell">
                <span>Title</span>
                <input value={artifactTitle} onChange={(event) => onArtifactTitleChange(event.target.value)} />
              </label>
              <label className="field-shell">
                <span>Summary</span>
                <textarea rows={3} value={artifactSummary} onChange={(event) => onArtifactSummaryChange(event.target.value)} />
              </label>
              <button type="button" className="action-button primary" onClick={onCreateArtifact}>
                {editingArtifactId ? 'Save artifact' : 'Add artifact'}
              </button>
            </motion.article>
          </section>

          <motion.section className="glass-card lane-board" layout>
            <div className="card-topline">
              <span className="eyebrow">Active room board</span>
              <span className="signal-chip neutral">{activeRoom.dispatch_summary.total_tasks} tasks</span>
            </div>
            <div className="lane-board-header">
              <div>
                <h2>{activeRoom.name}</h2>
                <p>{activeRoom.mission}</p>
              </div>
              <div className="badge-cluster">
                <span className="status-badge neutral">{activeRoom.dispatch_summary.in_progress} active</span>
                <span className="status-badge neutral">{activeRoom.dispatch_summary.completed} done</span>
                <span className="status-badge neutral">{activeRoom.artifact_summary.total_artifacts} artifacts</span>
              </div>
            </div>

            <div className="lane-columns">
              {laneOrder.map((lane) => (
                <div key={lane} className="lane-column">
                  <div className="lane-column-top">
                    <strong>{lane}</strong>
                    <span>{activeRoom.lanes[lane]?.length ?? 0}</span>
                  </div>
                  <AnimatePresence mode="popLayout">
                    {(activeRoom.lanes[lane] ?? []).map((task) => (
                      <motion.article
                        key={task.id}
                        layout
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -16 }}
                        className="lane-task-card"
                      >
                        <div className="lane-task-top">
                          <strong>{task.title}</strong>
                          <span className={`signal-chip ${task.priority === 'critical' ? 'alert' : task.priority === 'high' ? 'thinking' : 'neutral'}`}>
                            {task.priority}
                          </span>
                        </div>
                        <p>{task.description}</p>
                        <div className="field-row">
                          <label className="field-shell compact">
                            <span>Owner</span>
                            <select value={task.owner} onChange={(event) => onUpdateTaskOwner(task.id, event.target.value)}>
                              {ownerOptions.map((owner) => <option key={owner} value={owner}>{owner}</option>)}
                            </select>
                          </label>
                          <label className="field-shell compact">
                            <span>Status</span>
                            <select value={task.status} onChange={(event) => onUpdateTaskStatus(task.id, event.target.value)}>
                              <option value="queued">queued</option>
                              <option value="in_progress">in progress</option>
                              <option value="completed">completed</option>
                            </select>
                          </label>
                        </div>
                        <label className="field-shell compact">
                          <span>Move lane</span>
                          <select value={task.lane} onChange={(event) => onMoveTaskToLane(task.id, event.target.value)}>
                            {laneOrder.map((laneOption) => <option key={laneOption} value={laneOption}>{laneOption}</option>)}
                          </select>
                        </label>
                        <button type="button" className="action-button ghost" onClick={() => onEditTask(toEditableTask(task))}>Edit task</button>
                      </motion.article>
                    ))}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </motion.section>

          <motion.section className="glass-card artifact-deck" layout>
            <div className="card-topline">
              <span className="eyebrow">Artifacts</span>
              <span className="signal-chip neutral">{activeRoom.artifact_summary.total_artifacts}</span>
            </div>
            <div className="artifact-grid">
              {activeRoom.artifacts.map((artifact) => (
                <motion.article key={artifact.id} className="artifact-card" layout>
                  <div className="lane-task-top">
                    <strong>{artifact.title}</strong>
                    <span className="signal-chip neutral">{artifact.artifact_type}</span>
                  </div>
                  <p>{artifact.summary}</p>
                  {artifact.link && <small>{artifact.link}</small>}
                  <button type="button" className="action-button ghost" onClick={() => onEditArtifact(toEditableArtifact(artifact))}>Edit artifact</button>
                </motion.article>
              ))}
            </div>
          </motion.section>
        </>
      )}
    </div>
  );
}
