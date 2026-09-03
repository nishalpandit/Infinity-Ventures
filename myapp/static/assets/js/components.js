/* ==========================================================================
   INFINITY ADMIN DASHBOARD — components.js
   Shared layout: injects the SAME sidebar + header into every page,
   detects active menu, renders breadcrumbs, header dropdowns.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- Path helpers (pages live at root or one level deep) ---------- */
  var SUBFOLDERS = ['users', 'quick-services', 'jobs', 'bidding', 'subscriptions', 'payments', 'reviews', 'complaints', 'reports'];

  function inSubfolder() {
    var segs = location.pathname.split('/').filter(Boolean);
    return segs.length >= 2 && SUBFOLDERS.indexOf(segs[segs.length - 2]) !== -1;
  }

  var P = inSubfolder() ? '../' : './'; // prefix for links

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

  /* ---------- Sidebar menu configuration ---------- */
  var MENU = [
    { label: 'Dashboard', icon: 'fa-gauge-high', href: 'dashboard.html' },
    {
      label: 'Users', icon: 'fa-users', children: [
        { label: 'End Users', href: 'users/users.html' },
        { label: 'Vendors', href: 'users/vendors.html' },
        { label: 'Company Vendors', href: 'users/company-vendors.html' },
        { label: 'Outsider Vendors', href: 'users/outsider-vendors.html' }
      ]
    },
    {
      label: 'Quick Services', icon: 'fa-bolt', children: [
        { label: 'All Quick Services', href: 'quick-services/index.html' },
        { label: 'Active', href: 'quick-services/index.html?status=active' },
        { label: 'Completed', href: 'quick-services/index.html?status=completed' },
        { label: 'Cancelled', href: 'quick-services/index.html?status=cancelled' }
      ]
    },
    {
      label: 'Jobs', icon: 'fa-briefcase', children: [
        { label: 'All Jobs', href: 'jobs/index.html' },
        { label: 'Active', href: 'jobs/index.html?status=active' },
        { label: 'Completed', href: 'jobs/index.html?status=completed' },
        { label: 'Cancelled', href: 'jobs/index.html?status=cancelled' }
      ]
    },
    {
      label: 'Bidding', icon: 'fa-gavel', children: [
        { label: 'All Bids', href: 'bidding/index.html' },
        { label: 'Active Bids', href: 'bidding/index.html?status=submitted' },
        { label: 'Withdrawn Bids', href: 'bidding/index.html?status=withdrawn' },
        { label: 'Rejected Bids', href: 'bidding/index.html?status=rejected' },
        { label: 'Selected Vendors', href: 'bidding/selected-vendors.html' }
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
        { label: 'Transactions', href: 'payments/index.html?view=transactions' }
      ]
    },
    { label: 'Admin Profile', icon: 'fa-user-shield', href: 'profile.html' }
  ];

  /* ---------- Sidebar template ---------- */
  function buildSidebar() {
    var html = '';
    html += '<aside class="app-sidebar" id="appSidebar">';
    html += '  <div class="sidebar-logo">';
    html += '    <a href="' + P + 'dashboard.html" style="display:flex;align-items:center;gap:12px;text-decoration:none;">';
    html += '      <span class="logo-mark"><i class="fa-solid fa-infinity"></i></span>';
    html += '      <span class="logo-text">Infinity <span>Admin</span></span>';
    html += '    </a>';
    html += '  </div>';
    html += '  <nav class="sidebar-nav" id="sidebarNav">';

    MENU.forEach(function (item) {
      if (item.children) {
        html += '<div class="snav-item has-sub" data-menu="' + item.label + '">';
        html += '  <div class="snav-link" role="button" tabindex="0">';
        html += '    <span class="snav-icon"><i class="fa-solid ' + item.icon + '"></i></span>';
        html += '    <span class="snav-label">' + item.label + '</span>';
        html += '    <span class="snav-arrow"><i class="fa-solid fa-chevron-right"></i></span>';
        html += '  </div>';
        html += '  <div class="sb-tooltip">' + item.label + '</div>';
        html += '  <div class="sb-flyout"><div class="flyout-title">' + item.label + '</div>';
        item.children.forEach(function (c) {
          html += '<a href="' + P + c.href + '" data-canon="' + canonical(c.href) + '" data-status="' + (qsFromHref(c.href) || '') + '">' + c.label + '</a>';
        });
        html += '  </div>';
        html += '  <ul class="snav-sub">';
        item.children.forEach(function (c) {
          html += '<li><a class="snav-sublink" href="' + P + c.href + '" data-canon="' + canonical(c.href) + '" data-status="' + (qsFromHref(c.href) || '') + '">' + c.label + '</a></li>';
        });
        html += '  </ul>';
        html += '</div>';
      } else {
        html += '<div class="snav-item" data-menu="' + item.label + '">';
        html += '  <a class="snav-link" href="' + P + item.href + '" data-canon="' + canonical(item.href) + '">';
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

  function qsFromHref(href) {
    var i = href.indexOf('?');
    if (i === -1) return null;
    var m = /[?&]status=([^&]*)/.exec(href);
    return m ? m[1] : null;
  }

  /* ---------- Header template ---------- */
  function buildHeader() {
    var html = '';
    html += '<header class="app-header">';
    html += '  <button class="header-toggle d-lg-none" id="mobileMenuBtn" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button>';
    html += '  <button class="header-toggle d-none d-lg-inline-flex" id="sidebarToggle" aria-label="Toggle sidebar"><i class="fa-solid fa-bars-staggered"></i></button>';
    html += '  <div class="header-actions">';
    html += '    <div style="position:relative;">';
    html += '      <button class="header-icon-btn" id="notifBtn" aria-label="Notifications"><i class="fa-regular fa-bell"></i><span class="dot"></span></button>';
    html += '      <div class="header-dropdown" id="notifDropdown">';
    html += '        <div class="hd-head"><span>Notifications</span><span class="badge badge-danger">3 new</span></div>';
    html += '        <div class="hd-item"><span class="ic icon-indigo"><i class="fa-solid fa-gavel"></i></span><div class="txt"><div class="t">New bid submitted</div><div class="d">Sharma Enterprises bid ₹48,000 on JOB-1042</div><div class="time">5 minutes ago</div></div></div>';
    html += '        <div class="hd-item"><span class="ic icon-green"><i class="fa-solid fa-indian-rupee-sign"></i></span><div class="txt"><div class="t">Subscription purchased</div><div class="d">Ravi Kumar bought 50 Bid Package (₹700)</div><div class="time">22 minutes ago</div></div></div>';
    html += '        <div class="hd-item"><span class="ic icon-red"><i class="fa-solid fa-triangle-exclamation"></i></span><div class="txt"><div class="t">New complaint filed</div><div class="d">CMP-207 opened against vendor QuickFix Services</div><div class="time">1 hour ago</div></div></div>';
    html += '        <div class="hd-footer"><a href="' + P + 'notifications.html">View all notifications</a></div>';
    html += '      </div>';
    html += '    </div>';
    html += '    <div style="position:relative;">';
    html += '      <div class="header-profile" id="profileBtn">';
    html += '        <span class="avatar">AD</span>';
    html += '        <span class="meta"><span class="name d-block">Arjun Desai</span><span class="role d-block">Super Admin</span></span>';
    html += '        <i class="fa-solid fa-chevron-down" style="font-size:10px;color:var(--text-light);"></i>';
    html += '      </div>';
    html += '      <div class="header-dropdown profile-menu" id="profileDropdown">';
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

  /* ---------- Active menu detection ---------- */
  function setActive() {
    var cur = currentCanonical();
    var curStatus = qs('status') || (qs('view') ? qs('view') : null);

    document.querySelectorAll('.snav-sublink, .sb-flyout a').forEach(function (a) {
      var canon = a.getAttribute('data-canon');
      var st = a.getAttribute('data-status');
      var isMatch = canon === cur && (st ? st === qs('status') : !qs('status'));
      if (isMatch) a.classList.add('active');
    });

    document.querySelectorAll('.snav-item').forEach(function (item) {
      var activeInside = item.querySelector('.snav-sublink.active');
      var direct = item.querySelector('.snav-link[data-canon]');
      if (direct && direct.getAttribute('data-canon') === cur) {
        direct.classList.add('active');
      }
      if (activeInside) {
        item.classList.add('open');
        var parent = item.querySelector(':scope > .snav-link');
        if (parent) parent.classList.add('parent-active');
      }
    });
  }

  /* ---------- Breadcrumb renderer ---------- */
  function renderBreadcrumb(items) {
    var el = document.getElementById('breadcrumb');
    if (!el) return;
    var html = '<a href="' + P + 'dashboard.html"><i class="fa-solid fa-house" style="font-size:11px;"></i> Dashboard</a>';
    items.forEach(function (it, i) {
      html += '<span class="sep"><i class="fa-solid fa-chevron-right" style="font-size:9px;"></i></span>';
      if (i === items.length - 1 || !it.href) {
        html += '<span class="current">' + it.label + '</span>';
      } else {
        html += '<a href="' + it.href + '">' + it.label + '</a>';
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

    if (notifBtn) notifBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = notifDd.classList.contains('open');
      closeAll();
      if (!open) notifDd.classList.add('open');
    });
    if (profileBtn) profileBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = profileDd.classList.contains('open');
      closeAll();
      if (!open) profileDd.classList.add('open');
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.header-dropdown')) closeAll();
    });

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
      }
    }
    var hl = document.getElementById('headerLogout');
    if (hl) hl.addEventListener('click', doLogout);
    var sl = document.getElementById('sidebarLogout');
    if (sl) sl.addEventListener('click', doLogout);
  }

  /* ---------- Init ---------- */
  function init() {
    var sm = document.getElementById('sidebar-mount');
    var hm = document.getElementById('header-mount');
    if (sm) sm.innerHTML = buildSidebar();
    if (hm) hm.innerHTML = buildHeader();
    setActive();
    bindHeader();
    if (window.AdminSidebar) window.AdminSidebar.init();
  }

  window.AdminComponents = {
    init: init,
    renderBreadcrumb: renderBreadcrumb,
    prefix: function () { return P; }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();