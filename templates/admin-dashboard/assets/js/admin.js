/* ==========================================================================
   INFINITY ADMIN DASHBOARD — admin.js
   Reusable UI toolkit: DataTable engine (search/filter/sort/pagination/
   export), toasts, confirm dialogs, modal helper, badges, misc helpers.
   ========================================================================== */

(function () {
  'use strict';

  /* ================= HELPERS ================= */

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&').replace(/</g, '<')
      .replace(/>/g, '>').replace(/"/g, '"');
  }

  function inr(n) {
    return '₹' + Number(n || 0).toLocaleString('en-IN');
  }

  function initials(name) {
    return String(name || '?').split(' ').map(function (w) { return w[0]; }).slice(0, 2).join('').toUpperCase();
  }

  function avatarClass(id) {
    var n = 0;
    String(id).split('').forEach(function (c) { n += c.charCodeAt(0); });
    return 'av-' + ((n % 8) + 1);
  }

  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&]*)').exec(location.search);
    return m ? decodeURIComponent(m[1]) : null;
  }

  /* ================= BADGES ================= */

  var STATUS_BADGES = {
    // generic
    active: ['badge-success', 'Active'],
    inactive: ['badge-slate', 'Inactive'],
    suspended: ['badge-danger', 'Suspended'],
    blocked: ['badge-danger', 'Blocked'],
    pending: ['badge-warning', 'Pending'],
    // quick services / jobs
    open: ['badge-info', 'Open'],
    'in-progress': ['badge-warning', 'In Progress'],
    completed: ['badge-success', 'Completed'],
    cancelled: ['badge-danger', 'Cancelled'],
    assigned: ['badge-purple', 'Assigned'],
    // bids
    submitted: ['badge-info', 'Submitted'],
    selected: ['badge-success', 'Selected'],
    rejected: ['badge-danger', 'Rejected'],
    withdrawn: ['badge-slate', 'Withdrawn'],
    // payments
    success: ['badge-success', 'Success'],
    failed: ['badge-danger', 'Failed'],
    refunded: ['badge-purple', 'Refunded'],
    // complaints
    'in-review': ['badge-warning', 'In Review'],
    'waiting-response': ['badge-info', 'Waiting for Response'],
    resolved: ['badge-success', 'Resolved'],
    closed: ['badge-slate', 'Closed'],
    // reviews
    published: ['badge-success', 'Published'],
    hidden: ['badge-slate', 'Hidden'],
    flagged: ['badge-danger', 'Flagged'],
    // credits
    purchased: ['badge-success', 'Purchased'],
    'bid-used': ['badge-warning', 'Bid Used'],
    'withdrawn-bid': ['badge-slate', 'Withdrawn Bid'],
    'rejected-bid': ['badge-danger', 'Rejected Bid'],
    // priority
    high: ['badge-danger', 'High'],
    medium: ['badge-warning', 'Medium'],
    low: ['badge-info', 'Low'],
    // vendor type
    company: ['badge-purple', 'Company'],
    outsider: ['badge-teal', 'Outsider']
  };

  function badge(status, labelOverride) {
    var key = String(status || '').toLowerCase();
    var cfg = STATUS_BADGES[key] || ['badge-slate', status];
    return '<span class="badge ' + cfg[0] + '"><span class="dot"></span>' + esc(labelOverride || cfg[1]) + '</span>';
  }

  function stars(rating) {
    var r = Math.round(Number(rating) || 0);
    var html = '<span class="stars">';
    for (var i = 1; i <= 5; i++) {
      html += i <= r ? '★' : '<span class="dim">★</span>';
    }
    html += '</span> <span class="text-muted" style="font-size:12px;">' + Number(rating || 0).toFixed(1) + '</span>';
    return html;
  }

  function userCell(name, sub, id) {
    return '<div class="cell-user"><span class="avatar ' + avatarClass(id || name) + '">' + esc(initials(name)) + '</span>' +
      '<div><div class="u-name">' + esc(name) + '</div>' + (sub ? '<div class="u-sub">' + esc(sub) + '</div>' : '') + '</div></div>';
  }

  /* ================= TOASTS ================= */

  function ensureToastContainer() {
    var c = document.querySelector('.toast-container');
    if (!c) {
      c = document.createElement('div');
      c.className = 'toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  var TOAST_ICONS = {
    success: 'fa-circle-check',
    error: 'fa-circle-xmark',
    warning: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  function toast(type, title, msg, duration) {
    var c = ensureToastContainer();
    var el = document.createElement('div');
    el.className = 'app-toast ' + (type || 'info');
    el.innerHTML =
      '<span class="t-icon"><i class="fa-solid ' + (TOAST_ICONS[type] || TOAST_ICONS.info) + '"></i></span>' +
      '<div class="t-body"><div class="t-title">' + esc(title) + '</div>' + (msg ? '<div class="t-msg">' + esc(msg) + '</div>' : '') + '</div>' +
      '<button class="t-close" aria-label="Close"><i class="fa-solid fa-xmark"></i></button>';
    c.appendChild(el);
    var timer = setTimeout(remove, duration || 3500);
    function remove() {
      clearTimeout(timer);
      el.style.opacity = '0';
      el.style.transform = 'translateX(24px)';
      el.style.transition = 'all .3s ease';
      setTimeout(function () { el.remove(); }, 300);
    }
    el.querySelector('.t-close').addEventListener('click', remove);
  }

  /* ================= CONFIRM DIALOG ================= */

  function confirmDialog(opts) {
    opts = opts || {};
    var backdrop = document.createElement('div');
    backdrop.className = 'modal fade show';
    backdrop.style.display = 'block';
    backdrop.style.backgroundColor = 'rgba(15,23,42,.55)';
    backdrop.innerHTML =
      '<div class="modal-dialog modal-dialog-centered modal-sm">' +
      '  <div class="modal-content">' +
      '    <div class="modal-body" style="text-align:center;padding:28px 24px 20px;">' +
      '      <div style="width:56px;height:56px;border-radius:50%;margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-size:22px;' +
      (opts.danger ? 'background:var(--danger-soft);color:var(--danger);' : 'background:var(--primary-soft);color:var(--primary);') + '">' +
      '        <i class="fa-solid ' + (opts.icon || (opts.danger ? 'fa-trash-can' : 'fa-circle-question')) + '"></i>' +
      '      </div>' +
      '      <h5 style="font-weight:700;margin-bottom:6px;">' + esc(opts.title || 'Are you sure?') + '</h5>' +
      '      <p style="font-size:13px;color:var(--text-muted);margin:0;">' + esc(opts.message || '') + '</p>' +
      '    </div>' +
      '    <div class="modal-footer" style="justify-content:center;border:none;padding-top:0;">' +
      '      <button class="btn btn-outline btn-sm" data-act="cancel">' + esc(opts.cancelText || 'Cancel') + '</button>' +
      '      <button class="btn ' + (opts.danger ? 'btn-danger' : 'btn-primary') + ' btn-sm" data-act="ok">' + esc(opts.confirmText || 'Confirm') + '</button>' +
      '    </div>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(backdrop);
    document.body.style.overflow = 'hidden';

    function close() {
      backdrop.remove();
      document.body.style.overflow = '';
    }
    backdrop.addEventListener('click', function (e) {
      if (e.target === backdrop) close();
      var act = e.target.closest('[data-act]');
      if (!act) return;
      if (act.getAttribute('data-act') === 'ok') {
        close();
        if (opts.onConfirm) opts.onConfirm();
      } else {
        close();
        if (opts.onCancel) opts.onCancel();
      }
    });
  }

  /* ================= MODAL HELPER ================= */

  function openModal(opts) {
    opts = opts || {};
    var backdrop = document.createElement('div');
    backdrop.className = 'modal fade show';
    backdrop.style.display = 'block';
    backdrop.style.backgroundColor = 'rgba(15,23,42,.55)';
    backdrop.innerHTML =
      '<div class="modal-dialog modal-dialog-centered ' + (opts.size || '') + '">' +
      '  <div class="modal-content">' +
      '    <div class="modal-header"><h5 class="modal-title">' + esc(opts.title || '') + '</h5>' +
      '      <button type="button" class="btn-close" data-act="close" aria-label="Close"></button></div>' +
      '    <div class="modal-body">' + (opts.body || '') + '</div>' +
      (opts.footer === false ? '' :
        '    <div class="modal-footer">' +
        '      <button class="btn btn-outline btn-sm" data-act="close">' + esc(opts.cancelText || 'Cancel') + '</button>' +
        '      <button class="btn btn-primary btn-sm" data-act="save">' + esc(opts.saveText || 'Save') + '</button>' +
        '    </div>') +
      '  </div>' +
      '</div>';
    document.body.appendChild(backdrop);
    document.body.style.overflow = 'hidden';

    function close() {
      backdrop.remove();
      document.body.style.overflow = '';
      if (opts.onClose) opts.onClose();
    }
    backdrop.addEventListener('click', function (e) {
      if (e.target === backdrop) close();
      var act = e.target.closest('[data-act]');
      if (!act) return;
      if (act.getAttribute('data-act') === 'save') {
        if (opts.onSave) {
          var keepOpen = opts.onSave(backdrop);
          if (keepOpen === true) return;
        }
        close();
      } else {
        close();
      }
    });
    return backdrop;
  }

  /* ================= DATA TABLE ENGINE ================= */
  /*
   * AdminUI.createTable({
   *   mount: '#tableMount',
   *   columns: [{ key, label, sortable, render(row), sortVal(row), csv }],
   *   data: [...],
   *   searchKeys: ['name','email'],
   *   filters: [{ key, selector: '#statusFilter', match(row, value) }],
   *   pageSize: 10,
   *   emptyTitle, emptyText,
   *   onRowClick(row)
   * })
   */
  function createTable(cfg) {
    var mount = typeof cfg.mount === 'string' ? document.querySelector(cfg.mount) : cfg.mount;
    if (!mount) return null;

    var state = {
      rows: (cfg.data || []).slice(),
      filtered: [],
      page: 1,
      pageSize: cfg.pageSize || 10,
      search: '',
      sortKey: cfg.sortKey || null,
      sortDir: cfg.sortDir || 'desc',
      filterVals: {}
    };

    // Pre-read URL status filter if configured
    if (cfg.urlStatusFilter) {
      var urlStatus = qs('status');
      if (urlStatus) state.filterVals[cfg.urlStatusFilter] = urlStatus;
    }

    function applyFilters() {
      var rows = state.rows;

      if (state.search) {
        var q = state.search.toLowerCase();
        rows = rows.filter(function (r) {
          return (cfg.searchKeys || []).some(function (k) {
            return String(r[k] == null ? '' : r[k]).toLowerCase().indexOf(q) !== -1;
          });
        });
      }

      (cfg.filters || []).forEach(function (f) {
        var v = state.filterVals[f.key];
        if (v && v !== 'all') {
          rows = rows.filter(function (r) { return f.match(r, v); });
        }
      });

      if (state.sortKey) {
        var col = cfg.columns.find(function (c) { return c.key === state.sortKey; });
        if (col) {
          rows = rows.slice().sort(function (a, b) {
            var av = col.sortVal ? col.sortVal(a) : a[col.key];
            var bv = col.sortVal ? col.sortVal(b) : b[col.key];
            if (av == null) av = '';
            if (bv == null) bv = '';
            if (typeof av === 'string') av = av.toLowerCase();
            if (typeof bv === 'string') bv = bv.toLowerCase();
            var r = av < bv ? -1 : av > bv ? 1 : 0;
            return state.sortDir === 'asc' ? r : -r;
          });
        }
      }
      state.filtered = rows;
    }

    function render() {
      applyFilters();
      var total = state.filtered.length;
      var pages = Math.max(1, Math.ceil(total / state.pageSize));
      if (state.page > pages) state.page = pages;
      var start = (state.page - 1) * state.pageSize;
      var pageRows = state.filtered.slice(start, start + state.pageSize);

      var html = '';

      // Toolbar
      if (cfg.searchKeys || cfg.toolbarExtra) {
        html += '<div class="table-toolbar">';
        if (cfg.searchKeys) {
          html += '<div class="tt-search"><i class="fa-solid fa-magnifying-glass"></i>' +
            '<input type="text" placeholder="' + esc(cfg.searchPlaceholder || 'Search…') + '" data-tt="search" value="' + esc(state.search) + '"></div>';
        }
        html += '<div class="tt-filters">';
        (cfg.filters || []).forEach(function (f) {
          var val = state.filterVals[f.key] || 'all';
          html += '<select class="form-select form-select-sm" data-tt="filter" data-key="' + f.key + '" style="width:auto;">';
          f.options.forEach(function (o) {
            html += '<option value="' + esc(o.value) + '"' + (o.value === val ? ' selected' : '') + '>' + esc(o.label) + '</option>';
          });
          html += '</select>';
        });
        if (cfg.exportable !== false) {
          html += '<button class="btn btn-outline btn-sm" data-tt="export"><i class="fa-solid fa-file-export"></i> Export</button>';
        }
        html += '</div></div>';
      }

      // Body
      if (total === 0) {
        html += '<div class="state-box">' +
          '<div class="state-icon"><i class="fa-regular fa-folder-open"></i></div>' +
          '<h5>' + esc(cfg.emptyTitle || 'No records found') + '</h5>' +
          '<p>' + esc(cfg.emptyText || 'Try adjusting your search or filters.') + '</p>' +
          '<button class="btn btn-soft btn-sm" data-tt="reset"><i class="fa-solid fa-rotate-left"></i> Reset filters</button>' +
          '</div>';
      } else {
        html += '<div class="table-wrap"><table class="table"><thead><tr>';
        cfg.columns.forEach(function (c) {
          var arrow = '';
          if (c.sortable && state.sortKey === c.key) {
            arrow = ' <i class="fa-solid fa-arrow-' + (state.sortDir === 'asc' ? 'up' : 'down') + '" style="font-size:9px;"></i>';
          }
          html += '<th' + (c.sortable ? ' data-tt="sort" data-key="' + c.key + '" style="cursor:pointer;"' : '') + '>' + esc(c.label) + arrow + '</th>';
        });
        html += '</tr></thead><tbody>';
        pageRows.forEach(function (row, ri) {
          html += '<tr data-idx="' + (start + ri) + '"' + (cfg.onRowClick ? ' style="cursor:pointer;"' : '') + '>';
          cfg.columns.forEach(function (c) {
            html += '<td>' + (c.render ? c.render(row) : esc(row[c.key])) + '</td>';
          });
          html += '</tr>';
        });
        html += '</tbody></table></div>';

        // Footer / pagination
        html += '<div class="table-footer">';
        html += '<div class="tf-info">Showing ' + (start + 1) + '–' + Math.min(start + state.pageSize, total) + ' of ' + total + ' records</div>';
        html += '<div class="pagination">';
        html += '<span class="' + (state.page === 1 ? 'disabled' : '') + '"><span class="page-link" data-tt="page" data-page="' + (state.page - 1) + '"><i class="fa-solid fa-chevron-left" style="font-size:10px;"></i></span></span>';
        var from = Math.max(1, state.page - 2);
        var to = Math.min(pages, from + 4);
        from = Math.max(1, to - 4);
        for (var p = from; p <= to; p++) {
          html += '<span class="' + (p === state.page ? 'active' : '') + '"><span class="page-link" data-tt="page" data-page="' + p + '">' + p + '</span></span>';
        }
        html += '<span class="' + (state.page === pages ? 'disabled' : '') + '"><span class="page-link" data-tt="page" data-page="' + (state.page + 1) + '"><i class="fa-solid fa-chevron-right" style="font-size:10px;"></i></span></span>';
        html += '</div></div>';
      }

      mount.innerHTML = html;
      bind();
      if (cfg.onRendered) cfg.onRendered(state.filtered);
    }

    function bind() {
      mount.querySelectorAll('[data-tt="search"]').forEach(function (inp) {
        inp.addEventListener('input', function () {
          state.search = inp.value;
          state.page = 1;
          render();
          // keep focus
          var ni = mount.querySelector('[data-tt="search"]');
          if (ni) { ni.focus(); ni.setSelectionRange(ni.value.length, ni.value.length); }
        });
      });
      mount.querySelectorAll('[data-tt="filter"]').forEach(function (sel) {
        sel.addEventListener('change', function () {
          state.filterVals[sel.getAttribute('data-key')] = sel.value;
          state.page = 1;
          render();
        });
      });
      mount.querySelectorAll('[data-tt="sort"]').forEach(function (th) {
        th.addEventListener('click', function () {
          var k = th.getAttribute('data-key');
          if (state.sortKey === k) {
            state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
          } else {
            state.sortKey = k;
            state.sortDir = 'asc';
          }
          render();
        });
      });
      mount.querySelectorAll('[data-tt="page"]').forEach(function (pg) {
        pg.addEventListener('click', function () {
          state.page = parseInt(pg.getAttribute('data-page'), 10);
          render();
        });
      });
      var resetBtn = mount.querySelector('[data-tt="reset"]');
      if (resetBtn) resetBtn.addEventListener('click', function () {
        state.search = '';
        state.filterVals = {};
        state.page = 1;
        render();
      });
      var expBtn = mount.querySelector('[data-tt="export"]');
      if (expBtn) expBtn.addEventListener('click', exportCsv);
      if (cfg.onRowClick) {
        mount.querySelectorAll('tbody tr').forEach(function (tr) {
          tr.addEventListener('click', function (e) {
            if (e.target.closest('button, a, .action-btn')) return;
            cfg.onRowClick(state.filtered[parseInt(tr.getAttribute('data-idx'), 10)]);
          });
        });
      }
      (cfg.rowActions || []).forEach(function () { /* handled via render callbacks */ });
      mount.querySelectorAll('[data-action]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
          e.stopPropagation();
          var idx = parseInt(btn.closest('tr').getAttribute('data-idx'), 10);
          var row = state.filtered[idx];
          var act = btn.getAttribute('data-action');
          if (cfg.onAction) cfg.onAction(act, row, btn);
        });
      });
    }

    function exportCsv() {
      var cols = cfg.columns.filter(function (c) { return c.csv !== false; });
      var lines = [cols.map(function (c) { return '"' + esc(c.label) + '"'; }).join(',')];
      state.filtered.forEach(function (row) {
        lines.push(cols.map(function (c) {
          var v = c.csvVal ? c.csvVal(row) : (c.render ? String(row[c.key] == null ? '' : row[c.key]) : String(row[c.key] == null ? '' : row[c.key]));
          return '"' + String(v).replace(/"/g, '""') + '"';
        }).join(','));
      });
      var blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = (cfg.exportName || 'export') + '.csv';
      a.click();
      URL.revokeObjectURL(a.href);
      toast('success', 'Export complete', (cfg.exportName || 'Data') + '.csv downloaded.');
    }

    render();

    return {
      refresh: render,
      setRows: function (rows) { state.rows = rows; state.page = 1; render(); },
      getFiltered: function () { return state.filtered; }
    };
  }

  /* ================= ACTION BUTTONS ================= */

  function actionBtns(list) {
    var html = '<div class="action-group">';
    list.forEach(function (a) {
      html += '<button class="action-btn ' + (a.cls || 'view') + '" data-action="' + esc(a.action) + '" title="' + esc(a.title || '') + '">' +
        '<i class="fa-solid ' + esc(a.icon) + '"></i></button>';
    });
    html += '</div>';
    return html;
  }

  /* ================= PAGE LOADING SIMULATION ================= */

  function simulateLoad(container, done) {
    var el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) { if (done) done(); return; }
    el.innerHTML = '<div class="state-box"><div class="spinner"></div><p>Loading data…</p></div>';
    setTimeout(function () { if (done) done(); }, 350);
  }

  /* ================= EXPOSE ================= */

  window.AdminUI = {
    esc: esc,
    inr: inr,
    initials: initials,
    avatarClass: avatarClass,
    qs: qs,
    badge: badge,
    stars: stars,
    userCell: userCell,
    toast: toast,
    confirm: confirmDialog,
    modal: openModal,
    createTable: createTable,
    actionBtns: actionBtns,
    simulateLoad: simulateLoad
  };
})();