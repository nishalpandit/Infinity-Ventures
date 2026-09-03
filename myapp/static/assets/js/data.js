/* ==========================================================================
   INFINITY ADMIN DASHBOARD — data.js
   Centralized mock data for all modules (Cleared for Backend Integration).
   ========================================================================== */

(function () {
  'use strict';

  // Empty arrays for backend integration
  window.AdminData = {
    users: [
      { id: 'USR-001', name: 'Aarav Sharma', location: 'Delhi', registered: '2023-10-01' },
      { id: 'USR-002', name: 'Priya Patel', location: 'Mumbai', registered: '2023-10-05' }
    ],
    vendors: [
      { id: 'VEND-001', name: 'TechSolutions India', type: 'company', category: 'Software Development', registered: '2023-09-15', location: 'Bangalore' },
      { id: 'VEND-002', name: 'Ravi Kumar', type: 'outsider', category: 'Graphic Design', registered: '2023-10-10', location: 'Pune' }
    ],
    quickServices: [
      { id: 'QS-001', title: 'E-commerce UI Redesign', user: 'Aarav Sharma', budget: 15000, status: 'active' },
      { id: 'QS-002', title: 'Server Maintenance', user: 'Priya Patel', budget: 8000, status: 'in-progress' },
      { id: 'QS-003', title: 'Logo Creation', user: 'Amit Singh', budget: 3500, status: 'completed' }
    ],
    jobs: [
      { id: 'JOB-001', title: 'Build Mobile App', user: 'Aarav Sharma', bids: 4, status: 'active' },
      { id: 'JOB-002', title: 'SEO Optimization', user: 'Priya Patel', bids: 2, status: 'in-progress' },
      { id: 'JOB-003', title: 'Database Migration', user: 'Neha Gupta', bids: 0, status: 'pending' }
    ],
    bids: [
      { id: 'BID-001', vendor: 'TechSolutions India', jobTitle: 'Build Mobile App', quotation: 45000, status: 'selected' },
      { id: 'BID-002', vendor: 'Ravi Kumar', jobTitle: 'Build Mobile App', quotation: 38000, status: 'rejected' },
      { id: 'BID-003', vendor: 'Creative Minds', jobTitle: 'SEO Optimization', quotation: 12000, status: 'pending' }
    ],
    transactions: [],
    purchases: [
      { id: 'TXN-001', vendor: 'TechSolutions India', package: 'Pro Pack', amount: 350, paymentStatus: 'success' },
      { id: 'TXN-002', vendor: 'Ravi Kumar', package: 'Starter Pack', amount: 100, paymentStatus: 'success' }
    ],
    packages: [
      { id: 'PKG-1', name: 'Starter Pack', credits: 5, price: 100, status: 'active' },
      { id: 'PKG-2', name: 'Pro Pack', credits: 20, price: 350, status: 'active' }
    ],
    complaints: [],
    userReviews: [],
    vendorReviews: [],
    categories: ['Software Development', 'Graphic Design', 'Marketing', 'Data Entry'],
    cities: ['Delhi', 'Mumbai', 'Bangalore', 'Pune', 'Hyderabad']
  };

})();