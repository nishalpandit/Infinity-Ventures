/* ==========================================================================
   INFINITY ADMIN DASHBOARD — data.js
   Centralized data store (static mock data removed; all data is
   served dynamically by the Django backend via template context).
   ========================================================================== */

(function () {
  'use strict';

  // Retained only for any legacy UI helpers that reference AdminData.
  // All module data (jobs, quick-services, bids, etc.) is rendered
  // server-side via Django templates — no static arrays needed here.
  window.AdminData = {
    users: [],
    vendors: [],
    quickServices: [],
    jobs: [],
    bids: [],
    transactions: [],
    purchases: [],
    packages: [],
    complaints: [],
    userReviews: [],
    vendorReviews: [],
    categories: [],
    cities: []
  };

})();