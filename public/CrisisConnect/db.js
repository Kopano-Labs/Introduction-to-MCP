/* ═══════════════════════════════════════════════════════════════
   CrisisConnect — IndexedDB Sovereign Persistence Layer
   Real data persistence. No cloud dependency. Survives OS pressure.
   GSMB Mandate 001: Crisis data must persist.
   I_AM_STATELESS_RENTER_NOT_LANDLORD
   ═══════════════════════════════════════════════════════════════ */

const CCDB = (function () {
  'use strict';

  const DB_NAME = 'CrisisConnectDB';
  const DB_VERSION = 1;

  const STORES = {
    INCIDENTS: 'incidents',
    QUEUE:     'offline_queue',
    EVIDENCE:  'evidence_ledger'
  };

  let _db = null;

  /* ── Open / Upgrade ──────────────────────────────────────── */
  function open() {
    return new Promise((resolve, reject) => {
      if (_db) { resolve(_db); return; }

      const req = indexedDB.open(DB_NAME, DB_VERSION);

      req.onupgradeneeded = (e) => {
        const db = e.target.result;

        // Incidents store — primary data
        if (!db.objectStoreNames.contains(STORES.INCIDENTS)) {
          const incStore = db.createObjectStore(STORES.INCIDENTS, { keyPath: 'id' });
          incStore.createIndex('severity', 'severity', { unique: false });
          incStore.createIndex('type', 'type', { unique: false });
          incStore.createIndex('trust', 'trust', { unique: false });
          incStore.createIndex('timestamp', 'timestamp', { unique: false });
          incStore.createIndex('synced', 'synced', { unique: false });
        }

        // Offline queue — pending sync items
        if (!db.objectStoreNames.contains(STORES.QUEUE)) {
          const qStore = db.createObjectStore(STORES.QUEUE, { keyPath: 'id' });
          qStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Evidence ledger — CLAFP Altar bridge
        if (!db.objectStoreNames.contains(STORES.EVIDENCE)) {
          const evStore = db.createObjectStore(STORES.EVIDENCE, { keyPath: 'entry_id', autoIncrement: true });
          evStore.createIndex('incident_id', 'incident_id', { unique: false });
          evStore.createIndex('gate', 'gate', { unique: false });
          evStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        console.log('[CCDB] Schema upgraded to v' + DB_VERSION);
      };

      req.onsuccess = (e) => {
        _db = e.target.result;
        console.log('[CCDB] Database opened — sovereign persistence active');
        resolve(_db);
      };

      req.onerror = (e) => {
        console.error('[CCDB] Open failed:', e.target.error);
        reject(e.target.error);
      };
    });
  }

  /* ── Generic CRUD helpers ────────────────────────────────── */
  function _tx(storeName, mode) {
    return _db.transaction(storeName, mode).objectStore(storeName);
  }

  function _promisify(req) {
    return new Promise((resolve, reject) => {
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  /* ── Incidents ───────────────────────────────────────────── */
  async function putIncident(incident) {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readwrite');
    return _promisify(store.put(incident));
  }

  async function getIncident(id) {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readonly');
    return _promisify(store.get(id));
  }

  async function getAllIncidents() {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readonly');
    return _promisify(store.getAll());
  }

  async function deleteIncident(id) {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readwrite');
    return _promisify(store.delete(id));
  }

  async function countIncidents() {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readonly');
    return _promisify(store.count());
  }

  async function getIncidentsBySeverity(severity) {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readonly');
    const idx = store.index('severity');
    return _promisify(idx.getAll(severity));
  }

  async function getIncidentsByTrust(trust) {
    await open();
    const store = _tx(STORES.INCIDENTS, 'readonly');
    const idx = store.index('trust');
    return _promisify(idx.getAll(trust));
  }

  /* ── Offline Queue ───────────────────────────────────────── */
  async function enqueue(item) {
    await open();
    const store = _tx(STORES.QUEUE, 'readwrite');
    return _promisify(store.put(item));
  }

  async function dequeue(id) {
    await open();
    const store = _tx(STORES.QUEUE, 'readwrite');
    return _promisify(store.delete(id));
  }

  async function getQueue() {
    await open();
    const store = _tx(STORES.QUEUE, 'readonly');
    return _promisify(store.getAll());
  }

  async function clearQueue() {
    await open();
    const store = _tx(STORES.QUEUE, 'readwrite');
    return _promisify(store.clear());
  }

  async function queueSize() {
    await open();
    const store = _tx(STORES.QUEUE, 'readonly');
    return _promisify(store.count());
  }

  /* ── Evidence Ledger (CLAFP Altar Bridge) ────────────────── */
  async function logEvidence(entry) {
    await open();
    const record = {
      ...entry,
      timestamp: entry.timestamp || new Date().toISOString(),
      constraint: 'I_AM_STATELESS_RENTER_NOT_LANDLORD'
    };
    const store = _tx(STORES.EVIDENCE, 'readwrite');
    return _promisify(store.put(record));
  }

  async function getEvidenceForIncident(incidentId) {
    await open();
    const store = _tx(STORES.EVIDENCE, 'readonly');
    const idx = store.index('incident_id');
    return _promisify(idx.getAll(incidentId));
  }

  async function getAllEvidence() {
    await open();
    const store = _tx(STORES.EVIDENCE, 'readonly');
    return _promisify(store.getAll());
  }

  async function getEvidenceByGate(gate) {
    await open();
    const store = _tx(STORES.EVIDENCE, 'readonly');
    const idx = store.index('gate');
    return _promisify(idx.getAll(gate));
  }

  /* ── Seed demo data (first run only) ─────────────────────── */
  async function seedIfEmpty(demoIncidents) {
    await open();
    const count = await countIncidents();
    if (count > 0) {
      console.log('[CCDB] Data already exists (' + count + ' incidents) — skip seed');
      return false;
    }

    const tx = _db.transaction(STORES.INCIDENTS, 'readwrite');
    const store = tx.objectStore(STORES.INCIDENTS);
    for (const inc of demoIncidents) {
      store.put({
        ...inc,
        timestamp: inc.timestamp || new Date().toISOString(),
        synced: true
      });
    }

    return new Promise((resolve, reject) => {
      tx.oncomplete = () => {
        console.log('[CCDB] Seeded ' + demoIncidents.length + ' demo incidents');

        // Log evidence for seed
        demoIncidents.forEach(inc => {
          logEvidence({
            incident_id: inc.id,
            gate: 'SEED',
            action: 'DEMO_DATA_LOADED',
            verdict: 'POC',
            detail: 'Initial demo incident loaded into IndexedDB'
          });
        });

        resolve(true);
      };
      tx.onerror = () => reject(tx.error);
    });
  }

  /* ── Export (Public API) ─────────────────────────────────── */
  return {
    open,
    STORES,

    // Incidents
    putIncident,
    getIncident,
    getAllIncidents,
    deleteIncident,
    countIncidents,
    getIncidentsBySeverity,
    getIncidentsByTrust,

    // Offline queue
    enqueue,
    dequeue,
    getQueue,
    clearQueue,
    queueSize,

    // Evidence ledger
    logEvidence,
    getEvidenceForIncident,
    getAllEvidence,
    getEvidenceByGate,

    // Seed
    seedIfEmpty
  };
})();
