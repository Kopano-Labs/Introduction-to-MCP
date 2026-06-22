/* ═══════════════════════════════════════════════════════════════
   CrisisConnect — Adaptive Runtime Engine
   6 Dimensions: Connectivity, Role, Urgency, Device, Trust, Local
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── State ──────────────────────────────────────────────── */
  const state = {
    role: 'citizen',
    urgency: 'normal',
    connectivity: 'online',
    lastSync: new Date(),
    offlineQueue: [],
    incidents: [],
    deviceClass: 'unknown',
    networkType: 'unknown'
  };

  /* ── Demo Incidents ─────────────────────────────────────── */
  const DEMO_INCIDENTS = [
    { id: 'INC-001', type: 'flood', severity: 'critical', title: 'Flash flooding — N2 underpass Khayelitsha', location: 'Khayelitsha, Cape Town', time: '12 min ago', trust: 'verified', description: 'Multiple reports of rising water levels blocking the N2 underpass.' },
    { id: 'INC-002', type: 'power', severity: 'high', title: 'Stage 6 load shedding — Mitchells Plain grid failure', location: 'Mitchells Plain', time: '34 min ago', trust: 'verified', description: 'Extended outage beyond scheduled slot. Generator fuel running low at clinic.' },
    { id: 'INC-003', type: 'medical', severity: 'critical', title: 'Mass casualty — taxi accident R300', location: 'R300, Delft', time: '48 min ago', trust: 'unverified', description: 'Reports of multi-vehicle accident. Unconfirmed casualty count.' },
    { id: 'INC-004', type: 'water', severity: 'medium', title: 'Water main burst — Langa', location: 'Langa, Cape Town', time: '1h ago', trust: 'verified', description: 'Municipal water main burst, affecting 500+ households.' },
    { id: 'INC-005', type: 'fire', severity: 'high', title: 'Informal settlement fire — Dunoon', location: 'Dunoon, Milnerton', time: '2h ago', trust: 'verified', description: 'Structure fire spreading in dense informal area. Wind conditions worsening.' },
    { id: 'INC-006', type: 'infrastructure', severity: 'low', title: 'Road closure — maintenance M5', location: 'M5, Grassy Park', time: '3h ago', trust: 'stale', description: 'Scheduled maintenance. Last updated 3 hours ago.' },
    { id: 'INC-007', type: 'gbv', severity: 'critical', title: 'GBV shelter capacity alert', location: 'Gugulethu', time: '4h ago', trust: 'verified', description: 'Primary shelter at 98% capacity. Overflow protocol activated.' },
    { id: 'INC-008', type: 'civil_unrest', severity: 'medium', title: 'Service delivery protest — Nyanga', location: 'Nyanga East', time: '5h ago', trust: 'disputed', description: 'Conflicting reports on protest size and road closures.' }
  ];
  state.incidents = DEMO_INCIDENTS;

  /* ── DOM References ─────────────────────────────────────── */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  /* ── 1. Service Worker Registration ─────────────────────── */
  function registerSW() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => {
          console.log('[CC] Service Worker registered:', reg.scope);
          // Listen for sync messages
          navigator.serviceWorker.addEventListener('message', (event) => {
            if (event.data.type === 'SYNC_COMPLETE') {
              toast('Offline queue synced successfully', 'success');
              state.lastSync = new Date();
              updateSyncDisplay();
            }
          });
        })
        .catch(err => console.warn('[CC] SW registration failed:', err));
    }
  }

  /* ── 2. Connectivity Adaptation ─────────────────────────── */
  function initConnectivity() {
    function updateStatus() {
      const online = navigator.onLine;
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

      if (!online) {
        state.connectivity = 'offline';
      } else if (conn && (conn.effectiveType === 'slow-2g' || conn.effectiveType === '2g' || conn.saveData)) {
        state.connectivity = 'degraded';
      } else {
        state.connectivity = 'online';
      }

      // Update UI
      const badge = $('#connectionBadge');
      const label = $('#connectionLabel');
      badge.setAttribute('data-status', state.connectivity);

      const labels = { online: 'Online', degraded: 'Degraded', offline: 'Offline' };
      label.textContent = labels[state.connectivity];

      // Body class for CSS hooks
      document.body.classList.toggle('is-offline', state.connectivity === 'offline');
      document.body.classList.toggle('is-degraded', state.connectivity === 'degraded');

      // Show/hide queue banner
      updateQueueBanner();
    }

    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    if (navigator.connection) {
      navigator.connection.addEventListener('change', updateStatus);
    }
    updateStatus();
  }

  /* ── 3. Role Adaptation ─────────────────────────────────── */
  function initRoleSelector() {
    const current = $('#roleCurrent');
    const dropdown = $('#roleDropdown');
    const options = $$('.role-option');

    current.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.toggle('open');
      current.setAttribute('aria-expanded', isOpen);
    });

    options.forEach(opt => {
      opt.addEventListener('click', () => {
        const role = opt.dataset.role;
        const icon = opt.dataset.icon;
        setRole(role, icon, opt.textContent.trim());
        dropdown.classList.remove('open');
        current.setAttribute('aria-expanded', 'false');
      });
    });

    document.addEventListener('click', () => {
      dropdown.classList.remove('open');
      current.setAttribute('aria-expanded', 'false');
    });
  }

  function setRole(role, icon, label) {
    state.role = role;
    document.documentElement.setAttribute('data-role', role);
    $('#roleIcon').textContent = icon;
    $('#roleLabel').textContent = label.split(' ').slice(1).join(' ') || label;

    // Update active state
    $$('.role-option').forEach(o => o.classList.toggle('active', o.dataset.role === role));

    // Role-specific nav adjustments
    updateNavForRole(role);
    toast(`Role switched to ${label}`, 'info');
  }

  function updateNavForRole(role) {
    // All roles see dashboard and incidents
    // Role-specific visibility could be expanded here
    const navItems = {
      citizen: ['dashboard', 'incidents', 'report', 'map', 'adaptation', 'ecosystem'],
      operator: ['dashboard', 'incidents', 'report', 'map', 'queue', 'adaptation', 'ecosystem'],
      responder: ['dashboard', 'incidents', 'map', 'queue', 'adaptation', 'ecosystem'],
      command: ['dashboard', 'incidents', 'map', 'adaptation', 'queue', 'ecosystem']
    };

    $$('.nav-item[data-view]').forEach(item => {
      const view = item.dataset.view;
      const visible = navItems[role]?.includes(view) ?? true;
      item.style.display = visible ? '' : 'none';
    });
  }

  /* ── 4. Urgency Adaptation ──────────────────────────────── */
  function initUrgencySelector() {
    $$('.urgency-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const urgency = btn.dataset.urgency;
        setUrgency(urgency);
      });
    });
  }

  function setUrgency(urgency) {
    state.urgency = urgency;
    document.documentElement.setAttribute('data-urgency', urgency);

    $$('.urgency-btn').forEach(b => {
      const isActive = b.dataset.urgency === urgency;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-checked', isActive);
    });

    const labels = { normal: 'Normal operations', active: 'Active incident mode', mass: 'Mass incident mode' };
    toast(labels[urgency], urgency === 'mass' ? 'error' : urgency === 'active' ? 'warning' : 'success');
  }

  /* ── 5. Device Adaptation ───────────────────────────────── */
  function detectDevice() {
    const ua = navigator.userAgent;
    const width = window.innerWidth;
    let deviceClass = 'desktop';

    if (width <= 640) deviceClass = 'mobile';
    else if (width <= 1024) deviceClass = 'tablet';

    // Cheap device detection heuristic
    const memory = navigator.deviceMemory;
    const cores = navigator.hardwareConcurrency;
    if (memory && memory <= 2) deviceClass += ' (low-end)';
    else if (memory && memory >= 8) deviceClass += ' (high-end)';

    state.deviceClass = deviceClass;
    $('#deviceClass').textContent = deviceClass;

    // Network type
    const conn = navigator.connection;
    if (conn) {
      state.networkType = `${conn.effectiveType || 'unknown'} (${conn.downlink || '?'} Mbps)`;
      $('#networkType').textContent = state.networkType;
    } else {
      $('#networkType').textContent = navigator.onLine ? 'online' : 'offline';
    }

    // Battery
    if ('getBattery' in navigator) {
      navigator.getBattery().then(battery => {
        const level = Math.round(battery.level * 100);
        const charging = battery.charging ? ' ⚡' : '';
        $('#batteryLevel').textContent = `${level}%${charging}`;

        battery.addEventListener('levelchange', () => {
          const l = Math.round(battery.level * 100);
          const c = battery.charging ? ' ⚡' : '';
          $('#batteryLevel').textContent = `${l}%${c}`;
        });
      });
    }

    // Cache estimate
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      navigator.storage.estimate().then(est => {
        const used = (est.usage / 1024 / 1024).toFixed(1);
        const total = (est.quota / 1024 / 1024).toFixed(0);
        $('#cacheSize').textContent = `${used} / ${total} MB`;
      });
    }
  }

  /* ── 6. Navigation ──────────────────────────────────────── */
  function initNavigation() {
    $$('.nav-item[data-view]').forEach(item => {
      item.addEventListener('click', () => {
        const view = item.dataset.view;
        showView(view);

        // Update active nav
        $$('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        // Close mobile sidebar
        $('#appSidebar').classList.remove('open');
        $('#sidebarOverlay').classList.remove('visible');
      });
    });

    // Mobile menu toggle
    $('#menuToggle').addEventListener('click', () => {
      $('#appSidebar').classList.toggle('open');
      $('#sidebarOverlay').classList.toggle('visible');
    });

    $('#sidebarOverlay').addEventListener('click', () => {
      $('#appSidebar').classList.remove('open');
      $('#sidebarOverlay').classList.remove('visible');
    });
  }

  function showView(viewName) {
    $$('.view-container').forEach(v => v.classList.remove('active'));
    const target = $(`#view${viewName.charAt(0).toUpperCase() + viewName.slice(1)}`);
    if (target) target.classList.add('active');
  }

  /* ── 7. Incident Rendering ──────────────────────────────── */
  function renderIncidents() {
    const html = state.incidents.map(inc => `
      <div class="incident-item" data-id="${inc.id}">
        <div class="incident-severity ${inc.severity}"></div>
        <div class="incident-info">
          <h4>${inc.title}</h4>
          <p>${inc.location} · ${inc.id}</p>
        </div>
        <span class="trust-badge ${inc.trust}">${inc.trust}</span>
        <span class="incident-time">${inc.time}</span>
      </div>
    `).join('');

    const dashList = $('#incidentList');
    const fullList = $('#fullIncidentList');
    if (dashList) dashList.innerHTML = html;
    if (fullList) fullList.innerHTML = html;

    // Update timestamp
    const ts = new Date().toLocaleTimeString();
    const tsEl = $('#incidentListTime');
    if (tsEl) tsEl.textContent = ts;
    const dts = $('#dashboardTimestamp');
    if (dts) dts.textContent = ts;
  }

  /* ── 8. Adaptation Status Cards ─────────────────────────── */
  function renderAdaptationStatus() {
    const conn = navigator.connection;
    const dimensions = [
      {
        dimension: '1. Connectivity',
        status: state.connectivity === 'online' ? '🟢 Online — Live Mode' : state.connectivity === 'degraded' ? '🟡 Degraded — Text-first UI' : '🔴 Offline — Field Mode',
        detail: conn ? `${conn.effectiveType} · ${conn.downlink} Mbps · RTT ${conn.rtt}ms` : `navigator.onLine: ${navigator.onLine}`
      },
      {
        dimension: '2. Role',
        status: `Active: ${state.role.charAt(0).toUpperCase() + state.role.slice(1)}`,
        detail: `UI composition adapted · nav filtered · data density adjusted`
      },
      {
        dimension: '3. Urgency',
        status: state.urgency === 'normal' ? '🟢 Normal — Full dashboard' : state.urgency === 'active' ? '🟡 Active — Compressed UI' : '🔴 Mass — Stress mode',
        detail: `Button size: ${state.urgency === 'mass' ? '56px+' : state.urgency === 'active' ? '48px' : '40px'} · Decision friction: ${state.urgency === 'mass' ? 'minimal' : 'standard'}`
      },
      {
        dimension: '4. Device',
        status: `${state.deviceClass}`,
        detail: `Memory: ${navigator.deviceMemory || '?'}GB · Cores: ${navigator.hardwareConcurrency || '?'} · Width: ${window.innerWidth}px`
      },
      {
        dimension: '5. Trust',
        status: `${state.incidents.filter(i => i.trust === 'verified').length} verified · ${state.incidents.filter(i => i.trust === 'unverified').length} unverified · ${state.incidents.filter(i => i.trust === 'disputed').length} disputed`,
        detail: `Chain-of-custody: enabled · Stale threshold: 30min · Duplicate detection: active`
      },
      {
        dimension: '6. Local Context',
        status: 'Region: Western Cape, ZA',
        detail: `Language: en-ZA · Hazard profile: flood/fire/gbv · Protocol set: SAPS+EMS+metro · Network cost: medium`
      }
    ];

    const grid = $('#adaptationGrid');
    if (!grid) return;

    grid.innerHTML = dimensions.map(d => `
      <div class="adaptation-card">
        <div class="adaptation-dimension">${d.dimension}</div>
        <div class="adaptation-status">${d.status}</div>
        <div class="adaptation-detail">${d.detail}</div>
      </div>
    `).join('');
  }

  /* ── 9. Report Form ─────────────────────────────────────── */
  function initReportForm() {
    const form = $('#reportForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const report = {
        id: `INC-${String(state.incidents.length + 1).padStart(3, '0')}`,
        type: $('#incidentType').value,
        severity: $('#incidentSeverity').value,
        title: `${$('#incidentType').selectedOptions[0]?.text || 'Report'} — ${$('#incidentLocation').value}`,
        location: $('#incidentLocation').value,
        description: $('#incidentDescription').value,
        contact: $('#reporterContact').value,
        time: 'just now',
        trust: 'unverified',
        timestamp: new Date().toISOString(),
        synced: navigator.onLine
      };

      if (navigator.onLine) {
        // Simulate API call
        state.incidents.unshift(report);
        renderIncidents();
        toast('Incident reported successfully', 'success');
      } else {
        // Queue for offline sync
        state.offlineQueue.push(report);
        state.incidents.unshift(report);
        updateQueueBanner();
        renderIncidents();
        toast('Report queued — will sync when online', 'warning');

        // Try background sync
        if ('serviceWorker' in navigator && 'SyncManager' in window) {
          navigator.serviceWorker.ready.then(reg => reg.sync.register('cc-offline-queue'));
        }
      }

      form.reset();
      // Update stats
      updateStats();
    });
  }

  /* ── 10. Offline Queue ──────────────────────────────────── */
  function updateQueueBanner() {
    const banner = $('#offlineQueueBanner');
    const count = state.offlineQueue.length;
    const queueCount = $('#queueCount');
    const queueBadge = $('#queueBadge');
    const statQueued = $('#statQueued');

    if (count > 0) {
      banner.classList.add('visible');
      queueCount.textContent = count;
      queueBadge.textContent = count;
      queueBadge.classList.remove('hidden');
    } else {
      banner.classList.remove('visible');
      queueBadge.classList.add('hidden');
    }

    if (statQueued) statQueued.textContent = count;
  }

  /* ── 11. Stats Update ───────────────────────────────────── */
  function updateStats() {
    const critical = state.incidents.filter(i => i.severity === 'critical').length;
    const high = state.incidents.filter(i => i.severity === 'high').length;
    const pending = state.incidents.filter(i => i.severity === 'medium' || i.severity === 'high').length;

    $('#statActive').textContent = critical;
    $('#statPending').textContent = pending;
    $('#metricCritical').textContent = critical;
    $('#incidentBadge').textContent = critical + high;
  }

  /* ── 12. Sync Display ───────────────────────────────────── */
  function updateSyncDisplay() {
    const el = $('#lastSync');
    if (!el) return;

    function update() {
      const diff = Math.floor((Date.now() - state.lastSync.getTime()) / 1000);
      if (diff < 10) el.textContent = 'just now';
      else if (diff < 60) el.textContent = `${diff}s ago`;
      else if (diff < 3600) el.textContent = `${Math.floor(diff / 60)}m ago`;
      else el.textContent = `${Math.floor(diff / 3600)}h ago`;

      // Stale warning
      if (diff > 1800) {
        el.classList.add('stale-warning');
        el.textContent += ' ⚠️';
      } else {
        el.classList.remove('stale-warning');
      }
    }

    update();
    setInterval(update, 10000);
  }

  /* ── 13. PWA Install ────────────────────────────────────── */
  let deferredPrompt = null;

  function initInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      $('#installBanner').classList.add('visible');
    });

    const installBtn = $('#installBtn');
    if (installBtn) {
      installBtn.addEventListener('click', () => {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          deferredPrompt.userChoice.then(result => {
            if (result.outcome === 'accepted') {
              toast('CrisisConnect installed!', 'success');
            }
            deferredPrompt = null;
            $('#installBanner').classList.remove('visible');
          });
        }
      });
    }
  }

  /* ── 14. Toast Notifications ────────────────────────────── */
  function toast(message, type = 'info') {
    const container = $('#toastContainer');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);

    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(20px)';
      setTimeout(() => el.remove(), 300);
    }, 3500);
  }

  /* ── 15. Force Sync Button ──────────────────────────────── */
  function initForceSync() {
    const syncBtn = $('#forceSync');
    const syncAllBtn = $('#syncAll');

    function doSync() {
      if (state.offlineQueue.length === 0) {
        toast('Nothing to sync', 'info');
        return;
      }
      if (!navigator.onLine) {
        toast('Cannot sync — no connectivity', 'error');
        return;
      }

      // Simulate sync
      toast(`Syncing ${state.offlineQueue.length} items...`, 'info');
      setTimeout(() => {
        state.offlineQueue = [];
        state.lastSync = new Date();
        updateQueueBanner();
        updateSyncDisplay();
        toast('All items synced successfully', 'success');
      }, 1500);
    }

    if (syncBtn) syncBtn.addEventListener('click', doSync);
    if (syncAllBtn) syncAllBtn.addEventListener('click', doSync);
  }

  /* ── 16. Clock ──────────────────────────────────────────── */
  function initClock() {
    function update() {
      const dts = $('#dashboardTimestamp');
      if (dts) dts.textContent = new Date().toLocaleTimeString();
    }
    update();
    setInterval(update, 1000);
  }

  /* ── INIT ───────────────────────────────────────────────── */
  function init() {
    registerSW();
    initConnectivity();
    initRoleSelector();
    initUrgencySelector();
    detectDevice();
    initNavigation();
    renderIncidents();
    renderAdaptationStatus();
    initReportForm();
    updateQueueBanner();
    updateSyncDisplay();
    initInstallPrompt();
    initForceSync();
    initClock();
    updateStats();
    initUserMenu();  // ── USER DROP MENU ─────────────────────

    // Set initial role
    setRole('citizen', '👤', '👤 Citizen');

    console.log('[CrisisConnect] Adaptive PWA initialized');
    console.log('[CrisisConnect] 6 dimensions active: connectivity, role, urgency, device, trust, local');
    console.log('[CrisisConnect] USER DROP MENU: active | IKP: CLEAN | 360DP: VIP ####!!!!');
  }

  /* ── 17. USER DROP MENU (UMP) ───────────────────────────── */
  /*
   * USER DROP MENU — Pilot profile dropdown
   * KPGS: IKP CLEAN | 360DP VIP ####!!!! | DSO HDSO ###!!!
   * localStorage key: cc_pilot_profile
   * Stores: callsign, role, reports_count, synced_count, session_start
   * I_AM_STATELESS_RENTER_NOT_LANDLORD
   */
  const UMP_KEY       = 'cc_pilot_profile';
  const UMP_ALP_COUNT = 13;    // current ALP activation count
  const UMP_DSO       = 'HDSO ###!!!';
  const UMP_IKP       = 'IKP: CLEAN';
  const UMP_360DP     = '360DP: VIP ####!!!!';

  function loadPilot() {
    try {
      const raw = localStorage.getItem(UMP_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) { return null; }
  }

  function savePilot(profile) {
    try { localStorage.setItem(UMP_KEY, JSON.stringify(profile)); } catch (_) {}
  }

  function getInitials(callsign) {
    if (!callsign || callsign === 'Guest') return '?';
    const parts = callsign.trim().split(/[\s\-_]+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return callsign.substring(0, 2).toUpperCase();
  }

  function formatSessionTime(startIso) {
    if (!startIso) return '0m';
    const mins = Math.floor((Date.now() - new Date(startIso).getTime()) / 60000);
    if (mins < 60) return `${mins}m`;
    return `${Math.floor(mins / 60)}h${mins % 60}m`;
  }

  function umpRender(pilot) {
    const callsign = (pilot && pilot.callsign) ? pilot.callsign : 'Guest';
    const initials  = getInitials(callsign);
    const reports   = (pilot && pilot.reports_count) ? pilot.reports_count : 0;
    const synced    = (pilot && pilot.synced_count)  ? pilot.synced_count  : 0;
    const session   = (pilot && pilot.session_start) ? formatSessionTime(pilot.session_start) : '0m';
    const roleLabel = state.role.charAt(0).toUpperCase() + state.role.slice(1);

    // Trigger button
    const avatarEl    = $('#userAvatar');
    const callsignEl  = $('#userCallsign');
    if (avatarEl)   avatarEl.textContent   = initials;
    if (callsignEl) callsignEl.textContent = callsign;

    // Panel
    const nameEl    = $('#umpName');
    const roleEl    = $('#umpRole');
    const avatarLg  = $('#umpAvatarLg');
    const reports_  = $('#umpReports');
    const synced_   = $('#umpSynced');
    const session_  = $('#umpSession');
    const alpEl     = $('#umpAlpLabel');
    const ikpEl     = $('#umpIkpStatus');
    const dpEl      = $('#ump360dp');
    const dsoEl     = $('#umpDso');
    const urgEl     = $('#umpUrgencyLabel');

    if (nameEl)   nameEl.textContent  = pilot ? callsign : 'Guest Pilot';
    if (roleEl)   roleEl.textContent  = `${roleLabel} · ${navigator.onLine ? 'Online' : 'Field Mode'}`;
    if (avatarLg) avatarLg.textContent = initials;
    if (reports_) reports_.textContent = reports;
    if (synced_)  synced_.textContent  = synced;
    if (session_) session_.textContent = session;
    if (alpEl)    alpEl.textContent   = `ALP #${UMP_ALP_COUNT}`;
    if (ikpEl)    ikpEl.textContent   = UMP_IKP;
    if (dpEl)     dpEl.textContent    = UMP_360DP;
    if (dsoEl)    dsoEl.textContent   = `DSO: ${UMP_DSO}`;

    // Urgency toggle label
    const nextUrgency = { normal: 'active', active: 'mass', mass: 'normal' }[state.urgency];
    if (urgEl) urgEl.textContent = `Switch to ${nextUrgency} mode`;

    // Offline queue badge in UMP
    const qBadge = $('#umpQueueBadge');
    if (qBadge) {
      const qCount = state.offlineQueue.length;
      qBadge.textContent = qCount;
      qBadge.classList.toggle('is-hidden', qCount === 0);
    }
  }

  function umpOpen() {
    const panel   = $('#userMenuPanel');
    const trigger = $('#userMenuTrigger');
    if (!panel) return;
    umpRender(loadPilot());
    panel.classList.remove('is-hidden');
    trigger.setAttribute('aria-expanded', 'true');
  }

  function umpClose() {
    const panel   = $('#userMenuPanel');
    const trigger = $('#userMenuTrigger');
    if (!panel) return;
    panel.classList.add('is-hidden');
    trigger.setAttribute('aria-expanded', 'false');
  }

  function umpToggle() {
    const panel = $('#userMenuPanel');
    if (panel && panel.classList.contains('is-hidden')) {
      umpOpen();
    } else {
      umpClose();
    }
  }

  function initUserMenu() {
    // Ensure/bootstrap pilot profile
    let pilot = loadPilot();
    if (!pilot) {
      pilot = {
        callsign:      'Guest',
        role:          'citizen',
        reports_count: 0,
        synced_count:  0,
        session_start: new Date().toISOString(),
        kpgs_dso:      UMP_DSO,
        alp_count:     UMP_ALP_COUNT,
      };
      savePilot(pilot);
    } else {
      // Refresh session start on each boot
      pilot.session_start = new Date().toISOString();
      pilot.alp_count     = UMP_ALP_COUNT;
      savePilot(pilot);
    }

    // Render initial state into trigger button
    umpRender(pilot);

    // Toggle on trigger click
    const trigger = $('#userMenuTrigger');
    if (trigger) {
      trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        umpToggle();
      });
    }

    // Close on outside click
    document.addEventListener('click', (e) => {
      const wrap = $('#userMenuWrap');
      if (wrap && !wrap.contains(e.target)) {
        umpClose();
      }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') umpClose();
    });

    // Edit callsign
    const umpEdit = $('#umpEditProfile');
    if (umpEdit) {
      umpEdit.addEventListener('click', () => {
        umpClose();
        const modal = $('#umpCallsignModal');
        const input = $('#umpCallsignInput');
        const p     = loadPilot();
        if (input && p) input.value = p.callsign !== 'Guest' ? p.callsign : '';
        if (modal) modal.classList.remove('is-hidden');
        if (input) setTimeout(() => input.focus(), 50);
      });
    }

    // Save callsign
    const umpSave = $('#umpCallsignSave');
    if (umpSave) {
      umpSave.addEventListener('click', () => {
        const input  = $('#umpCallsignInput');
        const modal  = $('#umpCallsignModal');
        const val    = input ? input.value.trim() : '';
        if (!val) { toast('Callsign cannot be empty', 'error'); return; }
        const p = loadPilot() || {};
        p.callsign = val;
        savePilot(p);
        umpRender(p);
        if (modal) modal.classList.add('is-hidden');
        toast(`Callsign set: ${val}`, 'success');
      });
    }

    // Cancel callsign modal
    const umpCancel = $('#umpCallsignCancel');
    if (umpCancel) {
      umpCancel.addEventListener('click', () => {
        const modal = $('#umpCallsignModal');
        if (modal) modal.classList.add('is-hidden');
      });
    }

    // Enter key in callsign input → save
    const umpInput = $('#umpCallsignInput');
    if (umpInput) {
      umpInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') $('#umpCallsignSave')?.click();
      });
    }

    // View offline queue
    const umpQueue = $('#umpViewQueue');
    if (umpQueue) {
      umpQueue.addEventListener('click', () => {
        umpClose();
        showView('queue');
        $$('.nav-item').forEach(n => n.classList.remove('active'));
        $('#navQueue')?.classList.add('active');
      });
    }

    // Toggle urgency
    const umpUrgency = $('#umpToggleUrgency');
    if (umpUrgency) {
      umpUrgency.addEventListener('click', () => {
        const next = { normal: 'active', active: 'mass', mass: 'normal' }[state.urgency];
        setUrgency(next);
        umpClose();
      });
    }

    // Go to ecosystem
    const umpEco = $('#umpEcosystem');
    if (umpEco) {
      umpEco.addEventListener('click', () => {
        umpClose();
        showView('ecosystem');
        $$('.nav-item').forEach(n => n.classList.remove('active'));
        $('#navEcosystem')?.classList.add('active');
      });
    }

    // Sign out / reset pilot
    const umpOut = $('#umpSignOut');
    if (umpOut) {
      umpOut.addEventListener('click', () => {
        umpClose();
        if (!confirm('Reset all pilot data on this device? This cannot be undone.')) return;
        localStorage.removeItem(UMP_KEY);
        const fresh = {
          callsign:      'Guest',
          role:          'citizen',
          reports_count: 0,
          synced_count:  0,
          session_start: new Date().toISOString(),
          kpgs_dso:      UMP_DSO,
          alp_count:     UMP_ALP_COUNT,
        };
        savePilot(fresh);
        umpRender(fresh);
        toast('Pilot data reset. Flying as Guest.', 'info');
      });
    }

    // Hook: track reports in profile
    const reportForm = $('#reportForm');
    if (reportForm) {
      reportForm.addEventListener('submit', () => {
        const p = loadPilot() || {};
        p.reports_count = (p.reports_count || 0) + 1;
        if (navigator.onLine) p.synced_count = (p.synced_count || 0) + 1;
        savePilot(p);
        // Update session timer in panel if open
        const panel = $('#userMenuPanel');
        if (panel && !panel.classList.contains('is-hidden')) umpRender(p);
      });
    }

    // Refresh session timer every 60s
    setInterval(() => {
      const panel = $('#userMenuPanel');
      if (panel && !panel.classList.contains('is-hidden')) {
        umpRender(loadPilot());
      }
    }, 60000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

