/* ==========================================================================
   INFINITY ADMIN DASHBOARD — sidebar.js
   Collapse/expand with localStorage persistence, submenu accordion,
   mobile off-canvas drawer.
   ========================================================================== */

(function () {
  'use strict';

  var STORAGE_KEY = 'infinity_admin_sidebar';
  var MOBILE_BP = 992;

  function isMobile() {
    return window.innerWidth < MOBILE_BP;
  }

  function applyState() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'collapsed') {
        document.body.classList.add('sidebar-collapsed');
      } else {
        document.body.classList.remove('sidebar-collapsed');
      }
    } catch (e) {
      console.warn('localStorage not available', e);
    }
  }

  function toggleDesktop() {
    var collapsed = document.body.classList.toggle('sidebar-collapsed');
    try {
      localStorage.setItem(STORAGE_KEY, collapsed ? 'collapsed' : 'expanded');
    } catch (e) {
      console.warn('localStorage not available', e);
    }
  }

  function openMobile() {
    document.body.classList.add('sidebar-mobile-open');
    var ov = document.getElementById('sidebarOverlay');
    if (ov) ov.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeMobile() {
    document.body.classList.remove('sidebar-mobile-open');
    var ov = document.getElementById('sidebarOverlay');
    if (ov) ov.classList.remove('show');
    document.body.style.overflow = '';
  }

  function bindSubmenus() {
    document.querySelectorAll('.snav-item.has-sub > .snav-link').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        if (document.body.classList.contains('sidebar-collapsed') && !isMobile()) {
          // Collapsed desktop: flyout handles submenus on hover; do nothing on click
          return;
        }
        var item = link.parentElement;
        var wasOpen = item.classList.contains('open');
        // Accordion: close siblings
        document.querySelectorAll('.snav-item.has-sub.open').forEach(function (o) {
          if (o !== item) o.classList.remove('open');
        });
        item.classList.toggle('open', !wasOpen);
      });
      link.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          link.click();
        }
      });
    });
  }

  function init() {
    applyState();

    // Desktop toggle button (header)
    var toggleBtn = document.getElementById('sidebarToggle');
    if (toggleBtn) toggleBtn.addEventListener('click', toggleDesktop);

    // Mobile hamburger
    var mobileBtn = document.getElementById('mobileMenuBtn');
    if (mobileBtn) mobileBtn.addEventListener('click', openMobile);

    // Overlay click closes drawer
    var overlay = document.getElementById('sidebarOverlay');
    if (overlay) overlay.addEventListener('click', closeMobile);

    // Selecting a page inside the drawer closes it
    document.querySelectorAll('.app-sidebar a').forEach(function (a) {
      a.addEventListener('click', function () {
        if (isMobile()) closeMobile();
      });
    });

    bindSubmenus();

    // Reset mobile state when resizing to desktop
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        if (!isMobile()) closeMobile();
      }, 120);
    });

    // ESC closes mobile drawer
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isMobile()) closeMobile();
    });
  }

  window.AdminSidebar = {
    init: init,
    toggle: toggleDesktop,
    openMobile: openMobile,
    closeMobile: closeMobile
  };

  // Apply persisted state as early as possible (before components inject markup)
  applyState();
})();