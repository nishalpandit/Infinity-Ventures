/* ==========================================================================
   Suggu Admin DASHBOARD — components.js
   Shared layout: injects the SAME sidebar + header into every page,
   detects active menu, renders breadcrumbs, header dropdowns.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- Path helpers (pages live at root or one level deep) ---------- */
  var SUBFOLDERS = ['users', 'quick-services', 'jobs', 'bidding', 'subscriptions', 'payments', 'reviews', 'complaints', 'reports', 'master'];

  function inSubfolder() {
    var segs = location.pathname.split('/').filter(Boolean);
    return segs.length >= 2 && SUBFOLDERS.indexOf(segs[segs.length - 2]) !== -1;
  }

  var P = inSubfolder() ? '../' : './'; // prefix for links

  function resolveHref(href) {
    if (!href) return '#';
    if (href.startsWith('/') || href.startsWith('http://') || href.startsWith('https://') || href.startsWith('#')) {
      return href;
    }
    return P + href;
  }

  function currentCanonical() {
    var segs = location.pathname.split('/').filter(Boolean);
    if (segs.length >= 2 && SUBFOLDERS.indexOf(segs[segs.length - 2]) !== -1) {
      return segs.slice(-2).join('/');
    }
    return segs[segs.length - 1] || 'dashboard.html';
  }

  function canonical(href) {
    return href.replace(/^\.\//, '').replace(/^\.\.\//, '');
  }

  function qs(name) {
    var m = new RegExp('[?&]' + name + '=([^&]*)').exec(location.search);
    return m ? decodeURIComponent(m[1]) : null;
  }

  function qsFromHref(href) {
    var i = href.indexOf('?');
    if (i === -1) return null;
    var m = /[?&](?:status|view)=([^&#]*)/.exec(href);
    return m ? m[1] : null;
  }

  function isItemActive(href) {
    var cur = currentCanonical();
    var isDash = ['admin-dashboard', 'dashboard', 'dashboard.html', 'admin-dashboard.html'].indexOf(cur) !== -1;
    var cHref = canonical(href);

    if (isDash && (cHref === 'admin-dashboard' || cHref === 'dashboard.html' || href === '/admin-dashboard')) {
      return true;
    }

    var hrefStatus = qsFromHref(href);
    var curStatus = qs('status') || (qs('view') ? qs('view') : null);

    if (cHref === cur) {
      if (hrefStatus) {
        return hrefStatus === curStatus;
      }
      return !curStatus;
    }
    return false;
  }

  /* ---------- Sidebar menu configuration ---------- */
  var MENU = [
    { label: 'Dashboard', icon: 'fa-gauge-high', href: '/admin-dashboard' },
    {
      label: 'Users', icon: 'fa-users', children: [
        { label: 'User', href: 'users/users.html' },
        { label: 'Vendor', href: 'users/vendors.html' },
        { label: 'Company Vendor', href: 'users/company-vendors.html' }
      ]
    },
    {
      label: 'Quick Services', icon: 'fa-bolt', children: [
        { label: 'Active Quick Services', href: 'quick-services/index.html#active' },
        { label: 'Closed Quick Services', href: 'quick-services/index.html#closed' }
      ]
    },
    {
      label: 'Jobs', icon: 'fa-briefcase', children: [
        { label: 'Active Jobs', href: 'jobs/index.html#active' },
        { label: 'Closed Jobs', href: 'jobs/index.html#closed' }
      ]
    },
    {
      label: 'Subscriptions', icon: 'fa-layer-group', children: [
        { label: 'Bid Packages', href: 'subscriptions/packages.html' },
        { label: 'Purchases', href: 'subscriptions/purchases.html' },
        { label: 'Credit Transactions', href: 'subscriptions/credit-transactions.html' }
      ]
    },
    { label: 'Payments', icon: 'fa-credit-card', children: [
        { label: 'Subscription Payments', href: 'payments/index.html' },
        { label: 'Transactions', href: 'payments/index.html?view=transactions' },
        { label: 'Vendor Payouts', href: '/super-admin/payouts/' }
      ]
    },
    {
      label: 'Master', icon: 'fa-database', children: [
        { label: 'Categories', href: 'master/categories.html' },
        { label: 'Locations', href: 'master/locations.html' }
      ]
    },
    { label: 'Disputes & Complaints', icon: 'fa-shield-halved', href: 'complaints/index.html' },
    { label: 'Admin Profile', icon: 'fa-user-shield', href: 'profile.html' }
  ];

  /* ---------- Sidebar template (pre-computes active/open states with ZERO flash) ---------- */
  function buildSidebar() {
    var stateLabel = window.ADMIN_STATE ? '<div style="font-size:11px; color:#818cf8; font-weight:600; padding:2px 0 0 36px;"><i class="fa-solid fa-map-pin" style="margin-right:4px;"></i>' + window.ADMIN_STATE + '</div>' : '';
    var html = '';
    html += '<aside class="app-sidebar" id="appSidebar">';
    html += '  <div class="sidebar-logo">';
    html += '    <a href="/admin-dashboard" style="display:flex;align-items:center;gap:12px;text-decoration:none;">';
    html += '      <span class="logo-mark" style="background:transparent;padding:0;display:flex;align-items:center;justify-content:center;"><img src="/static/assets/images/logo.png" alt="Suggu Services" style="width:32px;height:32px;border-radius:8px;object-fit:contain;" /></span>';
    html += '      <div><span class="logo-text">Suggu <span>Services</span></span>' + stateLabel + '</div>';
    html += '    </a>';
    html += '  </div>';
    html += '  <nav class="sidebar-nav" id="sidebarNav">';

    MENU.forEach(function (item) {
      if (item.children) {
        var hasActiveChild = item.children.some(function (c) { return isItemActive(c.href); });
        var itemClass = 'snav-item has-sub' + (hasActiveChild ? ' open' : '');
        var linkClass = 'snav-link' + (hasActiveChild ? ' parent-active' : '');

        html += '<div class="' + itemClass + '" data-menu="' + item.label + '">';
        html += '  <div class="' + linkClass + '" role="button" tabindex="0">';
        html += '    <span class="snav-icon"><i class="fa-solid ' + item.icon + '"></i></span>';
        html += '    <span class="snav-label">' + item.label + '</span>';
        html += '    <span class="snav-arrow"><i class="fa-solid fa-chevron-right"></i></span>';
        html += '  </div>';
        html += '  <div class="sb-tooltip">' + item.label + '</div>';
        html += '  <div class="sb-flyout"><div class="flyout-title">' + item.label + '</div>';
        item.children.forEach(function (c) {
          var isAct = isItemActive(c.href);
          var aClass = isAct ? ' class="active"' : '';
          html += '<a href="' + resolveHref(c.href) + '" data-canon="' + canonical(c.href) + '" data-status="' + (qsFromHref(c.href) || '') + '"' + aClass + '>' + c.label + '</a>';
        });
        html += '  </div>';
        html += '  <ul class="snav-sub">';
        item.children.forEach(function (c) {
          var isAct = isItemActive(c.href);
          var subClass = 'snav-sublink' + (isAct ? ' active' : '');
          html += '<li><a class="' + subClass + '" href="' + resolveHref(c.href) + '" data-canon="' + canonical(c.href) + '" data-status="' + (qsFromHref(c.href) || '') + '">' + c.label + '</a></li>';
        });
        html += '  </ul>';
        html += '</div>';
      } else {
        var isAct = isItemActive(item.href);
        var linkClass = 'snav-link' + (isAct ? ' active' : '');
        html += '<div class="snav-item" data-menu="' + item.label + '">';
        html += '  <a class="' + linkClass + '" href="' + resolveHref(item.href) + '" data-canon="' + canonical(item.href) + '">';
        html += '    <span class="snav-icon"><i class="fa-solid ' + item.icon + '"></i></span>';
        html += '    <span class="snav-label">' + item.label + '</span>';
        html += '  </a>';
        html += '  <div class="sb-tooltip">' + item.label + '</div>';
        html += '</div>';
      }
    });

    html += '  </nav>';
    html += '  <div class="sidebar-footer">';
    html += '    <div class="snav-item" data-menu="Logout">';
    html += '      <div class="snav-link" id="sidebarLogout" role="button" tabindex="0">';
    html += '        <span class="snav-icon"><i class="fa-solid fa-right-from-bracket"></i></span>';
    html += '        <span class="snav-label">Logout</span>';
    html += '      </div>';
    html += '      <div class="sb-tooltip">Logout</div>';
    html += '    </div>';
    html += '  </div>';
    html += '</aside>';
    html += '<div class="sidebar-overlay" id="sidebarOverlay"></div>';
    return html;
  }

  /* ---------- Header template ---------- */
  function buildHeader() {
    var uName = window.ADMIN_NAME || 'Area Admin';
    var uRole = window.ADMIN_ROLE || 'Area Admin';
    var uState = window.ADMIN_STATE ? ' (' + window.ADMIN_STATE + ')' : '';
    var uInitials = window.ADMIN_INITIALS || 'AA';
    var isSuper = uRole.indexOf('Super') !== -1;

    var html = '';
    html += '<header class="app-header">';
    html += '  <div style="display:flex;align-items:center;gap:12px;">';
    html += '    <button class="header-toggle d-lg-none" id="mobileMenuBtn" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button>';
    html += '    <button class="header-toggle d-none d-lg-inline-flex" id="sidebarToggle" aria-label="Toggle sidebar"><i class="fa-solid fa-bars-staggered"></i></button>';
    if (window.ADMIN_STATE && !isSuper) {
      html += '    <div class="d-none d-md-flex align-items-center gap-2 px-3 py-1" style="background:rgba(79,70,229,0.08);border:1px solid rgba(79,70,229,0.2);border-radius:20px;font-size:12px;color:var(--primary);font-weight:600;">';
      html += '      <i class="fa-solid fa-location-dot" style="font-size:11px;"></i> Territory: ' + window.ADMIN_STATE;
      html += '    </div>';
    } else if (isSuper) {
      html += '    <a href="/super-admin/" class="d-none d-md-inline-flex align-items-center gap-2 px-3 py-1 btn btn-sm btn-outline-primary" style="border-radius:20px;font-size:12px;font-weight:600;text-decoration:none;">';
      html += '      <i class="fa-solid fa-shield-halved"></i> Super Admin Hub';
      html += '    </a>';
    }
    html += '  </div>';
    html += '  <div class="header-actions">';
    html += '    <div style="position:relative;">';
    html += '      <button class="header-icon-btn" id="notifBtn" aria-label="Notifications"><i class="fa-regular fa-bell"></i><span class="dot"></span></button>';
    html += '      <div class="header-dropdown" id="notifDropdown">';
    html += '        <div class="hd-head"><span>Notifications</span><span class="badge badge-danger">Live</span></div>';
    html += '        <div class="hd-item"><span class="ic icon-indigo"><i class="fa-solid fa-map-pin"></i></span><div class="txt"><div class="t">Territory Active</div><div class="d">Managing area operations' + (window.ADMIN_STATE ? ' for ' + window.ADMIN_STATE : '') + '</div><div class="time">Just now</div></div></div>';
    html += '        <div class="hd-footer"><a href="' + P + 'notifications.html">View all notifications</a></div>';
    html += '      </div>';
    html += '    </div>';
    html += '    <div style="position:relative;">';
    html += '      <div class="header-profile" id="profileBtn">';
    html += '        <span class="avatar">' + uInitials + '</span>';
    html += '        <span class="meta"><span class="name d-block">' + uName + '</span><span class="role d-block">' + uRole + uState + '</span></span>';
    html += '        <i class="fa-solid fa-chevron-down" style="font-size:10px;color:var(--text-light);"></i>';
    html += '      </div>';
    html += '      <div class="header-dropdown profile-menu" id="profileDropdown">';
    if (isSuper) {
      html += '        <a class="pm-item" href="/super-admin/"><i class="fa-solid fa-shield-halved"></i> Super Admin Hub</a>';
    }
    html += '        <a class="pm-item" href="' + P + 'profile.html"><i class="fa-regular fa-user"></i> My Profile</a>';
    html += '        <a class="pm-item" href="' + P + 'notifications.html"><i class="fa-regular fa-bell"></i> Notifications</a>';
    html += '        <div class="pm-divider"></div>';
    html += '        <div class="pm-item danger" id="headerLogout"><i class="fa-solid fa-right-from-bracket"></i> Logout</div>';
    html += '      </div>';
    html += '    </div>';
    html += '  </div>';
    html += '</header>';
    return html;
  }

  /* ---------- Breadcrumb renderer ---------- */
  function renderBreadcrumb(items) {
    var el = document.getElementById('breadcrumb');
    if (!el) return;
    var html = '<a href="/admin-dashboard"><i class="fa-solid fa-house" style="font-size:11px;"></i> Dashboard</a>';
    items.forEach(function (it, i) {
      html += '<span class="sep"><i class="fa-solid fa-chevron-right" style="font-size:9px;"></i></span>';
      if (i === items.length - 1 || !it.href) {
        html += '<span class="current">' + it.label + '</span>';
      } else {
        html += '<a href="' + resolveHref(it.href) + '">' + it.label + '</a>';
      }
    });
    el.innerHTML = html;
  }

  /* ---------- Header dropdown behavior ---------- */
  function bindHeader() {
    var notifBtn = document.getElementById('notifBtn');
    var notifDd = document.getElementById('notifDropdown');
    var profileBtn = document.getElementById('profileBtn');
    var profileDd = document.getElementById('profileDropdown');

    function closeAll() {
      if (notifDd) notifDd.classList.remove('open');
      if (profileDd) profileDd.classList.remove('open');
    }

    if (notifBtn && !notifBtn.dataset.bound) {
      notifBtn.dataset.bound = 'true';
      notifBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = notifDd.classList.contains('open');
        closeAll();
        if (!open) notifDd.classList.add('open');
      });
    }

    if (profileBtn && !profileBtn.dataset.bound) {
      profileBtn.dataset.bound = 'true';
      profileBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = profileDd.classList.contains('open');
        closeAll();
        if (!open) profileDd.classList.add('open');
      });
    }

    if (!document.body.dataset.headerClickBound) {
      document.body.dataset.headerClickBound = 'true';
      document.addEventListener('click', function (e) {
        if (!e.target.closest('.header-dropdown')) closeAll();
      });
    }

    function doLogout() {
      if (window.AdminUI && AdminUI.confirm) {
        AdminUI.confirm({
          title: 'Logout',
          message: 'Are you sure you want to logout from the admin panel?',
          confirmText: 'Logout',
          danger: true,
          onConfirm: function () {
            AdminUI.toast('success', 'Logged out', 'You have been signed out securely.');
            setTimeout(function() {
              window.location.href = '/logout/';
            }, 500);
          }
        });
      } else {
        window.location.href = '/logout/';
      }
    }

    var hl = document.getElementById('headerLogout');
    if (hl && !hl.dataset.bound) {
      hl.dataset.bound = 'true';
      hl.addEventListener('click', doLogout);
    }

    var sl = document.getElementById('sidebarLogout');
    if (sl && !sl.dataset.bound) {
      sl.dataset.bound = 'true';
      sl.addEventListener('click', doLogout);
    }
  }

  /* ---------- Init (Smooth immediate mounting with zero flicker) ---------- */
  function init() {
    var sm = document.getElementById('sidebar-mount');
    var hm = document.getElementById('header-mount');
    if (!sm && !hm) return;

    document.documentElement.classList.add('sidebar-no-transition');
    if (document.body) document.body.classList.add('sidebar-no-transition');

    if (sm && !sm.dataset.mounted) {
      sm.innerHTML = buildSidebar();
      sm.dataset.mounted = 'true';
    }
    if (hm && !hm.dataset.mounted) {
      hm.innerHTML = buildHeader();
      hm.dataset.mounted = 'true';
    }

    bindHeader();
    if (window.AdminSidebar) window.AdminSidebar.init();

    // Re-enable smooth transitions on subsequent interactions
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        document.documentElement.classList.remove('sidebar-no-transition');
        if (document.body) document.body.classList.remove('sidebar-no-transition');
      });
    });
  }

  window.AdminComponents = {
    init: init,
    renderBreadcrumb: renderBreadcrumb,
    prefix: function () { return P; }
  };

  // Mount immediately to eliminate any blank frame or pop-in
  init();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  }
})();