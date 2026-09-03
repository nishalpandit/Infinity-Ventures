/* Shared vendor table builder used by vendors.html, company-vendors.html, outsider-vendors.html */
(function () {
  'use strict';

  window.VendorTable = {
    init: function (opts) {
      var D = window.AdminData, U = window.AdminUI;
      var typeFilter = opts.type || null; // null = all, 'company', 'outsider'

      var data = typeFilter
        ? D.vendors.filter(function (v) { return v.type === typeFilter; })
        : D.vendors;

      var typeFilterDef = typeFilter ? [] : [{
        key: 'type',
        options: [
          { value: 'all', label: 'All Types' },
          { value: 'company', label: 'Company Vendor' },
          { value: 'outsider', label: 'Outsider Vendor' }
        ],
        match: function (r, v) { return r.type === v; }
      }];

      var table = U.createTable({
        mount: '#tableMount',
        data: data,
        searchKeys: ['id', 'name', 'email', 'contact', 'category', 'location'],
        searchPlaceholder: 'Search vendors…',
        exportName: opts.exportName || 'vendors',
        pageSize: 10,
        filters: typeFilterDef.concat([
          {
            key: 'status',
            options: [
              { value: 'all', label: 'All Status' },
              { value: 'active', label: 'Active' },
              { value: 'suspended', label: 'Suspended' }
            ],
            match: function (r, v) { return r.status === v; }
          },
          {
            key: 'location',
            options: [{ value: 'all', label: 'All Locations' }].concat(D.cities.map(function (c) { return { value: c, label: c }; })),
            match: function (r, v) { return r.location === v; }
          },
          {
            key: 'category',
            options: [{ value: 'all', label: 'All Categories' }].concat(D.categories.map(function (c) { return { value: c, label: c }; })),
            match: function (r, v) { return r.category === v; }
          }
        ]),
        columns: [
          { key: 'id', label: 'Vendor ID', sortable: true, render: function (r) { return '<span class="mono">' + r.id + '</span>'; } },
          { key: 'name', label: 'Vendor', sortable: true, render: function (r) { return U.userCell(r.name, r.email, r.id); } },
          { key: 'type', label: 'Vendor Type', sortable: true, render: function (r) { return U.badge(r.type); } },
          { key: 'contact', label: 'Contact', render: function (r) { return U.esc(r.contact); } },
          { key: 'category', label: 'Category', sortable: true, render: function (r) { return U.esc(r.category); } },
          { key: 'location', label: 'Location', sortable: true, render: function (r) { return U.esc(r.location); } },
          { key: 'totalBids', label: 'Total Bids', sortable: true, render: function (r) { return '<span class="count-pill">' + r.totalBids + '</span>'; } },
          { key: 'completedJobs', label: 'Completed Jobs', sortable: true, render: function (r) { return '<span class="count-pill green">' + r.completedJobs + '</span>'; } },
          { key: 'bidCredits', label: 'Bid Credits', sortable: true, render: function (r) { return '<span class="count-pill blue">' + r.bidCredits + '</span>'; } },
          { key: 'status', label: 'Status', sortable: true, render: function (r) { return U.badge(r.status); } },
          { key: 'registered', label: 'Registered', sortable: true, render: function (r) { return r.registered; } },
          {
            key: 'actions', label: 'Actions', csv: false, render: function (r) {
              return U.actionBtns([
                { action: 'view', icon: 'fa-eye', title: 'View', cls: 'view' },
                { action: 'edit', icon: 'fa-pen', title: 'Edit', cls: 'edit' },
                { action: r.status === 'active' ? 'suspend' : 'activate', icon: r.status === 'active' ? 'fa-ban' : 'fa-check', title: r.status === 'active' ? 'Suspend' : 'Activate', cls: r.status === 'active' ? 'warn' : 'ok' },
                { action: 'delete', icon: 'fa-trash-can', title: 'Delete', cls: 'danger' }
              ]);
            }
          }
        ],
        onAction: function (act, row) {
          if (act === 'view') {
            location.href = 'vendor-details.html?id=' + row.id;
          } else if (act === 'edit') {
            U.modal({
              title: 'Edit Vendor — ' + row.id,
              body:
                '<div class="row g-3">' +
                '<div class="col-md-6"><label class="form-label">Name</label><input class="form-control" id="eName" value="' + U.esc(row.name) + '"></div>' +
                '<div class="col-md-6"><label class="form-label">Contact</label><input class="form-control" id="eContact" value="' + U.esc(row.contact) + '"></div>' +
                '<div class="col-md-6"><label class="form-label">Category</label><select class="form-select" id="eCat">' +
                D.categories.map(function (c) { return '<option' + (c === row.category ? ' selected' : '') + '>' + c + '</option>'; }).join('') + '</select></div>' +
                '<div class="col-md-6"><label class="form-label">Location</label><select class="form-select" id="eLoc">' +
                D.cities.map(function (c) { return '<option' + (c === row.location ? ' selected' : '') + '>' + c + '</option>'; }).join('') + '</select></div>' +
                '</div>',
              onSave: function () {
                row.name = document.getElementById('eName').value;
                row.contact = document.getElementById('eContact').value;
                row.category = document.getElementById('eCat').value;
                row.location = document.getElementById('eLoc').value;
                table.refresh();
                U.toast('success', 'Vendor updated', row.name + ' has been saved.');
              }
            });
          } else if (act === 'suspend') {
            U.confirm({
              title: 'Suspend vendor?', message: row.name + ' will no longer be able to bid or accept work.',
              danger: true, icon: 'fa-ban', confirmText: 'Suspend',
              onConfirm: function () { row.status = 'suspended'; table.refresh(); U.toast('warning', 'Vendor suspended', row.name + ' has been suspended.'); }
            });
          } else if (act === 'activate') {
            row.status = 'active';
            table.refresh();
            U.toast('success', 'Vendor activated', row.name + ' is now active.');
          } else if (act === 'delete') {
            U.confirm({
              title: 'Delete vendor?', message: 'This will permanently remove ' + row.name + ' and all associated records.',
              danger: true, confirmText: 'Delete',
              onConfirm: function () {
                var idx = D.vendors.indexOf(row);
                if (idx > -1) D.vendors.splice(idx, 1);
                table.refresh();
                U.toast('success', 'Vendor deleted', row.name + ' has been removed.');
              }
            });
          }
        }
      });

      return table;
    }
  };
})();