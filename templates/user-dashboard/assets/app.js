/* Fixora user — shared Vanilla JS interactions */
(() => {
  'use strict';
  const $ = (s, c=document) => c.querySelector(s);
  const $$ = (s, c=document) => [...c.querySelectorAll(s)];
  const body = document.body;
  const root = body.dataset.root || '';
  const pageKey = body.dataset.page || 'dashboard';
  const pageTitle = body.dataset.title || 'Dashboard';

  const icons = {
    grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    bolt:'<path d="m13 2-9 12h8l-1 8 9-12h-8l1-8Z"/>', plus:'<path d="M12 5v14M5 12h14"/>', briefcase:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2"/>',
    list:'<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>', file:'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
    quote:'<path d="M8 11H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v12a4 4 0 0 1-4 4H5M20 11h-4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v12a4 4 0 0 1-4 4h-1"/>', users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    chat:'<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>', bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>', star:'<polygon points="12 2 15 8.5 22 9.3 17 14 18.2 21 12 17.7 5.8 21 7 14 2 9.3 9 8.5 12 2"/>',
    help:'<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 1 1 5.7 1.4c-.8 1.1-2.8 1.6-2.8 3.6M12 18h.01"/>', user:'<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="7" r="4"/>', settings:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21h-4v-.1A1.7 1.7 0 0 0 8.6 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3v-4h.1A1.7 1.7 0 0 0 4.6 8.6a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3h4v.1A1.7 1.7 0 0 0 15.4 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.37.25.67.6.82 1H21v4h-.1c-.46 0-.9.17-1.23.49-.12.12-.21.28-.27.51Z"/>',
    logout:'<path d="M10 17l5-5-5-5M15 12H3M21 19V5a2 2 0 0 0-2-2h-6"/>', menu:'<path d="M4 6h16M4 12h16M4 18h16"/>', panel:'<path d="M3 3h18v18H3zM9 3v18"/>', search:'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>', chevron:'<path d="m9 18 6-6-6-6"/>', down:'<path d="m6 9 6 6 6-6"/>',
    map:'<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/>', clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    check:'<path d="m5 12 4 4L19 6"/>', x:'<path d="M18 6 6 18M6 6l12 12"/>', eye:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>', filter:'<path d="M22 3H2l8 9.5V19l4 2v-8.5z"/>', sort:'<path d="M3 6h15M3 12h11M3 18h7M19 14v7M16 18l3 3 3-3"/>', more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>', edit:'<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>', trash:'<path d="M3 6h18M8 6V4h8v2M19 6l-1 15H6L5 6M10 11v5M14 11v5"/>',
    upload:'<path d="M12 16V4M7 9l5-5 5 5M4 20h16"/>', image:'<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>', paperclip:'<path d="m21.4 11.6-8.9 8.9a6 6 0 0 1-8.5-8.5l9.6-9.6a4 4 0 0 1 5.7 5.7l-9.6 9.6a2 2 0 1 1-2.8-2.8l8.9-8.9"/>', send:'<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>', phone:'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.4 19.4 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.12.9.33 1.78.62 2.62a2 2 0 0 1-.45 2.11L8 9.7a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.84.29 1.72.5 2.62.62a2 2 0 0 1 1.4 2.3Z"/>',
    home:'<path d="m3 11 9-8 9 8v10h-6v-6H9v6H3Z"/>', shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>', lock:'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>', mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>', building:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M9 21v-5h6v5"/>',
    alert:'<path d="M10.3 3.5 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.5a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>', info:'<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>', award:'<circle cx="12" cy="8" r="6"/><path d="M8.2 13 7 22l5-3 5 3-1.2-9"/>', tool:'<path d="M14.7 6.3a4 4 0 0 0-5-5L12 4 9 7 6.3 4.3a4 4 0 0 0 5 5L3 17.6A2 2 0 0 0 5.4 20l8.3-8.3a4 4 0 0 0 5-5L16 9l-3-3 2.7-2.7Z"/>',
    rupee:'<path d="M6 3h12M6 8h12M7 3c6 0 7 7 0 7h-1l9 11"/>', chart:'<path d="M3 3v18h18M7 16l4-5 4 3 5-7"/>', refresh:'<path d="M20 11a8 8 0 1 0-2.3 5.7L20 14M20 6v5h-5"/>', copy:'<rect x="9" y="9" width="12" height="12" rx="2"/><rect x="3" y="3" width="12" height="12" rx="2"/>',
    camera:'<path d="M14.5 4 16 6h3a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3l1.5-2z"/><circle cx="12" cy="13" r="4"/>', globe:'<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>', download:'<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>', external:'<path d="M14 3h7v7M10 14 21 3M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/>'
  };
  function icon(name, cls='') { return `<svg class="icon ${cls}" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.info}</svg>`; }

  const nav = [
    ['dashboard','grid','Dashboard','dashboard.html'],
    ['quick-create','bolt','Quick Services','quick-services/create.html'],
    ['quick','list','My Quick Services','quick-services/index.html'],
    ['jobs','briefcase','My Jobs','jobs/index.html'],
    ['vendors','users','Vendors','vendors/index.html'],
    ['messages','chat','Messages','messages/index.html'],
    ['notifications','bell','Notifications','notifications.html'],

    ['profile','user','Profile','profile/index.html'],
    ['settings','settings','Settings','settings/index.html']
  ];
  function route(path){ return root + path; }
  function navActive(k){
    if(pageKey === k) return true;
    if(k==='quick' && pageKey.startsWith('quick-') && pageKey!=='quick-create') return true;
    if(k==='jobs' && pageKey.startsWith('job-') && pageKey!=='job-create' && !pageKey.includes('quotation') && pageKey!=='job-compare') return true;
    if(k==='quotations' && (pageKey.includes('quotation') || pageKey==='job-compare')) return true;
    if(k==='vendors' && pageKey.startsWith('vendor')) return true;
    if(k==='messages' && pageKey.startsWith('message')) return true;
    if(k==='reviews' && pageKey.startsWith('review')) return true;
    if(k==='support' && pageKey.startsWith('support')) return true;
    if(k==='profile' && pageKey.startsWith('profile')) return true;
    if(k==='settings' && pageKey.startsWith('setting')) return true;
    return false;
  }
  const sidebarRoot = $('#sidebar-root');
  if(sidebarRoot){
    const links = nav.map(([k,i,l,p]) => {
      const link = `<a class="nav-link ${navActive(k)?'active':''}" href="${route(p)}" data-tooltip="${l}">${icon(i)}<span class="nav-text">${l}</span></a>`;
      if(k !== 'quotations') return link;
      return `<div class="nav-parent ${navActive(k)?'open':''}">${link}<button class="submenu-toggle" type="button" aria-label="Toggle quotation links">${icon('down')}</button></div><div class="nav-submenu"><a href="${route('quick-services/quotations.html')}">Quotations</a><a href="${route('jobs/compare.html')}">Compare Quotations</a></div>`;
    }).join('');
    sidebarRoot.outerHTML = `<aside class="sidebar" id="sidebar" aria-label="user navigation">
      <a class="brand" href="${route('dashboard.html')}"><span class="brand-mark">${icon('tool')}</span><span class="brand-copy"><strong>Fixora</strong><span>user Portal</span></span></a>
      <nav class="nav-scroll"><div class="nav-label">Workspace</div>${links}<div class="nav-label">Session</div><a class="nav-link" href="${route('dashboard.html')}" data-confirm="logout" data-tooltip="Logout">${icon('logout')}<span class="nav-text">Logout</span></a></nav>
      <div class="sidebar-bottom"><div class="side-user"><span class="avatar sm dyn-avatar"></span><span class="side-user-copy"><strong class="dyn-name"></strong><span>user account</span></span></div></div>
    </aside>`;
  }
  const topbarRoot = $('#topbar-root');
  if(topbarRoot){
    topbarRoot.outerHTML = `<header class="topbar"><div class="topbar-left"><button class="icon-btn hamburger" id="mobile-menu" aria-label="Open menu">${icon('menu')}</button><button class="icon-btn desktop-collapse" id="collapse-menu" aria-label="Collapse sidebar">${icon('panel')}</button><div><div class="topbar-title">${pageTitle}</div><div class="breadcrumbs"><a href="${route('dashboard.html')}">user</a> &nbsp;/&nbsp; ${pageTitle}</div></div></div><div class="topbar-actions"><div class="top-search">${icon('search')}<input type="search" id="global-search" placeholder="Search jobs, services, vendors" aria-label="Global search"></div><a class="icon-btn" href="${route('messages/index.html')}" aria-label="Messages">${icon('chat')}</a><a class="icon-btn" href="${route('notifications.html')}" aria-label="Notifications">${icon('bell')}<span class="notification-dot"></span></a><a class="top-user" href="${route('profile/index.html')}"><span class="avatar dyn-avatar"></span><span class="top-user-copy"><strong class="dyn-name"></strong><span>user account</span></span></a></div></header>`;
  }

  fetch('/api/user-nav-data/')
    .then(r => r.json())
    .then(d => {
      $$('.avatar:not(.xl)').forEach(el => el.textContent = d.initials);
      $$('.side-user-copy strong, .top-user-copy strong').forEach(el => el.textContent = d.name);
    }).catch(e => console.error(e));
  if(!$('.mobile-overlay')) body.insertAdjacentHTML('beforeend','<div class="mobile-overlay" id="mobile-overlay"></div><div class="toast-container" id="toast-container" aria-live="polite"></div>');
  if(!$('#global-modal')) body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop" id="global-modal" role="dialog" aria-modal="true"><div class="modal"><div class="modal-head"><h3 id="global-modal-title">Please confirm</h3><button class="modal-close" data-modal-close>${icon('x')}</button></div><div class="modal-body" id="global-modal-body"></div><div class="modal-actions"><button class="btn btn-secondary" data-modal-close>Cancel</button><button class="btn btn-primary" id="global-modal-confirm">Confirm</button></div></div></div>`);

  // Replace declarative icons after shared layout is mounted.
  $$('[data-icon]').forEach(el => el.innerHTML = icon(el.dataset.icon));

  // Sidebar state and mobile drawer.
  if(localStorage.getItem('fixora-sidebar') === 'collapsed' && innerWidth > 767) body.classList.add('sidebar-collapsed');
  $('#collapse-menu')?.addEventListener('click', () => { body.classList.toggle('sidebar-collapsed'); localStorage.setItem('fixora-sidebar', body.classList.contains('sidebar-collapsed')?'collapsed':'expanded'); });
  const closeMobile = () => body.classList.remove('mobile-menu-open');
  $('#mobile-menu')?.addEventListener('click', () => body.classList.add('mobile-menu-open'));
  $('#mobile-overlay')?.addEventListener('click', closeMobile);
  $$('.sidebar .nav-link').forEach(a => a.addEventListener('click', () => { if(innerWidth<=767 && !a.dataset.confirm) closeMobile(); }));
  $$('.submenu-toggle').forEach(toggle => toggle.addEventListener('click', () => toggle.closest('.nav-parent')?.classList.toggle('open')));
  $$('.settings-link').forEach(link => {
    const current = location.pathname.split('/').slice(-1)[0];
    if((link.getAttribute('href')||'').split('/').slice(-1)[0] === current) link.classList.add('active');
  });

  // Toasts.
  window.showToast = function(title, message='', type='success'){
    const c = $('#toast-container'); if(!c) return;
    const el = document.createElement('div'); el.className=`toast ${type}`;
    el.innerHTML=`<span class="toast-icon">${icon(type==='error'?'alert':'check')}</span><div><strong>${title}</strong>${message?`<p>${message}</p>`:''}</div>`;
    c.append(el); setTimeout(()=>{ el.style.opacity='0'; el.style.transform='translateX(20px)'; setTimeout(()=>el.remove(),220); },3300);
  };

  // Modal and confirmation system.
  let confirmAction = null;
  const modal = $('#global-modal');
  const openGlobalModal = (title, html, confirmLabel='Confirm', action=null, danger=false) => {
    $('#global-modal-title').textContent=title; $('#global-modal-body').innerHTML=html; const b=$('#global-modal-confirm'); b.textContent=confirmLabel; b.className=`btn ${danger?'btn-danger':'btn-primary'}`; confirmAction=action; modal.classList.add('open');
  };
  const closeModal = m => { (m||modal)?.classList.remove('open'); if(!m || m===modal) confirmAction=null; };
  $$('[data-modal-close]').forEach(b=>b.addEventListener('click',()=>closeModal(b.closest('.modal-backdrop'))));
  $$('.modal-backdrop').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)closeModal(m)}));
  $('#global-modal-confirm')?.addEventListener('click',()=>{ const fn=confirmAction; modal.classList.remove('open'); confirmAction=null; if(fn)fn(); });
  $$('[data-modal-open]').forEach(b=>b.addEventListener('click',()=>$('#'+b.dataset.modalOpen)?.classList.add('open')));
  $$('[data-confirm]').forEach(el=>el.addEventListener('click',e=>{
    e.preventDefault(); const type=el.dataset.confirm; const map={
      logout:['Log out of Fixora?','You will need to sign in again to manage your services and jobs.','Log out','You have been logged out.'],
      cancel:['Cancel this item?','This action will stop new vendor responses. A Quick Service may still be cancelled after a vendor is accepted.','Cancel item','Request cancelled'],
      close:['Close this item?','Closed requests no longer accept quotations. You can review the history at any time.','Close item','Request closed'],
      delete:['Delete this item?','This action cannot be undone.','Delete','Item deleted'],
      withdraw:['Reject all quotations?','The job can be reposted later if none of the quotations meet your needs.','Reject all','Quotations rejected']
    }; const x=map[type]||['Please confirm',el.dataset.confirmMessage||'Are you sure you want to continue?','Confirm','Action completed'];
    openGlobalModal(x[0],`<p>${x[1]}</p>`,x[2],()=>{ 
      if(type==='logout') { window.location.href = '/logout/'; return; }
      if(type==='delete') el.closest('[data-removable]')?.remove(); 
      showToast(x[3],'Your change has been saved.'); 
    },['delete','cancel','withdraw'].includes(type));
  }));

  // Accept / select vendors. Quick Service permits one vendor; Long Job permits many.
  $$('[data-accept-quick]').forEach(btn=>btn.addEventListener('click',()=>{
    const name=btn.dataset.acceptQuick;
    openGlobalModal('Accept vendor for this Quick Service?',`<div class="callout neutral">${icon('info')}<div><strong>${name}</strong>Are you sure you want to accept this vendor for this Quick Service? Other vendor responses will remain available.</div></div><p class="small muted">You can still cancel the Quick Service after accepting a vendor. Service payment is made directly to the vendor, not through Fixora.</p>`,'Accept vendor',()=>{ localStorage.setItem('fixora-quick-vendor',name); $$('[data-accept-quick]').forEach(b=>{b.textContent=b.dataset.acceptQuick===name?'Vendor accepted':'Accept vendor';b.disabled=b.dataset.acceptQuick!==name;}); showToast(`${name} selected`,'The vendor has been notified. Other quotations were not rejected.'); });
  }));
  $$('[data-select-job]').forEach(btn=>btn.addEventListener('click',()=>{
    const name=btn.dataset.selectJob; let selected=JSON.parse(localStorage.getItem('fixora-job-vendors')||'[]'); const has=selected.includes(name);
    if(has){ selected=selected.filter(n=>n!==name); localStorage.setItem('fixora-job-vendors',JSON.stringify(selected)); btn.classList.remove('btn-soft'); btn.classList.add('btn-primary'); btn.innerHTML=`${icon('plus')} Select vendor`; showToast(`${name} removed`,'You can add the vendor again at any time.'); }
    else openGlobalModal('Select vendor for this job?',`<p>Select <strong>${name}</strong> for the Full House Renovation job?</p><div class="callout success">${icon('users')}<div><strong>Multiple vendors supported</strong>You can select other vendors and assign a different part of the work to each.</div></div>`,'Select vendor',()=>{selected.push(name);localStorage.setItem('fixora-job-vendors',JSON.stringify(selected));btn.classList.remove('btn-primary');btn.classList.add('btn-soft');btn.innerHTML=`${icon('check')} Selected`;showToast(`${name} selected`,'Next, assign this vendor a scope of work.');});
  }));

  // Tabs filter table/card rows.
  $$('.tabs').forEach(tabs=>{
    const scope=tabs.closest('[data-filter-scope]')||tabs.parentElement;
    $$('.tab',tabs).forEach(tab=>tab.addEventListener('click',()=>{
      $$('.tab',tabs).forEach(x=>x.classList.remove('active')); tab.classList.add('active'); const f=tab.dataset.status||'all';
      $$('[data-row]',scope).forEach(row=>row.hidden=!(f==='all'||row.dataset.status===f));
      updateVisibleCount(scope);
    }));
  });
  function updateVisibleCount(scope){ const visible=$$('[data-row]',scope).filter(r=>!r.hidden); const out=$('[data-result-count]',scope); if(out)out.textContent=`${visible.length} result${visible.length===1?'':'s'}`; }

  // Search, select filters and sorting.
  $$('[data-search-input]').forEach(input=>input.addEventListener('input',()=>filterScope(input.closest('[data-filter-scope]')||document)));
  $$('[data-filter]').forEach(select=>select.addEventListener('change',()=>filterScope(select.closest('[data-filter-scope]')||document)));
  function filterScope(scope){
    const query=($('[data-search-input]',scope)?.value||'').toLowerCase().trim(); const filters=$$('[data-filter]',scope).filter(x=>x.value&&x.value!=='all');
    $$('[data-row]',scope).forEach(row=>{ const text=(row.dataset.search||row.textContent).toLowerCase(); const searchOK=!query||text.includes(query); const filterOK=filters.every(f=>{const key=f.dataset.filter;return (row.dataset[key]||'').toLowerCase()===f.value.toLowerCase();}); row.hidden=!(searchOK&&filterOK); }); updateVisibleCount(scope);
  }
  $$('[data-sort]').forEach(select=>select.addEventListener('change',()=>{
    const scope=select.closest('[data-filter-scope]')||document, container=$('[data-rows]',scope); if(!container)return; const [key,dir]=select.value.split(':'); const rows=$$('[data-row]',container);
    rows.sort((a,b)=>{let av=a.dataset[key]||'',bv=b.dataset[key]||''; if(!isNaN(av)&&!isNaN(bv)){av=+av;bv=+bv} return (av>bv?1:av<bv?-1:0)*(dir==='desc'?-1:1)}).forEach(r=>container.append(r));
  }));
  $$('.page-btn').forEach(b=>b.addEventListener('click',()=>{const p=b.parentElement;$$('.page-btn',p).forEach(x=>x.classList.remove('active'));b.classList.add('active');showToast(`Page ${b.dataset.page||b.textContent}`,'Results updated.','info')}));

  // Form validation, saves, and success state.
  $$('form.needs-validation').forEach(form=>form.addEventListener('submit',e=>{
    e.preventDefault(); let valid=true; $$('[required]',form).forEach(f=>{ const bad=!f.value.trim(); f.classList.toggle('error',bad); valid=valid&&!bad; });
    $$('[data-rating]',form).forEach(r=>{ const bad=!r.dataset.selected; r.classList.toggle('rating-error',bad); valid=valid&&!bad; });
    if(!valid){showToast('Please complete required fields','Review the highlighted fields and try again.','error');$('[required].error',form)?.focus();return;}
    const target=form.dataset.successTarget; if(target){ form.closest('.form-card')?.classList.add('hidden-after-submit'); const s=$('#'+target); if(s){s.hidden=false;s.scrollIntoView({behavior:'smooth',block:'start'});} }
    else showToast(form.dataset.successTitle||'Changes saved',form.dataset.successMessage||'Your information has been updated.');
    form.reset();
  }));
  $$('[data-save-draft]').forEach(b=>b.addEventListener('click',()=>showToast('Draft saved','You can continue editing it from your dashboard.')));
  $$('[data-toast]').forEach(b=>b.addEventListener('click',()=>showToast(b.dataset.toast,b.dataset.toastMessage||'Your request has been updated.')));
  $$('input.error,select.error,textarea.error').forEach(f=>f.addEventListener('input',()=>f.classList.remove('error')));

  // File previews.
  $$('input[type=file][data-preview]').forEach(input=>input.addEventListener('change',()=>{
    const list=$('#'+input.dataset.preview); if(!list)return; list.innerHTML=''; [...input.files].forEach((f,i)=>{const chip=document.createElement('div');chip.className='file-chip';chip.innerHTML=`${icon(f.type.startsWith('image/')?'image':'file')}<span>${f.name} <small>(${Math.max(1,Math.round(f.size/1024))} KB)</small></span><button type="button" aria-label="Remove">${icon('x')}</button>`;chip.querySelector('button').onclick=()=>chip.remove();list.append(chip);});
  }));
  $$('.upload-zone').forEach(z=>{z.addEventListener('dragover',e=>{e.preventDefault();z.classList.add('drag')});z.addEventListener('dragleave',()=>z.classList.remove('drag'));z.addEventListener('drop',()=>z.classList.remove('drag'));});

  // Inbox, chat compose, notification state.
  $$('.conversation').forEach(c=>c.addEventListener('click',()=>{$$('.conversation').forEach(x=>x.classList.remove('active'));c.classList.add('active');if(innerWidth<768&&c.dataset.href)location.href=c.dataset.href;}));
  $$('.chat-compose').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();const input=$('input',form);if(!input.value.trim())return;const area=$('.chat-messages');const row=document.createElement('div');row.className='message-row sent';row.innerHTML=`<div class="message">${input.value.replace(/[<>]/g,'')}<div class="message-time">Just now · Read ✓✓</div></div>`;area.append(row);input.value='';area.scrollTop=area.scrollHeight;}));
  $$('[data-attachment]').forEach(b=>b.addEventListener('click',()=>showToast('Choose an attachment','Images and documents up to 10 MB are supported.','info')));
  $$('[data-notification-read]').forEach(b=>b.addEventListener('click',()=>{const n=b.closest('.notification-item');n.classList.remove('unread');b.remove();showToast('Marked as read');}));
  $('[data-mark-all]')?.addEventListener('click',()=>{$$('.notification-item.unread').forEach(n=>n.classList.remove('unread'));$$('[data-notification-read]').forEach(b=>b.remove());showToast('All caught up','All notifications have been marked as read.');});

  // FAQs, ratings, assignments and addresses.
  $$('.faq-question').forEach(q=>q.addEventListener('click',()=>q.parentElement.classList.toggle('open')));
  $$('[data-rating] button').forEach(star=>star.addEventListener('click',()=>{const wrap=star.parentElement,n=+star.dataset.value;wrap.dataset.selected=n;wrap.classList.remove('rating-error');$$('button',wrap).forEach(s=>s.classList.toggle('selected',+s.dataset.value<=n));$('[data-rating-label]')&&( $('[data-rating-label]').textContent=`${n} out of 5 — ${['','Poor','Fair','Good','Very good','Excellent'][n]}` );}));
  $$('[data-assignment-form]').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();const name=form.dataset.assignmentForm;showToast(`Assignment saved for ${name}`,'The vendor has been notified of the updated work scope.');const badge=$('.assignment-status',form.closest('.assignment'));if(badge){badge.className='badge badge-selected assignment-status';badge.textContent='Assigned';}}));
  $$('[data-set-default]').forEach(b=>b.addEventListener('click',()=>{$$('.address-card').forEach(a=>a.classList.remove('default'));const c=b.closest('.address-card');c.classList.add('default');$$('[data-default-badge]').forEach(x=>x.remove());c.querySelector('.address-type').insertAdjacentHTML('beforeend','<span class="badge badge-selected" data-default-badge>Default</span>');showToast('Default address updated');}));
  $$('[data-add-address]').forEach(b=>b.addEventListener('click',()=>$('#address-modal')?.classList.add('open')));

  // Password strength.
  $$('[data-password-strength]').forEach(input=>input.addEventListener('input',()=>{const v=input.value;let level=v.length<6?'weak':(/[A-Z]/.test(v)&&/[0-9]/.test(v)&&/[^A-Za-z0-9]/.test(v)&&v.length>=10?'strong':'medium');const meter=$('#password-strength');if(meter){meter.className=`strength ${level}`;$('[data-strength-label]').textContent=level[0].toUpperCase()+level.slice(1);}}));

  // Global search provides useful feedback without a backend.
  $('#global-search')?.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();showToast(`Searching for “${e.target.value}”`,'Use the page filters to narrow results.','info');}});

  // Initial state for selected vendors.
  const selectedJobs=JSON.parse(localStorage.getItem('fixora-job-vendors')||'[]');
  $$('[data-select-job]').forEach(btn=>{if(selectedJobs.includes(btn.dataset.selectJob)){btn.classList.remove('btn-primary');btn.classList.add('btn-soft');btn.innerHTML=`${icon('check')} Selected`;}});
  const selectedQuick=localStorage.getItem('fixora-quick-vendor');
  if(selectedQuick) $$('[data-accept-quick]').forEach(b=>{if(b.dataset.acceptQuick===selectedQuick)b.innerHTML=`${icon('check')} Vendor accepted`;});

  // Expose helpers for small page scripts.
  window.Fixora={icon,openModal:openGlobalModal,closeModal,showToast};
})();
