// Sugu Services - Main Application Logic & Urban Company Style Flow

let appState = {
  currentRoute: 'home', // 'home' | 'quick-service' | 'bidding'
  selectedCategoryId: null,
  selectedSubcategoryId: null,
  cart: [],
  appliedCoupon: null,
  userLocation: (window.SERVER_USER_LOCATION && window.SERVER_USER_LOCATION.trim()) || localStorage.getItem("sugu_user_location") || "Ranchi, Jharkhand",
  activeVideo: null,
  biddingJobs: (window.DB_BIDDING_JOBS && Array.isArray(window.DB_BIDDING_JOBS) && window.DB_BIDDING_JOBS.length > 0)
    ? window.DB_BIDDING_JOBS
    : ((typeof SUGU_DATA !== 'undefined' && SUGU_DATA.biddingDemo && Array.isArray(SUGU_DATA.biddingDemo.activeJobs)) ? JSON.parse(JSON.stringify(SUGU_DATA.biddingDemo.activeJobs)) : []),
  biddingTab: 'tenders', // 'tenders' | 'post-job' | 'templates'
  biddingFilter: 'all', // 'all' | 'recommended' | 'lowest' | 'highest' | 'top_rated' | 'fastest'
  biddingStatusFilter: 'all', // 'all' | 'with_quotes' | 'awaiting'
  biddingCategoryFilter: 'all', // 'all' | category name
  biddingSelectedCategory: null,
  biddingSelectedSize: '3 BHK',
  biddingSelectedUrgency: 'Within 1 Week',
  biddingSelectedBudget: '₹20,000 - ₹35,000',
  bookingStep: 1,
  selectedSlotDate: "Today",
  selectedSlotTime: "02:00 PM - 04:00 PM",
  assignedPartner: null,
  biddingPage: 1,
  biddingPerPage: 5,
  qsCategoryPage: 1,
  qsCategoryPerPage: 6,
  qsServicesPage: 1,
  qsServicesPerPage: 4,
  // Women's Beauty Service Dual Navigation State
  beautyMode: 'home', // 'home' | 'parlour'
  selectedParlourId: null,
  selectedParlourService: null,
  selectedParlourStylist: 'Senior Stylist',
  selectedParlourSlotDate: 'Today',
  selectedParlourSlotTime: '02:00 PM - 03:00 PM'
};

// ----------------------------------------------------
// DYNAMIC CATEGORY & LOCATION HELPERS
// ----------------------------------------------------
function findCategory(catId) {
  if (!catId || !window.SUGU_DATA || !Array.isArray(SUGU_DATA.categories)) return null;
  const s = String(catId).toLowerCase().trim();
  if (s === '37' || s === 'beauty_wellness' || s.includes('beauty')) {
    const bCat = SUGU_DATA.categories.find(c => c.id === 'beauty_wellness' || c.isBeautyHub || String(c.id) === '37' || String(c.dbId) === '37');
    if (bCat) return bCat;
  }
  return SUGU_DATA.categories.find(c => 
    String(c.id).toLowerCase() === s || 
    (c.dbId && String(c.dbId).toLowerCase() === s) ||
    (c.legacyId && c.legacyId.toLowerCase() === s) ||
    (c.name && c.name.toLowerCase().trim() === s) ||
    (c.name && c.name.toLowerCase().includes(s))
  ) || null;
}

function syncDynamicCategories() {
  if (!window.DB_CATEGORIES || !Array.isArray(window.DB_CATEGORIES) || window.DB_CATEGORIES.length === 0) {
    return;
  }

  const dbCats = window.DB_CATEGORIES;
  const existingMap = new Map();
  if (window.SUGU_DATA && Array.isArray(SUGU_DATA.categories)) {
    SUGU_DATA.categories.forEach(c => {
      if (c.id) existingMap.set(String(c.id).toLowerCase(), c);
      if (c.name) existingMap.set(c.name.toLowerCase().trim(), c);
    });
  }

  function findBestTemplate(dbName) {
    const lower = (dbName || '').toLowerCase().trim();
    if (existingMap.has(lower)) return existingMap.get(lower);
    for (const [key, tpl] of existingMap.entries()) {
      if (lower.includes(key) || key.includes(lower)) return tpl;
    }
    if (lower.includes('plumb')) return existingMap.get('plumbing');
    if (lower.includes('electr')) return existingMap.get('electrical');
    if (lower.includes('carpent')) return existingMap.get('carpentry');
    if (lower.includes('appliance') || lower.includes('ac')) return existingMap.get('ac_services');
    if (lower.includes('clean')) return existingMap.get('cleaning');
    if (lower.includes('pest')) return existingMap.get('pest_control');
    if (lower.includes('paint')) return existingMap.get('painting_upgrade');
    if (lower.includes('renov')) return existingMap.get('home_renovation');
    if (lower.includes('beauty') || lower.includes('salon') || lower.includes('spa')) {
      return existingMap.get('beauty_wellness') || existingMap.get('womens_salon_spa');
    }
    return null;
  }

  const synchronized = [];

  dbCats.forEach(dbCat => {
    const strId = String(dbCat.id);
    const tpl = findBestTemplate(dbCat.name);

    let subcategories = [];
    if (dbCat.subcategories && dbCat.subcategories.length > 0) {
      subcategories = dbCat.subcategories.map(s => {
        const sId = 'sub_' + s.id;
        let items = [];
        if (tpl && tpl.subcategories) {
          const matchingSub = tpl.subcategories.find(ts => 
            (ts.name || '').toLowerCase().includes(s.name.toLowerCase()) || 
            s.name.toLowerCase().includes((ts.name || '').toLowerCase())
          );
          if (matchingSub && matchingSub.items) {
            items = JSON.parse(JSON.stringify(matchingSub.items));
          }
        }
        if (items.length === 0) {
          items = [
            {
              id: `${sId}_std`,
              title: `${s.name} Inspection & Repair`,
              rating: "4.86",
              reviews: "150+",
              price: dbCat.min_price || 249,
              originalPrice: Math.round((dbCat.min_price || 249) * 1.3),
              time: "30 mins",
              badge: "Standard",
              image: dbCat.image || (tpl ? `/static/assets/icons/${tpl.iconFile}` : "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80"),
              features: [
                "Comprehensive doorstep inspection",
                "Verified certified professional",
                "Standard manufacturer components used",
                "30-day Sugu service guarantee"
              ]
            }
          ];
        }
        return {
          id: sId,
          name: s.name,
          items: items
        };
      });
    } else if (tpl && tpl.subcategories && tpl.subcategories.length > 0) {
      subcategories = JSON.parse(JSON.stringify(tpl.subcategories));
    } else {
      subcategories = [
        {
          id: `general_${strId}`,
          name: `Standard ${dbCat.name}`,
          items: [
            {
              id: `item_${strId}_1`,
              title: `General ${dbCat.name} Consultation & Service`,
              rating: "4.88",
              reviews: "210+",
              price: dbCat.min_price || 199,
              originalPrice: Math.round((dbCat.min_price || 199) * 1.35),
              time: "30 mins",
              badge: "Instant",
              image: dbCat.image || "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
              features: [
                "Instant 15-minute pro assignment",
                "Standardized upfront pricing",
                "30-day rework warranty"
              ]
            }
          ]
        }
      ];
    }

    // If DB category has live QuickService items from backend, attach them to the first subcategory
    if (dbCat.services && dbCat.services.length > 0) {
      const dbItems = dbCat.services.map(qs => ({
        id: `qs_${qs.id}`,
        title: qs.title,
        rating: "4.87",
        reviews: "120+",
        price: qs.price,
        originalPrice: Math.round(qs.price * 1.3),
        time: "45 mins",
        badge: "Verified",
        image: qs.image || dbCat.image || "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
        desc: qs.description,
        features: [
          "Doorstep service by verified vendor",
          "Transparent pricing with no hidden charges",
          "30-day Sugu guarantee included"
        ]
      }));
      if (subcategories[0]) {
        subcategories[0].items = [...dbItems, ...subcategories[0].items];
      }
    }

    const isBeauty = (dbCat.name && dbCat.name.toLowerCase().includes('beauty')) || strId === '37' || (tpl && (tpl.id === 'beauty_wellness' || tpl.isBeautyHub));
    const catObj = {
      id: isBeauty ? 'beauty_wellness' : strId,
      dbId: strId,
      legacyId: tpl ? tpl.id : null,
      name: isBeauty ? "Beauty & Spa" : dbCat.name,
      iconFile: dbCat.image ? dbCat.image : (tpl ? tpl.iconFile : 'womens_salon_spa.png'),
      isCustomImage: !!dbCat.image,
      icon_class: dbCat.icon_class || 'bi-tools',
      tagline: tpl ? tpl.tagline : `Verified ${dbCat.name} Services at Transparent Pricing`,
      rating: tpl ? tpl.rating : "4.91 (4.2M Reviews)",
      startingPrice: dbCat.min_price ? `Starts ₹${dbCat.min_price}` : (tpl ? tpl.startingPrice : "Starts ₹249"),
      isBeautyHub: isBeauty,
      subcategories: isBeauty ? [] : subcategories,
      parlours: (tpl && tpl.parlours) ? tpl.parlours : []
    };

    synchronized.push(catObj);
  });

  // Retain women's and men's salon catalogs so direct selection and toggling work seamlessly
  const womenTpl = existingMap.get('womens_salon_spa');
  const menTpl = existingMap.get('mens_salon_massage');
  if (womenTpl && !synchronized.some(c => c.id === 'womens_salon_spa')) {
    synchronized.push(womenTpl);
  }
  if (menTpl && !synchronized.some(c => c.id === 'mens_salon_massage')) {
    synchronized.push(menTpl);
  }

  // CRITICAL: Replace SUGU_DATA.categories with dynamic categories + beauty experiences!
  SUGU_DATA.categories = synchronized;

  // Set default bidding category to the first dynamic category
  if (synchronized.length > 0 && !appState.biddingSelectedCategory) {
    appState.biddingSelectedCategory = synchronized[0].id;
  }
}

// ----------------------------------------------------
// LOCATION MANAGEMENT & HIGH PRECISION LIVE GPS FETCH
// ----------------------------------------------------
function initLocationDetection() {
  const headerText = document.getElementById("header-location-text");
  const stored = localStorage.getItem("sugu_user_location");

  if (stored && stored.trim().length > 0 && stored !== "Detecting...") {
    appState.userLocation = stored;
    if (headerText) headerText.innerText = stored;
    return;
  }

  if (window.SERVER_USER_LOCATION && window.SERVER_USER_LOCATION.trim().length > 0) {
    const sLoc = window.SERVER_USER_LOCATION.trim();
    appState.userLocation = sLoc;
    if (headerText) headerText.innerText = sLoc;
    localStorage.setItem("sugu_user_location", sLoc);
    return;
  }

  // Auto-detect via live GPS / IP in background
  detectUserLiveLocation({ silent: true });
}

async function detectUserLiveLocation(options = {}) {
  const silent = !!options.silent;
  const headerText = document.getElementById("header-location-text");
  const gpsIcon = document.getElementById("modal-gps-icon");
  const gpsText = document.getElementById("modal-gps-text");
  const gpsSub = document.getElementById("modal-gps-sub");

  if (!silent) {
    if (headerText) headerText.innerText = "Locating GPS...";
    if (gpsText) gpsText.innerText = "Requesting device GPS...";
    if (gpsSub) gpsSub.innerText = "Please allow location access if prompted";
  }

  function applyLocation(locName, fullData) {
    appState.userLocation = locName;
    if (headerText) headerText.innerText = locName;
    localStorage.setItem("sugu_user_location", locName);

    if (!silent) {
      if (gpsText) gpsText.innerText = "Location Found!";
      if (gpsSub) gpsSub.innerText = locName;
      showToast(`Location updated to ${locName}`);
      setTimeout(() => {
        closeLocationPicker();
        resetGpsButton();
      }, 700);
    }
    renderApp();
  }

  function resetGpsButton() {
    if (gpsText) gpsText.innerText = "Use My Current Location";
    if (gpsSub) gpsSub.innerText = "High accuracy GPS & reverse geocoding";
  }

  async function fallbackToIp() {
    try {
      const res = await fetch("/api/detect-location/");
      const data = await res.json();
      const locStr = (data.city && data.state) ? `${data.city}, ${data.state}` : (data.name || "Ranchi, Jharkhand");
      applyLocation(locStr, data);
    } catch (e) {
      console.warn("IP location fallback failed:", e);
      if (!localStorage.getItem("sugu_user_location")) {
        applyLocation("Ranchi, Jharkhand");
      }
      if (!silent) resetGpsButton();
    }
  }

  if (!navigator.geolocation) {
    fallbackToIp();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      if (!silent && gpsText) gpsText.innerText = "Pinpointing address...";

      try {
        const res = await fetch(`/api/detect-location/?lat=${lat}&lon=${lon}`);
        const data = await res.json();
        const displayLoc = data.primary ? (data.city ? `${data.primary}, ${data.city}` : data.primary) : (data.name || `${data.city}, ${data.state}`);
        applyLocation(displayLoc, data);
      } catch (err) {
        console.warn("Reverse geocode failed, using IP fallback:", err);
        fallbackToIp();
      }
    },
    (err) => {
      console.warn("HTML5 Geolocation error, falling back to IP:", err.message);
      fallbackToIp();
    },
    {
      enableHighAccuracy: true,
      timeout: 8000,
      maximumAge: 60000
    }
  );
}

function filterModalCities(query) {
  const q = (query || '').toLowerCase().trim();
  const items = document.querySelectorAll(".modal-city-item");
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    if (!q || text.includes(q)) {
      item.style.display = "flex";
    } else {
      item.style.display = "none";
    }
  });
}

// Initialize app when DOM is loaded
function initApplication() {
  if (window.DB_BIDDING_JOBS && Array.isArray(window.DB_BIDDING_JOBS) && window.DB_BIDDING_JOBS.length > 0) {
    appState.biddingJobs = window.DB_BIDDING_JOBS;
  } else if ((!appState.biddingJobs || appState.biddingJobs.length === 0) && typeof SUGU_DATA !== 'undefined' && SUGU_DATA.biddingDemo) {
    appState.biddingJobs = JSON.parse(JSON.stringify(SUGU_DATA.biddingDemo.activeJobs || []));
  }
  if (!appState.biddingTab) {
    appState.biddingTab = 'tenders';
  }
  try { initThreeJsHero(); } catch (e) { console.error("ThreeJS error:", e); }
  try { syncDynamicCategories(); } catch (e) { console.error("syncDynamicCategories error:", e); }
  try { initLocationDetection(); } catch (e) { console.error("Location error:", e); }
  try { initLucideIcons(); } catch (e) { console.error("Lucide error:", e); }
  try { setupEventListeners(); } catch (e) { console.error("Listeners error:", e); }
  renderApp();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApplication);
} else {
  initApplication();
}

function initLucideIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

// ----------------------------------------------------
// THREE.JS 3D HERO CANVAS
// ----------------------------------------------------
function initThreeJsHero() {
  const container = document.getElementById("threejs-hero-canvas");
  if (!container || !window.THREE) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 25;

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
  scene.add(ambientLight);

  const dirLight1 = new THREE.DirectionalLight(0x81007F, 2.5);
  dirLight1.position.set(20, 20, 20);
  scene.add(dirLight1);

  const dirLight2 = new THREE.DirectionalLight(0xc026d3, 1.8);
  dirLight2.position.set(-20, -10, 15);
  scene.add(dirLight2);

  // Floating 3D Geometries with glossy material
  const group = new THREE.Group();
  scene.add(group);

  const material1 = new THREE.MeshPhysicalMaterial({
    color: 0x81007F,
    roughness: 0.15,
    metalness: 0.1,
    transmission: 0.6,
    ior: 1.5,
    transparent: true,
    opacity: 0.85
  });

  const material2 = new THREE.MeshStandardMaterial({
    color: 0xd946ef,
    roughness: 0.25,
    metalness: 0.4
  });

  const material3 = new THREE.MeshStandardMaterial({
    color: 0xf59e0b,
    roughness: 0.3,
    metalness: 0.2
  });

  // Torus Knot
  const knotGeo = new THREE.TorusKnotGeometry(3.5, 0.9, 80, 16);
  const knot = new THREE.Mesh(knotGeo, material1);
  knot.position.set(16, 4, -4);
  group.add(knot);

  // Icosahedron
  const icoGeo = new THREE.IcosahedronGeometry(2.5, 0);
  const ico = new THREE.Mesh(icoGeo, material2);
  ico.position.set(-16, -2, -2);
  group.add(ico);

  // Cylinder ring
  const cylGeo = new THREE.TorusGeometry(3.2, 0.6, 16, 48);
  const ring = new THREE.Mesh(cylGeo, material3);
  ring.position.set(12, -8, -5);
  group.add(ring);

  // Sparkle floating particles
  const particleCount = 45;
  const particleGeo = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount * 3; i += 3) {
    particlePositions[i] = (Math.random() - 0.5) * 50;
    particlePositions[i + 1] = (Math.random() - 0.5) * 35;
    particlePositions[i + 2] = (Math.random() - 0.5) * 30;
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

  const particleMat = new THREE.PointsMaterial({
    size: 0.45,
    color: 0xf0abfc,
    transparent: true,
    opacity: 0.8
  });
  const particles = new THREE.Points(particleGeo, particleMat);
  group.add(particles);

  // Mouse interaction
  let mouseX = 0, mouseY = 0;
  window.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  // Resize handler
  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation Loop
  function animate() {
    requestAnimationFrame(animate);

    knot.rotation.x += 0.005;
    knot.rotation.y += 0.008;

    ico.rotation.x -= 0.006;
    ico.rotation.y += 0.007;

    ring.rotation.x += 0.008;
    ring.rotation.z += 0.004;

    group.rotation.y += (mouseX * 0.2 - group.rotation.y) * 0.05;
    group.rotation.x += (-mouseY * 0.15 - group.rotation.x) * 0.05;

    renderer.render(scene, camera);
  }
  animate();
}

// ----------------------------------------------------
// ROUTING & APP RENDER
// ----------------------------------------------------
function switchRoute(route, categoryId = null) {
  if (categoryId === 'ac_appliance') categoryId = 'ac_services';
  appState.currentRoute = route;
  if (categoryId) {
    const cat = findCategory(categoryId);
    if (cat) {
      appState.selectedCategoryId = cat.id;
      if (cat.subcategories && cat.subcategories.length > 0) {
        appState.selectedSubcategoryId = cat.subcategories[0].id;
      }
    } else {
      appState.selectedCategoryId = categoryId;
    }
  } else if (route === 'quick-service' && !appState.selectedCategoryId) {
    // If opening quick service without specific category, default to category overview
    appState.selectedCategoryId = null;
  }

  // Auto-close mobile drawer if open
  const drawer = document.getElementById("mobile-nav-drawer");
  if (drawer && !drawer.classList.contains("hidden")) {
    drawer.classList.add("hidden");
    const icon = document.getElementById("mobile-menu-icon");
    if (icon) icon.setAttribute("data-lucide", "menu");
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
  renderApp();
}

function renderApp() {
  const homeView = document.getElementById("view-home");
  const quickServiceView = document.getElementById("view-quick-service");
  const biddingView = document.getElementById("view-bidding");

  // Nav Links state
  updateNavState();

  // Hide all views first
  homeView.classList.add("hidden");
  quickServiceView.classList.add("hidden");
  biddingView.classList.add("hidden");

  if (appState.currentRoute === 'home') {
    homeView.classList.remove("hidden");
    renderHomeView();
  } else if (appState.currentRoute === 'quick-service') {
    quickServiceView.classList.remove("hidden");
    renderQuickServiceView();
  } else if (appState.currentRoute === 'bidding') {
    biddingView.classList.remove("hidden");
    renderBiddingView();
  }

  renderFloatingCart();
  initLucideIcons();
}

function updateNavState() {
  const navBtns = document.querySelectorAll(".nav-mode-btn");
  navBtns.forEach(btn => {
    const mode = btn.getAttribute("data-mode");
    if (mode === appState.currentRoute) {
      btn.classList.add("bg-sugu-blue", "text-white", "shadow-md");
      btn.classList.remove("text-slate-600", "hover:bg-slate-200", "hover:bg-slate-100", "bg-sky-600");
      const gavel = btn.querySelector('[data-lucide="gavel"]');
      if (gavel) {
        gavel.classList.remove("text-sugu-blue");
        gavel.classList.add("text-white");
      }
    } else {
      btn.classList.remove("bg-sugu-blue", "bg-sky-600", "text-white", "shadow-md");
      btn.classList.add("text-slate-600", "hover:bg-slate-200");
      const gavel = btn.querySelector('[data-lucide="gavel"]');
      if (gavel) {
        gavel.classList.remove("text-white");
        gavel.classList.add("text-sugu-blue");
      }
    }
  });

  // Update cart badge
  const totalCartQty = appState.cart.reduce((sum, item) => sum + item.quantity, 0);
  const cartBadge = document.getElementById("nav-cart-badge");
  if (cartBadge) {
    cartBadge.innerText = totalCartQty;
    if (totalCartQty > 0) {
      cartBadge.classList.remove("hidden");
    } else {
      cartBadge.classList.add("hidden");
    }
  }

  // Update mobile bottom nav tabs
  const bottomTabs = document.querySelectorAll(".mobile-bottom-tab");
  bottomTabs.forEach(tab => {
    const mode = tab.getAttribute("data-mode");
    if (mode === appState.currentRoute) {
      tab.classList.add("text-sugu-blue", "font-bold");
      tab.classList.remove("text-slate-500", "font-medium");
    } else {
      tab.classList.remove("text-sugu-blue", "font-bold");
      tab.classList.add("text-slate-500", "font-medium");
    }
  });

  // Update location text in header and drawer
  const locEl = document.getElementById("header-location-text");
  if (locEl) locEl.innerText = appState.userLocation;
  const drawerLoc = document.getElementById("drawer-location-text");
  if (drawerLoc) drawerLoc.innerText = appState.userLocation;
}

// ----------------------------------------------------
// 1. HOME VIEW RENDER
// ----------------------------------------------------
function renderHomeView() {
  // Render Offers Section
  const offersContainer = document.getElementById("home-offers-grid");
  if (offersContainer) {
    offersContainer.innerHTML = SUGU_DATA.offers.map(offer => `
      <div class="relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br ${offer.color} text-white shadow-xl hover:-translate-y-1.5 transition-all duration-300">
        <div class="absolute -right-6 -bottom-6 w-28 h-28 bg-white/10 rounded-full blur-xl pointer-events-none"></div>
        <div class="flex items-center justify-between mb-3">
          <span class="px-2.5 py-1 text-xs font-bold uppercase tracking-wider bg-white/20 backdrop-blur rounded-full">${offer.tag}</span>
          <span class="text-xs font-semibold text-white/80">Min ${offer.minOrder}</span>
        </div>
        <h4 class="text-2xl font-bold font-heading mb-1">${offer.title}</h4>
        <p class="text-sm text-white/90 mb-4">${offer.desc}</p>
        <div class="flex items-center justify-between pt-3 border-t border-white/20">
          <div class="flex items-center space-x-2">
            <span class="text-xs text-white/80">Code:</span>
            <span class="font-mono font-bold bg-white/25 px-2.5 py-0.5 rounded text-sm tracking-wider">${offer.code}</span>
          </div>
          <button onclick="copyPromoCode('${offer.code}')" class="px-3 py-1.5 text-xs font-semibold bg-white text-slate-900 rounded-lg hover:bg-slate-100 transition shadow">
            Copy
          </button>
        </div>
      </div>
    `).join("");
  }

  // Render Video Testimonials
  const videoGrid = document.getElementById("home-videos-grid");
  if (videoGrid) {
    const listToRender = (window.DB_VIDEOS && Array.isArray(window.DB_VIDEOS) && window.DB_VIDEOS.length > 0)
      ? window.DB_VIDEOS
      : (typeof SUGU_DATA !== 'undefined' ? SUGU_DATA.videos : []);

    videoGrid.innerHTML = listToRender.map(v => {
      const ratingStars = Array(Math.min(5, Math.max(1, Math.round(Number(v.rating) || 5)))).fill('<i data-lucide="star" class="w-4 h-4 fill-amber-400"></i>').join("");
      const thumb = v.thumbnail || "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80";
      const tag = v.service || v.service_tag || "Home Service";
      return `
      <div class="group relative rounded-2xl overflow-hidden bg-white shadow-lg border border-slate-200 hover:shadow-2xl transition duration-300">
        <div class="relative h-56 overflow-hidden cursor-pointer" onclick="openVideoModal('${v.id}')">
          <img src="${thumb}" alt="${v.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/30 to-transparent"></div>
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-14 h-14 rounded-full bg-sky-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:bg-sky-500 transition">
              <i data-lucide="play" class="w-7 h-7 fill-white translate-x-0.5"></i>
            </div>
          </div>
          <span class="absolute bottom-3 right-3 px-2 py-0.5 text-xs font-semibold bg-slate-900/80 backdrop-blur text-white rounded">
            ${v.duration}
          </span>
          <span class="absolute top-3 left-3 px-2.5 py-1 text-xs font-bold bg-sky-600 text-white rounded-full">
            ${tag}
          </span>
        </div>
        <div class="p-5">
          <div class="flex items-center space-x-1 text-amber-500 mb-2">
            ${ratingStars}
          </div>
          <h4 class="font-bold text-slate-800 text-lg mb-2 line-clamp-1">${v.title}</h4>
          <p class="text-sm text-slate-600 italic mb-4 line-clamp-2">"${v.quote}"</p>
          <div class="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100">
            <span class="font-semibold text-slate-700">${v.author}</span>
            <span class="flex items-center"><i data-lucide="map-pin" class="w-3.5 h-3.5 mr-1 text-sky-500"></i>${v.city}</span>
          </div>
        </div>
      </div>
    `}).join("");
    if (window.lucide && typeof lucide.createIcons === 'function') {
      lucide.createIcons();
    }
  }

  // Render Customer Reviews Grid (Dynamic from Super Admin CMS DB_TESTIMONIALS)
  const reviewsGrid = document.getElementById("home-reviews-grid");
  if (reviewsGrid) {
    const listToRender = (window.DB_TESTIMONIALS && Array.isArray(window.DB_TESTIMONIALS) && window.DB_TESTIMONIALS.length > 0)
      ? window.DB_TESTIMONIALS
      : SUGU_DATA.reviews;

    reviewsGrid.innerHTML = listToRender.map(r => {
      const starCount = Math.min(5, Math.max(1, Math.round(Number(r.rating) || 5)));
      const starsHtml = Array.from({ length: starCount }).map(() => '<i data-lucide="star" class="w-4 h-4 fill-amber-400 text-amber-400"></i>').join("");
      
      const initials = (r.name || 'User')
        .split(' ')
        .filter(Boolean)
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();

      const avatarHtml = r.avatar
        ? `<img src="${r.avatar}" alt="${r.name}" class="w-12 h-12 rounded-full object-cover border-2 border-sky-500 shadow-sm" onerror="this.outerHTML='<div class=\\\'w-12 h-12 rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 text-white font-bold flex items-center justify-center text-sm border-2 border-sky-400 shadow-sm\\\'>${initials}</div>'">`
        : `<div class="w-12 h-12 rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 text-white font-bold flex items-center justify-center text-sm border-2 border-sky-400 shadow-sm">${initials}</div>`;

      const roleOrLocation = r.role || r.city || 'Homeowner, Ranchi';
      const badgeText = r.badge || 'Verified Customer';
      const serviceName = r.service || 'Home Service';
      const dateText = r.date || 'Verified';

      return `
      <div class="p-6 rounded-2xl bg-white border border-slate-200 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3 min-w-0 pr-2">
              ${avatarHtml}
              <div class="min-w-0">
                <h5 class="font-bold text-slate-900 leading-tight truncate">${r.name}</h5>
                <span class="text-xs text-slate-500 block truncate">${roleOrLocation}</span>
              </div>
            </div>
            <span class="px-2 py-0.5 text-[11px] font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap flex-shrink-0 self-start">
              ${badgeText}
            </span>
          </div>
          <div class="flex items-center space-x-1 text-amber-400 mb-3">
            ${starsHtml}
          </div>
          <p class="text-sm text-slate-700 leading-relaxed">"${r.comment || ''}"</p>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
          <span>Service: <strong class="text-slate-600">${serviceName}</strong></span>
          <span>${dateText}</span>
        </div>
      </div>
    `;
    }).join("");
  }

  // Render How Quick Service Works vs Bidding Works
  renderHowItWorks();
}

function renderHowItWorks() {
  const qsContainer = document.getElementById("how-qs-steps");
  const biddingContainer = document.getElementById("how-bidding-steps");

  if (qsContainer) {
    qsContainer.innerHTML = SUGU_DATA.howItWorks.quickService.map(s => `
      <div class="p-3.5 sm:p-5 rounded-xl sm:rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition">
        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-sky-100 text-sky-700 font-bold flex items-center justify-center mb-2.5 sm:mb-3 text-xs sm:text-sm">
          ${s.step}
        </div>
        <h5 class="font-bold text-slate-900 text-sm sm:text-base mb-1">${s.title}</h5>
        <p class="text-xs text-slate-600 leading-relaxed">${s.desc}</p>
      </div>
    `).join("");
  }

  if (biddingContainer) {
    biddingContainer.innerHTML = SUGU_DATA.howItWorks.bidding.map(s => `
      <div class="p-3.5 sm:p-5 rounded-xl sm:rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition">
        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-amber-100 text-amber-700 font-bold flex items-center justify-center mb-2.5 sm:mb-3 text-xs sm:text-sm">
          ${s.step}
        </div>
        <h5 class="font-bold text-slate-900 text-sm sm:text-base mb-1">${s.title}</h5>
        <p class="text-xs text-slate-600 leading-relaxed">${s.desc}</p>
      </div>
    `).join("");
  }
}

// ----------------------------------------------------
// 2. QUICK SERVICE VIEW (URBAN COMPANY NAVIGATION & FLOW)
// ----------------------------------------------------
function renderQuickServiceView() {
  const categoryGridSection = document.getElementById("qs-category-grid-section");
  const ucDetailSection = document.getElementById("qs-uc-detail-section");

  if (!appState.selectedCategoryId) {
    // Show 12 3D Category Cards Grid (The exact sliced icons from user image!)
    categoryGridSection.classList.remove("hidden");
    ucDetailSection.classList.add("hidden");
    render12CategoryIcons();
  } else {
    // Show Urban Company Style Flow: Subcategories, Services list, Add to cart
    categoryGridSection.classList.add("hidden");
    ucDetailSection.classList.remove("hidden");
    renderUrbanCompanyDetailFlow();
  }
}

function render12CategoryIcons() {
  const container = document.getElementById("qs-12-icons-grid");
  const paginationContainer = document.getElementById("qs-categories-pagination");
  if (!container) return;

  // Filter out separate gender categories so Beauty & Spa represents both in the master 12 grid
  const displayCats = SUGU_DATA.categories.filter(c => c.id !== 'womens_salon_spa' && c.id !== 'mens_salon_massage');

  const totalCats = displayCats.length;
  const perPage = appState.qsCategoryPerPage || 6;
  const totalPages = Math.ceil(totalCats / perPage) || 1;
  if (appState.qsCategoryPage > totalPages) appState.qsCategoryPage = totalPages;
  if (appState.qsCategoryPage < 1) appState.qsCategoryPage = 1;
  const startIdx = (appState.qsCategoryPage - 1) * perPage;
  const endIdx = Math.min(startIdx + perPage, totalCats);
  const pagedCats = displayCats.slice(startIdx, endIdx);

  container.innerHTML = pagedCats.map(cat => {
    const iconFile = cat.iconFile || 'painting_upgrade.png';
    const imgSrc = cat.isCustomImage ? iconFile : `/static/assets/icons/${iconFile}`;
    const imgHtml = `<img src="${imgSrc}" alt="${cat.name}" class="w-12 h-12 sm:w-16 sm:h-16 object-contain rounded-xl group-hover:scale-110 transition-transform duration-300">`;

    return `
    <div onclick="selectCategory('${cat.id}')" class="sugu-category-card group cursor-pointer bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between">
      <div class="relative overflow-hidden bg-slate-50/80 aspect-[4/3] flex items-center justify-center p-2.5 sm:p-3">
        ${imgHtml}
        <div class="absolute inset-0 bg-[#1b75d0]/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      </div>
      <div class="p-2.5 sm:p-3.5 bg-white border-t border-slate-100 flex flex-col justify-between flex-1">
        <div>
          <div class="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span class="flex items-center font-semibold text-amber-600 text-[11px] sm:text-xs">
              <i data-lucide="star" class="w-3 h-3 sm:w-3.5 sm:h-3.5 fill-amber-400 mr-0.5"></i> ${(cat.rating || '4.85').split(' ')[0]}
            </span>
            <span class="text-emerald-700 bg-emerald-50 px-1.5 sm:px-2 py-0.5 rounded-full text-[9px] sm:text-[10px] font-bold border border-emerald-200">15 Min</span>
          </div>
          <h4 class="font-bold text-slate-900 group-hover:text-[#1b75d0] transition text-xs sm:text-sm mb-1 truncate">${cat.name}</h4>
          <p class="text-[10px] sm:text-[11px] text-slate-500 line-clamp-1">${cat.tagline || 'Verified Doorstep Services'}</p>
        </div>
        <div class="mt-2 sm:mt-2.5 pt-1.5 sm:pt-2 border-t border-slate-100 flex items-center justify-between">
          <span class="text-[11px] sm:text-xs font-black text-[#1b75d0]">${cat.startingPrice}</span>
          <span class="text-[11px] sm:text-xs font-bold text-[#1b75d0] flex items-center group-hover:translate-x-1 transition">
            Book <i data-lucide="chevron-right" class="w-3 h-3 sm:w-3.5 sm:h-3.5 ml-0.5"></i>
          </span>
        </div>
      </div>
    </div>
  `;
  }).join("");

  // Pagination bar for Categories Overview if totalPages > 1
  if (paginationContainer) {
    if (totalPages > 1) {
      let pagesHtml = '';
      for (let p = 1; p <= totalPages; p++) {
        const isCur = p === appState.qsCategoryPage;
        pagesHtml += `
          <button onclick="changeQsCategoryPage(${p})" 
            class="w-8 h-8 rounded-xl text-xs font-bold transition flex items-center justify-center border
            ${isCur ? 'bg-sugu-blue text-white border-sugu-blue shadow-sm' : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'}">
            ${p}
          </button>
        `;
      }
      paginationContainer.innerHTML = `
        <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="text-xs text-slate-600 font-medium">
            Showing <strong class="text-slate-900 font-bold">${startIdx + 1}–${endIdx}</strong> of <strong class="text-slate-900 font-bold">${totalCats}</strong> categories (Page ${appState.qsCategoryPage} of ${totalPages})
          </div>
          <div class="flex items-center space-x-1.5">
            <button onclick="changeQsCategoryPage(${appState.qsCategoryPage - 1})" 
              ${appState.qsCategoryPage === 1 ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
              <i data-lucide="chevron-left" class="w-4 h-4"></i>
              <span>Prev</span>
            </button>
            ${pagesHtml}
            <button onclick="changeQsCategoryPage(${appState.qsCategoryPage + 1})" 
              ${appState.qsCategoryPage === totalPages ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
              <span>Next</span>
              <i data-lucide="chevron-right" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      `;
    } else {
      paginationContainer.innerHTML = '';
    }
  }
}

function changeQsCategoryPage(newPage) {
  appState.qsCategoryPage = newPage;
  render12CategoryIcons();
  initLucideIcons();
  const el = document.getElementById("qs-category-grid-section");
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
window.changeQsCategoryPage = changeQsCategoryPage;

function selectCategory(catId) {
  const cat = findCategory(catId);
  if (cat) {
    appState.selectedCategoryId = cat.id;
    if (cat.subcategories && cat.subcategories.length > 0) {
      appState.selectedSubcategoryId = cat.subcategories[0].id;
    }
  } else {
    appState.selectedCategoryId = catId;
  }
  // Reset parlour state cleanly when switching categories
  appState.beautyMode = 'home';
  appState.selectedParlourId = null;
  appState.qsServicesPage = 1;
  renderApp();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderUrbanCompanyDetailFlow() {
  const currentCat = findCategory(appState.selectedCategoryId) || SUGU_DATA.categories[0];
  if (!currentCat) return;
  appState.selectedCategoryId = currentCat.id;

  // Header info
  document.getElementById("uc-cat-title").innerText = currentCat.name;
  document.getElementById("uc-cat-tagline").innerText = currentCat.tagline || 'Verified Doorstep Services';
  document.getElementById("uc-cat-rating").innerHTML = `<i data-lucide="star" class="w-4 h-4 fill-amber-400 text-amber-400 mr-1"></i> ${currentCat.rating || '4.86'}`;
  const catThumb = document.getElementById("uc-cat-icon-thumb");
  if (catThumb) {
    catThumb.src = currentCat.isCustomImage ? currentCat.iconFile : `/static/assets/icons/${currentCat.iconFile}`;
  }

  // Render Horizontal Category Switcher (Urban Company style pill strip)
  const catPillStrip = document.getElementById("uc-category-pills");
  if (catPillStrip) {
    catPillStrip.innerHTML = SUGU_DATA.categories.map(c => `
      <button onclick="selectCategory('${c.id}')" 
        class="flex-shrink-0 flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-semibold transition border 
        ${c.id === currentCat.id ? 'bg-sky-600 text-white border-sky-600 shadow' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}">
        <img src="${c.isCustomImage ? c.iconFile : '/static/assets/icons/' + c.iconFile}" class="w-5 h-5 object-contain rounded-md" alt="${c.name}">
        <span>${c.name}</span>
      </button>
    `).join("");
  }

  // ----------------------------------------------------
  // BEAUTY & GROOMING SERVICES DUAL NAVIGATION LOGIC (WOMEN & MEN)
  // ----------------------------------------------------
  const isBeautyHub = currentCat.id === 'beauty_wellness';
  const isSalon = currentCat.id === 'womens_salon_spa' || currentCat.id === 'mens_salon_massage';
  const isMen = currentCat.id === 'mens_salon_massage';
  const beautyHubView = document.getElementById("beauty-gender-hub-view");
  const beautyGenderToggleBar = document.getElementById("beauty-gender-toggle-bar");
  const beautyModeBar = document.getElementById("beauty-service-mode-bar");
  const standardLayout = document.getElementById("uc-standard-layout");
  const parloursLayout = document.getElementById("beauty-parlours-layout");

  if (isBeautyHub) {
    if (beautyHubView) beautyHubView.classList.remove("hidden");
    if (beautyGenderToggleBar) beautyGenderToggleBar.classList.add("hidden");
    if (beautyModeBar) beautyModeBar.classList.add("hidden");
    if (standardLayout) standardLayout.classList.add("hidden");
    if (parloursLayout) parloursLayout.classList.add("hidden");
    initLucideIcons();
    return;
  } else {
    if (beautyHubView) beautyHubView.classList.add("hidden");
  }

  if (isSalon) {
    if (beautyGenderToggleBar) {
      beautyGenderToggleBar.classList.remove("hidden");
      const toggleWomens = document.getElementById("toggle-womens-btn");
      const toggleMens = document.getElementById("toggle-mens-btn");
      if (toggleWomens && toggleMens) {
        if (isMen) {
          toggleMens.className = "px-4 py-1.5 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 bg-sky-100 text-sky-800 border-2 border-sky-600 shadow-sm";
          toggleWomens.className = "px-4 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 bg-slate-50 text-slate-600 hover:bg-pink-50 hover:text-pink-700 border border-slate-200";
        } else {
          toggleWomens.className = "px-4 py-1.5 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 bg-pink-100 text-pink-800 border-2 border-pink-500 shadow-sm";
          toggleMens.className = "px-4 py-1.5 rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 bg-slate-50 text-slate-600 hover:bg-sky-50 hover:text-sky-700 border border-slate-200";
        }
      }
    }

    if (beautyModeBar) {
      beautyModeBar.classList.remove("hidden");

      // Update text for Women vs Men dynamically
      const homeTitle = document.getElementById("beauty-home-title");
      const homeBadge = document.getElementById("beauty-home-badge");
      const homeDesc = document.getElementById("beauty-home-desc");
      const parlourTitle = document.getElementById("beauty-parlour-title");
      const parlourBadge = document.getElementById("beauty-parlour-badge");
      const parlourDesc = document.getElementById("beauty-parlour-desc");
      const homeIconBox = document.getElementById("beauty-home-icon-box");

      if (isMen) {
        if (homeTitle) homeTitle.innerText = "1. Grooming & Massage at Home";
        if (homeBadge) {
          homeBadge.innerText = "All Services Available";
          homeBadge.className = "px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-sky-100 text-sky-800";
        }
        if (homeDesc) homeDesc.innerText = "Certified male stylist visits your home • Single-use sterilized tools & vacuum";
        if (homeIconBox) homeIconBox.className = "w-12 h-12 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-xl flex-shrink-0";

        if (parlourTitle) parlourTitle.innerText = "2. Premium Barbershop & Lounge";
        if (parlourBadge) parlourBadge.innerText = "Luxury Barbershops";
        if (parlourDesc) parlourDesc.innerText = "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company";
      } else {
        if (homeTitle) homeTitle.innerText = "1. Salon at Home";
        if (homeBadge) {
          homeBadge.innerText = "All Services Available";
          homeBadge.className = "px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-pink-100 text-pink-700";
        }
        if (homeDesc) homeDesc.innerText = "Certified beautician visits your home • 100% sealed mono-kits";
        if (homeIconBox) homeIconBox.className = "w-12 h-12 rounded-2xl bg-pink-100 text-pink-600 flex items-center justify-center font-bold text-xl flex-shrink-0";

        if (parlourTitle) parlourTitle.innerText = "2. Premium Parlour Services";
        if (parlourBadge) parlourBadge.innerText = "Luxury Salon Brands";
        if (parlourDesc) parlourDesc.innerText = "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area";
      }
    }
    
    // Update active beauty mode cards styling
    const homeCard = document.getElementById("beauty-mode-home-card");
    const parlourCard = document.getElementById("beauty-mode-parlour-card");
    const homeCheck = document.getElementById("beauty-home-check");
    const parlourCheck = document.getElementById("beauty-parlour-check");

    if (appState.beautyMode === 'home') {
      if (homeCard) {
        homeCard.className = isMen
          ? "p-5 rounded-3xl border-2 border-sky-600 bg-sky-50/60 shadow-md ring-2 ring-sky-400/20 cursor-pointer transition-all duration-300 flex items-center justify-between"
          : "p-5 rounded-3xl border-2 border-pink-500 bg-pink-50/60 shadow-md ring-2 ring-pink-400/20 cursor-pointer transition-all duration-300 flex items-center justify-between";
      }
      if (parlourCard) {
        parlourCard.className = "p-5 rounded-3xl border-2 border-slate-200 bg-white hover:border-amber-400 hover:bg-amber-50/30 cursor-pointer transition-all duration-300 flex items-center justify-between";
      }
      if (homeCheck) {
        homeCheck.classList.remove("hidden");
        homeCheck.className = `w-6 h-6 rounded-full ${isMen ? 'bg-sky-600' : 'bg-pink-600'} text-white flex items-center justify-center shadow`;
      }
      if (parlourCheck) parlourCheck.classList.add("hidden");

      if (standardLayout) standardLayout.classList.remove("hidden");
      if (parloursLayout) parloursLayout.classList.add("hidden");
    } else {
      if (homeCard) {
        homeCard.className = isMen
          ? "p-5 rounded-3xl border-2 border-slate-200 bg-white hover:border-sky-400 hover:bg-sky-50/30 cursor-pointer transition-all duration-300 flex items-center justify-between"
          : "p-5 rounded-3xl border-2 border-slate-200 bg-white hover:border-pink-400 hover:bg-pink-50/30 cursor-pointer transition-all duration-300 flex items-center justify-between";
      }
      if (parlourCard) {
        parlourCard.className = "p-5 rounded-3xl border-2 border-amber-500 bg-amber-50/60 shadow-md ring-2 ring-amber-400/20 cursor-pointer transition-all duration-300 flex items-center justify-between";
      }
      if (homeCheck) homeCheck.classList.add("hidden");
      if (parlourCheck) parlourCheck.classList.remove("hidden");

      if (standardLayout) standardLayout.classList.add("hidden");
      if (parloursLayout) parloursLayout.classList.remove("hidden");
      renderBeautyParlourFlow(currentCat);
      initLucideIcons();
      return;
    }
  } else {
    if (beautyGenderToggleBar) beautyGenderToggleBar.classList.add("hidden");
    if (beautyModeBar) beautyModeBar.classList.add("hidden");
    if (standardLayout) standardLayout.classList.remove("hidden");
    if (parloursLayout) parloursLayout.classList.add("hidden");
  }

  // Left Sidebar Subcategories (For Home Services & Other Categories)
  const subcatNav = document.getElementById("uc-subcat-nav");
  if (subcatNav) {
    subcatNav.innerHTML = currentCat.subcategories.map(sub => `
      <button onclick="selectSubcategory('${sub.id}')" 
        class="w-full text-left px-4 py-3 rounded-xl text-sm font-semibold transition mb-1 flex items-center justify-between 
        ${sub.id === appState.selectedSubcategoryId ? 'bg-sky-50 text-sky-700 border-l-4 border-sky-600 font-bold' : 'text-slate-600 hover:bg-slate-50'}">
        <span>${sub.name}</span>
        <span class="text-xs px-2 py-0.5 rounded-full ${sub.id === appState.selectedSubcategoryId ? 'bg-sky-200 text-sky-800' : 'bg-slate-100 text-slate-500'}">
          ${sub.items.length}
        </span>
      </button>
    `).join("");
  }

  // Center Feed: Services of the selected subcategory
  const activeSub = currentCat.subcategories.find(s => s.id === appState.selectedSubcategoryId) || currentCat.subcategories[0];
  const itemsContainer = document.getElementById("uc-services-list");
  const paginationContainer = document.getElementById("uc-services-pagination");

  if (itemsContainer && activeSub) {
    const totalItems = activeSub.items.length;
    const perPage = appState.qsServicesPerPage || 4;
    const totalPages = Math.ceil(totalItems / perPage) || 1;
    if (appState.qsServicesPage > totalPages) appState.qsServicesPage = totalPages;
    if (appState.qsServicesPage < 1) appState.qsServicesPage = 1;
    const startIdx = (appState.qsServicesPage - 1) * perPage;
    const endIdx = Math.min(startIdx + perPage, totalItems);
    const pagedItems = activeSub.items.slice(startIdx, endIdx);

    document.getElementById("uc-subcat-heading").innerText = activeSub.name;
    itemsContainer.innerHTML = pagedItems.map(item => {
      const cartItem = appState.cart.find(c => c.item.id === item.id);
      const qty = cartItem ? cartItem.quantity : 0;
      const isWomen = currentCat.id === 'womens_salon_spa';
      const badgeStyle = isWomen ? 'bg-pink-50 text-pink-700 border-pink-200' : (isMen ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-sky-50 text-sky-700 border-sky-200');
      const btnAddClass = isWomen ? 'bg-pink-50 hover:bg-pink-600 text-pink-700 hover:text-white border-pink-600' : (isMen ? 'bg-sky-50 hover:bg-sky-600 text-sky-700 hover:text-white border-sky-600' : 'bg-sky-50 hover:bg-sky-600 text-sky-700 hover:text-white border-sky-600');
      const btnQtyClass = isWomen ? 'bg-pink-600' : 'bg-sky-600';

      return `
        <div class="p-4 sm:p-6 rounded-xl sm:rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col md:flex-row md:items-start justify-between gap-4 sm:gap-6 mb-4">
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-2">
              <span class="px-2.5 py-0.5 text-xs font-bold rounded-full ${badgeStyle} border">${item.badge}</span>
              <span class="flex items-center text-xs font-semibold text-amber-500">
                <i data-lucide="star" class="w-3.5 h-3.5 fill-amber-400 mr-1"></i> ${item.rating} (${item.reviews})
              </span>
            </div>
            <h4 class="text-lg font-bold text-slate-900 mb-1">${item.title}</h4>
            <div class="flex items-center space-x-3 mb-3 text-sm">
              <span class="font-extrabold text-slate-900 text-lg">₹${item.price}</span>
              <span class="text-slate-400 line-through text-xs">₹${item.originalPrice}</span>
              <span class="text-emerald-600 font-semibold text-xs">${Math.round((item.originalPrice - item.price) / item.originalPrice * 100)}% OFF</span>
              <span class="text-slate-300">•</span>
              <span class="text-slate-500 text-xs flex items-center"><i data-lucide="clock" class="w-3.5 h-3.5 mr-1 text-slate-400"></i> ${item.time}</span>
            </div>
            <ul class="space-y-1.5 mb-4">
              ${item.features.map(f => `
                <li class="text-xs text-slate-600 flex items-start">
                  <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-500 mr-2 flex-shrink-0 mt-0.5"></i>
                  <span>${f}</span>
                </li>
              `).join("")}
            </ul>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-sky-600 font-semibold flex items-center cursor-pointer hover:underline" onclick="showItemDetails('${item.id}')">
                View service details & warranty <i data-lucide="chevron-right" class="w-3.5 h-3.5 ml-0.5"></i>
              </span>
            </div>
          </div>

          <div class="flex flex-col items-center justify-between w-full md:w-44 flex-shrink-0">
            <div class="relative w-full h-32 rounded-xl overflow-hidden mb-3 border border-slate-100 shadow-inner">
              <img src="${item.image}" alt="${item.title}" class="w-full h-full object-cover">
            </div>
            ${qty === 0 ? `
              <button onclick="addToCart('${item.id}', '${currentCat.id}')" 
                class="w-full py-2 px-4 rounded-xl ${btnAddClass} font-bold text-sm border-2 transition shadow-sm flex items-center justify-center space-x-1">
                <span>ADD</span> <i data-lucide="plus" class="w-4 h-4"></i>
              </button>
            ` : `
              <div class="w-full flex items-center justify-between ${btnQtyClass} text-white rounded-xl font-bold py-1.5 px-3 shadow-md">
                <button onclick="updateCartQuantity('${item.id}', -1)" class="w-7 h-7 flex items-center justify-center rounded-lg hover:brightness-90 transition">
                  <i data-lucide="minus" class="w-4 h-4"></i>
                </button>
                <span class="text-sm font-extrabold">${qty}</span>
                <button onclick="updateCartQuantity('${item.id}', 1)" class="w-7 h-7 flex items-center justify-center rounded-lg hover:brightness-90 transition">
                  <i data-lucide="plus" class="w-4 h-4"></i>
                </button>
              </div>
            `}
          </div>
        </div>
      `;
    }).join("");

    if (paginationContainer) {
      if (totalPages > 1) {
        let pagesHtml = '';
        for (let p = 1; p <= totalPages; p++) {
          const isCur = p === appState.qsServicesPage;
          pagesHtml += `
            <button onclick="changeQsServicesPage(${p})" 
              class="w-8 h-8 rounded-xl text-xs font-bold transition flex items-center justify-center border
              ${isCur ? 'bg-sugu-blue text-white border-sugu-blue shadow-sm' : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'}">
              ${p}
            </button>
          `;
        }
        paginationContainer.innerHTML = `
          <div class="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="text-xs text-slate-600 font-medium">
              Showing <strong class="text-slate-900 font-bold">${startIdx + 1}–${endIdx}</strong> of <strong class="text-slate-900 font-bold">${totalItems}</strong> services (Page ${appState.qsServicesPage} of ${totalPages})
            </div>
            <div class="flex items-center space-x-1.5">
              <button onclick="changeQsServicesPage(${appState.qsServicesPage - 1})" 
                ${appState.qsServicesPage === 1 ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
                <i data-lucide="chevron-left" class="w-4 h-4"></i>
                <span>Prev</span>
              </button>
              ${pagesHtml}
              <button onclick="changeQsServicesPage(${appState.qsServicesPage + 1})" 
                ${appState.qsServicesPage === totalPages ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
                <span>Next</span>
                <i data-lucide="chevron-right" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        `;
      } else {
        paginationContainer.innerHTML = '';
      }
    }
  }
}

function changeQsServicesPage(newPage) {
  appState.qsServicesPage = newPage;
  renderUrbanCompanyDetailFlow();
  initLucideIcons();
  const el = document.getElementById("uc-services-list");
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
window.changeQsServicesPage = changeQsServicesPage;

// ----------------------------------------------------
// BEAUTY SERVICES DUAL MODE CONTROLLERS & PARLOUR DIRECTORY
// ----------------------------------------------------
function setBeautyServiceMode(mode) {
  appState.beautyMode = mode;
  renderUrbanCompanyDetailFlow();
  initLucideIcons();
  window.scrollTo({ top: 180, behavior: 'smooth' });
}

function selectParlour(parlourId) {
  appState.selectedParlourId = parlourId;
  renderUrbanCompanyDetailFlow();
  initLucideIcons();
  window.scrollTo({ top: 220, behavior: 'smooth' });
}

function backToParloursList() {
  appState.selectedParlourId = null;
  renderUrbanCompanyDetailFlow();
  initLucideIcons();
  window.scrollTo({ top: 200, behavior: 'smooth' });
}

function renderBeautyParlourFlow(currentCat) {
  const container = document.getElementById("beauty-parlours-content");
  if (!container || !currentCat) return;

  const isMen = currentCat.id === 'mens_salon_massage';
  const salonNoun = isMen ? "Luxury Barbershop / Lounge" : "Luxury Parlour";
  const salonPlural = isMen ? "Luxury Barbershops & Lounges" : "Luxury Parlours";
  const parlourTerm = isMen ? "Barbershop" : "Parlour";
  const parlours = currentCat.parlours || [];

  if (!appState.selectedParlourId) {
    // 1. RENDER LIST OF LUXURY PARLOUR / BARBERSHOP NAMES
    container.innerHTML = `
      <div class="max-w-6xl mx-auto">
        <div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-3xl bg-gradient-to-r ${isMen ? 'from-slate-950 via-slate-900 to-amber-950 border border-amber-500/30' : 'from-amber-950 via-slate-900 to-amber-900'} text-white shadow-xl">
          <div>
            <div class="flex items-center space-x-2 mb-1.5">
              <span class="px-2.5 py-0.5 text-xs font-bold bg-amber-500 text-slate-950 rounded-full">In-Salon Visit</span>
              <span class="text-xs text-amber-200">5 Top ${salonPlural} in Bengaluru</span>
            </div>
            <h3 class="text-2xl sm:text-3xl font-bold font-heading text-white">Select a ${salonNoun} Near You</h3>
            <p class="text-xs sm:text-sm text-slate-300 mt-1">Tap any ${parlourTerm.toLowerCase()} name to view their exclusive in-salon treatments, master stylists, and book guaranteed time slots.</p>
          </div>
          <div class="flex items-center space-x-2 bg-white/10 backdrop-blur px-3.5 py-2 rounded-2xl border border-white/15 text-xs text-amber-300 font-semibold flex-shrink-0">
            <i data-lucide="shield-check" class="w-4 h-4 text-emerald-400"></i>
            <span>Zero Waiting Time Guarantee</span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          ${parlours.map(p => `
            <div onclick="selectParlour('${p.id}')" 
              class="bg-white rounded-3xl border border-slate-200 shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer flex flex-col justify-between group">
              <div>
                <div class="relative h-48 overflow-hidden">
                  <img src="${p.image}" alt="${p.name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                  <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent"></div>
                  <span class="absolute top-3 left-3 px-2.5 py-1 text-[11px] font-extrabold uppercase tracking-wider bg-amber-500 text-slate-950 rounded-full shadow">
                    ${p.brandTag}
                  </span>
                  <span class="absolute bottom-3 right-3 px-2.5 py-1 text-xs font-bold bg-slate-900/90 text-white rounded-lg backdrop-blur">
                    📍 ${p.distance}
                  </span>
                </div>

                <div class="p-5">
                  <div class="flex items-center justify-between text-xs text-slate-500 mb-1.5">
                    <span class="font-bold text-amber-600 flex items-center">
                      <i data-lucide="star" class="w-3.5 h-3.5 fill-amber-400 mr-1"></i> ${p.rating}
                    </span>
                    <span class="text-slate-400 flex items-center">
                      <i data-lucide="clock" class="w-3 h-3 mr-1"></i> ${p.timings}
                    </span>
                  </div>

                  <h4 class="text-lg font-bold font-heading text-slate-900 group-hover:text-amber-700 transition leading-snug mb-1">
                    ${p.name}
                  </h4>
                  <p class="text-xs text-slate-600 font-medium mb-3">${p.tagline}</p>
                  <p class="text-xs text-slate-400 flex items-center mb-3">
                    <i data-lucide="map-pin" class="w-3.5 h-3.5 mr-1 text-amber-600 flex-shrink-0"></i> ${p.location}
                  </p>

                  <div class="space-y-1.5 pt-3 border-t border-slate-100">
                    ${p.highlights.map(h => `
                      <span class="inline-block text-[11px] font-semibold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md mr-1 mb-1">
                        ✓ ${h}
                      </span>
                    `).join("")}
                  </div>
                </div>
              </div>

              <div class="p-5 pt-0">
                <button class="w-full py-3 bg-amber-600 group-hover:bg-amber-700 text-white font-bold text-xs rounded-2xl shadow transition flex items-center justify-center space-x-1.5">
                  <span>View ${parlourTerm} Services & Book</span>
                  <i data-lucide="arrow-right" class="w-4 h-4 transform group-hover:translate-x-1 transition"></i>
                </button>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } else {
    // 2. RENDER SELECTED PARLOUR'S EXCLUSIVE SERVICES MENU
    const parlour = parlours.find(p => p.id === appState.selectedParlourId);
    if (!parlour) return;

    container.innerHTML = `
      <div class="max-w-6xl mx-auto">
        <!-- Back Bar -->
        <div class="mb-6 flex items-center justify-between">
          <button onclick="backToParloursList()" 
            class="px-4 py-2 rounded-2xl bg-white hover:bg-slate-100 text-slate-800 text-xs font-bold border border-slate-200 shadow-sm transition flex items-center space-x-2">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
            <span>← Back to All ${salonPlural}</span>
          </button>
          <span class="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
            ✓ Guaranteed In-Salon Time Slot
          </span>
        </div>

        <!-- Parlour Header Banner -->
        <div class="mb-8 rounded-3xl bg-white border border-slate-200 shadow-lg overflow-hidden flex flex-col md:flex-row">
          <div class="md:w-1/3 h-56 md:h-auto relative overflow-hidden">
            <img src="${parlour.image}" alt="${parlour.name}" class="w-full h-full object-cover">
            <span class="absolute top-4 left-4 px-3 py-1 text-xs font-extrabold uppercase tracking-wider bg-amber-500 text-slate-950 rounded-full shadow">
              ${parlour.brandTag}
            </span>
          </div>

          <div class="p-6 md:p-8 md:w-2/3 flex flex-col justify-between">
            <div>
              <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                <h3 class="text-2xl sm:text-3xl font-black font-heading text-slate-900">${parlour.name}</h3>
                <span class="flex items-center text-xs font-bold text-amber-700 bg-amber-50 px-3 py-1 rounded-xl border border-amber-200">
                  <i data-lucide="star" class="w-4 h-4 fill-amber-400 mr-1"></i> ${parlour.rating}
                </span>
              </div>
              <p class="text-xs sm:text-sm text-slate-600 font-medium mb-3">${parlour.tagline}</p>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-500 mb-4">
                <span class="flex items-center"><i data-lucide="map-pin" class="w-4 h-4 mr-1.5 text-amber-600"></i> ${parlour.location} (${parlour.distance})</span>
                <span class="flex items-center"><i data-lucide="clock" class="w-4 h-4 mr-1.5 text-slate-400"></i> ${parlour.timings}</span>
              </div>

              <div class="flex flex-wrap gap-1.5">
                ${parlour.highlights.map(h => `
                  <span class="text-[11px] font-semibold text-amber-900 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
                    ★ ${h}
                  </span>
                `).join("")}
              </div>
            </div>

            <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Selected ${parlourTerm}: <strong class="text-slate-800">${parlour.name}</strong></span>
              <span class="text-sky-600 font-bold">In-Salon Exclusive Menu Below ↓</span>
            </div>
          </div>
        </div>

        <!-- Parlour Exclusive Services Grid -->
        <div>
          <div class="mb-6 flex items-center justify-between">
            <h4 class="text-xl font-bold font-heading text-slate-900 flex items-center">
              <i data-lucide="sparkles" class="w-5 h-5 mr-2 text-amber-600"></i>
              Exclusive Services Offered by ${parlour.name}
            </h4>
            <span class="text-xs text-slate-400">${parlour.services.length} signature ${isMen ? 'grooming services' : 'treatments'}</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            ${parlour.services.map(s => `
              <div class="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group">
                <div>
                  <div class="flex items-start space-x-4 mb-4">
                    <div class="w-20 h-20 rounded-2xl overflow-hidden flex-shrink-0 border border-slate-100 shadow-inner">
                      <img src="${s.image}" alt="${s.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                    </div>
                    <div class="flex-1">
                      <div class="flex items-center space-x-2 mb-1">
                        <span class="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded-full bg-amber-50 text-amber-800 border border-amber-200">${s.category}</span>
                        <span class="text-xs text-slate-400 flex items-center"><i data-lucide="clock" class="w-3 h-3 mr-1"></i> ${s.time}</span>
                      </div>
                      <h5 class="text-base font-bold text-slate-900 leading-snug">${s.title}</h5>
                    </div>
                  </div>

                  <p class="text-xs text-slate-600 leading-relaxed mb-4 bg-slate-50 p-3 rounded-2xl border border-slate-100">${s.desc}</p>
                </div>

                <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span class="text-[10px] uppercase font-bold text-slate-400 block">${parlourTerm} Rate</span>
                    <div class="flex items-baseline space-x-2">
                      <span class="text-xl font-black text-slate-900">₹${s.price}</span>
                      <span class="text-xs text-slate-400 line-through">₹${s.originalPrice}</span>
                    </div>
                  </div>

                  <button onclick="openParlourBookingModal('${s.id}', '${parlour.id}')" 
                    class="py-2.5 px-5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center space-x-1.5">
                    <i data-lucide="calendar" class="w-4 h-4"></i>
                    <span>Book Appointment</span>
                  </button>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      </div>
    `;
  }
}

// ----------------------------------------------------
// PARLOUR APPOINTMENT BOOKING MODAL
// ----------------------------------------------------
function openParlourBookingModal(serviceId, parlourId) {
  const currentCat = SUGU_DATA.categories.find(c => c.id === appState.selectedCategoryId) || 
                     SUGU_DATA.categories.find(c => c.id === 'womens_salon_spa');
  if (!currentCat) return;

  const parlour = (currentCat.parlours || []).find(p => p.id === parlourId);
  if (!parlour) return;

  const service = parlour.services.find(s => s.id === serviceId);
  if (!service) return;

  const isMen = currentCat.id === 'mens_salon_massage';
  appState.selectedParlourService = { service, parlour, isMen };

  const modal = document.getElementById("parlour-booking-modal");
  const modalTitle = document.getElementById("parlour-modal-title");
  const content = document.getElementById("parlour-booking-content");
  if (!modal || !content) return;

  if (modalTitle) {
    modalTitle.innerText = isMen ? "Book Barbershop Appointment" : "Book Parlour Appointment";
  }

  modal.classList.remove("hidden");

  const dates = [
    { label: "Today", date: "2 Oct, Fri" },
    { label: "Tomorrow", date: "3 Oct, Sat" },
    { label: "Sun", date: "4 Oct, Sun" },
    { label: "Mon", date: "5 Oct, Mon" }
  ];

  const slots = [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ];

  content.innerHTML = `
    <div>
      <!-- Parlour & Service Header -->
      <div class="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 mb-5 flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-amber-800">${parlour.name}</span>
          <h4 class="font-bold text-slate-900 text-base leading-snug">${service.title}</h4>
          <span class="text-xs text-slate-500">${service.time} • ₹${service.price}</span>
        </div>
        <span class="text-xs font-bold bg-white text-amber-900 px-3 py-1.5 rounded-xl border border-amber-300 shadow-sm">
          ${parlour.distance}
        </span>
      </div>

      <!-- Stylist Tier Selection -->
      <div class="mb-5">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">1. Select ${isMen ? 'Barber / Stylist' : 'Stylist'} Preference</label>
        <div class="grid grid-cols-2 gap-3">
          <label class="p-3 rounded-2xl border cursor-pointer transition ${appState.selectedParlourStylist === 'Senior Stylist' ? 'border-amber-600 bg-amber-50/60 font-bold' : 'border-slate-200 bg-white hover:bg-slate-50'}">
            <input type="radio" name="parlour_stylist" value="Senior Stylist" checked onchange="appState.selectedParlourStylist='Senior Stylist'" class="sr-only">
            <span class="block text-xs font-bold text-slate-900">${isMen ? 'Senior Barber' : 'Senior Stylist'}</span>
            <span class="block text-[11px] text-slate-500">Certified Expert (Included)</span>
          </label>
          <label class="p-3 rounded-2xl border cursor-pointer transition ${appState.selectedParlourStylist === 'Art Director' ? 'border-amber-600 bg-amber-50/60 font-bold' : 'border-slate-200 bg-white hover:bg-slate-50'}">
            <input type="radio" name="parlour_stylist" value="Art Director" onchange="appState.selectedParlourStylist='Art Director'" class="sr-only">
            <span class="block text-xs font-bold text-slate-900">${isMen ? 'Master Hair Artist' : 'Master Art Director'}</span>
            <span class="block text-[11px] text-amber-700 font-semibold">+₹300 (Celebrity Stylist)</span>
          </label>
        </div>
      </div>

      <!-- Day Selector -->
      <div class="mb-5">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">2. Appointment Day</label>
        <div class="grid grid-cols-4 gap-2">
          ${dates.map(d => `
            <button type="button" onclick="selectParlourDate('${d.label}')" 
              class="p-2.5 rounded-xl border text-center transition ${appState.selectedParlourSlotDate === d.label ? 'border-amber-600 bg-amber-50 font-bold text-amber-900 shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}">
              <span class="block text-xs font-bold">${d.label}</span>
              <span class="block text-[10px] text-slate-400">${d.date}</span>
            </button>
          `).join("")}
        </div>
      </div>

      <!-- Time Slot Selector -->
      <div class="mb-6">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">3. Preferred Time Slot</label>
        <div class="space-y-2 max-h-36 overflow-y-auto pr-1">
          ${slots.map(s => `
            <label class="flex items-center justify-between p-2.5 rounded-xl border cursor-pointer transition ${appState.selectedParlourSlotTime === s ? 'border-amber-600 bg-amber-50 text-amber-900 font-bold' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}">
              <div class="flex items-center space-x-2.5">
                <input type="radio" name="parlour_slot_time" value="${s}" ${appState.selectedParlourSlotTime === s ? 'checked' : ''} onchange="selectParlourTime('${s}')" class="text-amber-600">
                <span class="text-xs">${s}</span>
              </div>
              <span class="text-[10px] font-bold text-emerald-600">Available</span>
            </label>
          `).join("")}
        </div>
      </div>

      <!-- Confirm Appointment Button -->
      <button onclick="confirmParlourAppointment()" class="w-full py-3.5 bg-gradient-to-r from-amber-600 via-amber-700 to-amber-600 hover:from-amber-700 hover:to-amber-800 text-white rounded-2xl font-bold text-sm shadow-xl transition flex items-center justify-center space-x-2">
        <i data-lucide="check-circle" class="w-5 h-5"></i>
        <span>Confirm Appointment Pass • Pay at ${isMen ? 'Barbershop' : 'Parlour'}</span>
      </button>

      <p class="text-center text-[11px] text-slate-400 mt-2">Free cancellation anytime before your scheduled slot.</p>
    </div>
  `;
  initLucideIcons();
}

function selectParlourDate(d) {
  appState.selectedParlourSlotDate = d;
  if (appState.selectedParlourService) {
    openParlourBookingModal(appState.selectedParlourService.service.id, appState.selectedParlourService.parlour.id);
  }
}

function selectParlourTime(t) {
  appState.selectedParlourSlotTime = t;
}

function closeParlourBookingModal() {
  const modal = document.getElementById("parlour-booking-modal");
  if (modal) modal.classList.add("hidden");
}

function confirmParlourAppointment() {
  const data = appState.selectedParlourService;
  if (!data) return;

  const isMen = data.isMen || appState.selectedCategoryId === 'mens_salon_massage';
  const prefix = isMen ? 'GENT' : 'LUXE';
  const code = `${prefix}-${Math.floor(1000 + Math.random() * 9000)}`;

  // Sync with Backend Beauty Booking REST API
  try {
    fetch('/api/beauty/book-appointment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hub: isMen ? 'mens_salon_massage' : 'womens_salon_spa',
        parlour_id: data.parlour.id,
        service_id: data.service.id,
        stylist_tier: appState.selectedParlourStylist,
        slot_date: appState.selectedParlourSlotDate,
        slot_time: appState.selectedParlourSlotTime,
        customer_name: (window.CURRENT_USER && window.CURRENT_USER.name) || 'Guest Customer',
        customer_phone: '9876543210'
      })
    }).catch(e => console.log('Booking API synced:', e));
  } catch(e) {}

  closeParlourBookingModal();

  showToast(`Appointment Confirmed at ${data.parlour.name}! Pass #${code}`);
  setTimeout(() => {
    alert(`🎉 ${isMen ? "Gentlemen's Barbershop" : "Luxury Parlour"} Appointment Confirmed!\n\nSalon: ${data.parlour.name}\nService: ${data.service.title}\nStylist: ${appState.selectedParlourStylist === 'Senior Stylist' ? (isMen ? 'Senior Barber' : 'Senior Stylist') : (isMen ? 'Master Hair Artist' : 'Master Art Director')}\nSlot: ${appState.selectedParlourSlotDate}, ${appState.selectedParlourSlotTime}\nAddress: ${data.parlour.location}\n\nPass Code: #${code}\n(Please present this pass code upon arrival for zero waiting time).`);
  }, 300);
}

function selectSubcategory(subId) {
  appState.selectedSubcategoryId = subId;
  appState.qsServicesPage = 1;
  renderUrbanCompanyDetailFlow();
  initLucideIcons();
}

function backToCategories() {
  appState.selectedCategoryId = null;
  renderApp();
}

// ----------------------------------------------------
// CART & URBAN COMPANY CHECKOUT FLOW
// ----------------------------------------------------
function addToCart(itemId, categoryId) {
  const cat = SUGU_DATA.categories.find(c => c.id === categoryId);
  if (!cat) return;

  let targetItem = null;
  for (const sub of cat.subcategories) {
    const found = sub.items.find(i => i.id === itemId);
    if (found) {
      targetItem = found;
      break;
    }
  }

  if (targetItem) {
    appState.cart.push({
      item: targetItem,
      quantity: 1,
      categoryId: categoryId
    });
    showToast(`Added "${targetItem.title}" to cart!`);
    renderApp();
  }
}

function updateCartQuantity(itemId, delta) {
  const idx = appState.cart.findIndex(c => c.item.id === itemId);
  if (idx !== -1) {
    appState.cart[idx].quantity += delta;
    if (appState.cart[idx].quantity <= 0) {
      const removedName = appState.cart[idx].item.title;
      appState.cart.splice(idx, 1);
      showToast(`Removed "${removedName}" from cart`);
    }
    renderApp();
  }
}

function renderFloatingCart() {
  const bar = document.getElementById("floating-cart-bar");
  if (!bar) return;

  const totalQty = appState.cart.reduce((sum, i) => sum + i.quantity, 0);
  const subtotal = appState.cart.reduce((sum, i) => sum + (i.item.price * i.quantity), 0);

  if (totalQty > 0) {
    bar.classList.remove("hidden", "translate-y-full");
    const countEl = document.getElementById("cart-bar-count");
    const totalEl = document.getElementById("cart-bar-total");
    if (countEl) countEl.innerText = `${totalQty} ${totalQty === 1 ? 'service' : 'services'}`;
    if (totalEl) totalEl.innerText = `₹${subtotal}`;
  } else {
    bar.classList.add("hidden", "translate-y-full");
  }
}

function openCheckoutModal() {
  if (appState.cart.length === 0) {
    showToast("Your cart is empty. Please select a service first!");
    return;
  }
  appState.bookingStep = 1;
  const modal = document.getElementById("checkout-modal");
  if (modal) {
    modal.classList.remove("hidden");
    renderCheckoutStep();
  }
}

function closeCheckoutModal() {
  const modal = document.getElementById("checkout-modal");
  if (modal) modal.classList.add("hidden");
}

function renderCheckoutStep() {
  const content = document.getElementById("checkout-step-content");
  if (!content) return;

  const subtotal = appState.cart.reduce((sum, i) => sum + (i.item.price * i.quantity), 0);
  let discount = 0;
  if (appState.appliedCoupon === 'SUGUFIRST') {
    discount = Math.min(200, Math.round(subtotal * 0.5));
  } else if (appState.appliedCoupon === 'ACFEST200') {
    discount = 200;
  }

  const convenienceFee = 49;
  const total = Math.max(0, subtotal - discount + convenienceFee);

  if (appState.bookingStep === 1) {
    // Step 1: Review items & Add-ons
    content.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <h3 class="font-bold text-lg text-slate-900">1. Review Selected Services</h3>
          <span class="text-xs font-semibold text-sky-600 bg-sky-50 px-2 py-1 rounded">${appState.cart.length} items</span>
        </div>

        <div class="space-y-3 mb-6 max-h-56 overflow-y-auto pr-1">
          ${appState.cart.map(c => `
            <div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div class="flex-1 pr-3">
                <h5 class="text-sm font-bold text-slate-800">${c.item.title}</h5>
                <span class="text-xs text-slate-500">₹${c.item.price} each</span>
              </div>
              <div class="flex items-center space-x-2 bg-white px-2 py-1 rounded-lg border border-slate-200">
                <button onclick="updateCartQuantity('${c.item.id}', -1); renderCheckoutStep();" class="text-slate-500 hover:text-sky-600 p-0.5">
                  <i data-lucide="minus" class="w-3.5 h-3.5"></i>
                </button>
                <span class="text-xs font-bold px-1">${c.quantity}</span>
                <button onclick="updateCartQuantity('${c.item.id}', 1); renderCheckoutStep();" class="text-slate-500 hover:text-sky-600 p-0.5">
                  <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                </button>
              </div>
              <span class="font-bold text-sm text-slate-900 ml-4">₹${c.item.price * c.quantity}</span>
            </div>
          `).join("")}
        </div>

        <!-- Coupon code input -->
        <div class="p-3.5 rounded-xl bg-sky-50/70 border border-sky-200 mb-6">
          <label class="block text-xs font-bold text-sky-900 mb-1.5">Apply Coupon / Promo Code</label>
          <div class="flex gap-2">
            <input type="text" id="coupon-input" placeholder="Try SUGUFIRST or ACFEST200" 
              value="${appState.appliedCoupon || ''}"
              class="flex-1 px-3 py-2 text-xs uppercase font-mono font-bold rounded-lg border border-slate-300 focus:outline-none focus:border-sky-600 bg-white">
            <button onclick="applyCouponCode()" class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-bold transition">
              Apply
            </button>
          </div>
          ${appState.appliedCoupon ? `
            <p class="text-[11px] text-emerald-700 font-semibold mt-1.5 flex items-center">
              <i data-lucide="check-circle" class="w-3.5 h-3.5 mr-1"></i> Coupon "${appState.appliedCoupon}" applied successfully!
            </p>
          ` : ''}
        </div>

        <!-- Bill Breakdown -->
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 mb-6 space-y-2 text-xs">
          <div class="flex justify-between text-slate-600">
            <span>Item Total</span>
            <span>₹${subtotal}</span>
          </div>
          ${discount > 0 ? `
            <div class="flex justify-between text-emerald-600 font-semibold">
              <span>Coupon Discount</span>
              <span>- ₹${discount}</span>
            </div>
          ` : ''}
          <div class="flex justify-between text-slate-600">
            <span>Safety & Technician Hygiene Fee</span>
            <span>₹${convenienceFee}</span>
          </div>
          <div class="flex justify-between text-sm font-extrabold text-slate-900 pt-2 border-t border-slate-200">
            <span>Total Payable</span>
            <span class="text-sky-700">₹${total}</span>
          </div>
        </div>

        <button onclick="goToBookingStep(2)" class="w-full py-3 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-sm shadow-md transition flex items-center justify-center space-x-2">
          <span>Select Date & Time Slot</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </div>
    `;
  } else if (appState.bookingStep === 2) {
    // Step 2: Date & Slot Selection
    const days = [
      { label: "Today", date: "2 Oct, Fri" },
      { label: "Tomorrow", date: "3 Oct, Sat" },
      { label: "Sun", date: "4 Oct, Sun" },
      { label: "Mon", date: "5 Oct, Mon" }
    ];

    const slots = [
      "09:00 AM - 11:00 AM",
      "11:00 AM - 01:00 PM",
      "02:00 PM - 04:00 PM",
      "04:00 PM - 06:00 PM",
      "06:30 PM - 08:30 PM"
    ];

    content.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <h3 class="font-bold text-lg text-slate-900">2. Select Arrival Date & Slot</h3>
          <button onclick="goToBookingStep(1)" class="text-xs font-semibold text-sky-600 hover:underline">← Back</button>
        </div>

        <!-- Date Picker -->
        <label class="block text-xs font-bold text-slate-700 mb-2">Select Preferred Day</label>
        <div class="grid grid-cols-4 gap-2 mb-6">
          ${days.map(d => `
            <button onclick="selectDate('${d.label}')" class="p-3 rounded-xl border text-center transition ${appState.selectedSlotDate === d.label ? 'border-sky-600 bg-sky-50 text-sky-800 font-bold shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'}">
              <span class="block text-xs font-bold">${d.label}</span>
              <span class="block text-[11px] text-slate-500">${d.date}</span>
            </button>
          `).join("")}
        </div>

        <!-- Slot Picker -->
        <label class="block text-xs font-bold text-slate-700 mb-2">Select 2-Hour Arrival Window</label>
        <div class="space-y-2 mb-6">
          ${slots.map(s => `
            <label class="flex items-center justify-between p-3 rounded-xl border cursor-pointer transition ${appState.selectedSlotTime === s ? 'border-sky-600 bg-sky-50 text-sky-900 font-bold' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}">
              <div class="flex items-center space-x-3">
                <input type="radio" name="time_slot" value="${s}" ${appState.selectedSlotTime === s ? 'checked' : ''} onchange="selectTime('${s}')" class="text-sky-600 focus:ring-sky-500">
                <span class="text-xs font-semibold">${s}</span>
              </div>
              <span class="text-[11px] font-semibold text-emerald-600">✓ Free Cancellation</span>
            </label>
          `).join("")}
        </div>

        <button onclick="goToBookingStep(3)" class="w-full py-3 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-sm shadow-md transition flex items-center justify-center space-x-2">
          <span>Continue to Address & Payment</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </div>
    `;
  } else if (appState.bookingStep === 3) {
    // Step 3: Address & Payment Confirmation
    content.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <h3 class="font-bold text-lg text-slate-900">3. Address & Payment</h3>
          <button onclick="goToBookingStep(2)" class="text-xs font-semibold text-sky-600 hover:underline">← Back</button>
        </div>

        <!-- Address details -->
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-slate-800 flex items-center">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 mr-1 text-sky-600"></i> Service Address
            </span>
            <span class="text-[11px] font-semibold text-sky-600 cursor-pointer" onclick="openLocationPicker()">Change</span>
          </div>
          <p class="text-xs text-slate-700 font-medium">Flat 402, Prestige Palms, 12th Main, ${appState.userLocation}</p>
          <input type="text" placeholder="Add Flat / Floor / Landmark details..." value="Flat 402, 4th Floor" class="w-full mt-2 px-3 py-1.5 text-xs rounded border border-slate-200 bg-white">
        </div>

        <!-- Slot summary -->
        <div class="p-3 rounded-xl bg-sky-50 border border-sky-200 mb-5 flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2 text-sky-900">
            <i data-lucide="calendar" class="w-4 h-4 text-sky-600"></i>
            <span class="font-bold">${appState.selectedSlotDate}, ${appState.selectedSlotTime}</span>
          </div>
          <span class="text-emerald-700 font-semibold">15-Min Guaranteed Dispatch</span>
        </div>

        <!-- Payment Method -->
        <label class="block text-xs font-bold text-slate-700 mb-2">Select Payment Method</label>
        <div class="space-y-2 mb-6">
          <label class="flex items-center justify-between p-3 rounded-xl border border-sky-600 bg-sky-50/50 cursor-pointer">
            <div class="flex items-center space-x-3">
              <input type="radio" name="payment_method" checked class="text-sky-600">
              <div>
                <span class="text-xs font-bold text-slate-900 block">Pay After Service (Cash / UPI on Completion)</span>
                <span class="text-[11px] text-slate-500">Pay the expert only when you are 100% satisfied</span>
              </div>
            </div>
            <span class="text-xs font-bold text-emerald-600">Recommended</span>
          </label>
          <label class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white cursor-pointer hover:bg-slate-50">
            <div class="flex items-center space-x-3">
              <input type="radio" name="payment_method" class="text-sky-600">
              <div>
                <span class="text-xs font-bold text-slate-900 block">Instant UPI (GPay / PhonePe / Paytm)</span>
                <span class="text-[11px] text-slate-500">Fast 1-click contactless checkout</span>
              </div>
            </div>
          </label>
        </div>

        <button onclick="confirmOrder()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-base shadow-lg transition flex items-center justify-center space-x-2">
          <i data-lucide="shield-check" class="w-5 h-5"></i>
          <span>Confirm Booking • ₹${total}</span>
        </button>
      </div>
    `;
  }
  initLucideIcons();
}

function goToBookingStep(step) {
  appState.bookingStep = step;
  renderCheckoutStep();
}

function selectDate(dateLabel) {
  appState.selectedSlotDate = dateLabel;
  renderCheckoutStep();
}

function selectTime(timeSlot) {
  appState.selectedSlotTime = timeSlot;
  renderCheckoutStep();
}

function applyCouponCode() {
  const input = document.getElementById("coupon-input");
  if (!input) return;
  const val = input.value.trim().toUpperCase();
  if (val === 'SUGUFIRST' || val === 'ACFEST200' || val === 'RENO40') {
    appState.appliedCoupon = val;
    showToast(`Coupon "${val}" applied!`);
  } else {
    showToast("Invalid promo code. Try SUGUFIRST");
  }
  renderCheckoutStep();
}

function confirmOrder() {
  // Clear cart & trigger live assignment
  appState.assignedPartner = {
    name: "Rameshwar Varma",
    badge: "Master Certified Expert",
    rating: "4.92 ★ (1,240 jobs)",
    phone: "+91 98450 12894",
    arrivalMins: 18,
    otp: "5429",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80"
  };

  closeCheckoutModal();
  openOrderSuccessModal();
  appState.cart = [];
  appState.appliedCoupon = null;
  renderFloatingCart();
  updateNavState();
}

function openOrderSuccessModal() {
  const modal = document.getElementById("order-success-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  const container = document.getElementById("order-tracking-content");
  if (container && appState.assignedPartner) {
    const p = appState.assignedPartner;
    container.innerHTML = `
      <div class="text-center mb-6">
        <div class="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-3 shadow-md">
          <i data-lucide="check" class="w-8 h-8 stroke-[3]"></i>
        </div>
        <h3 class="text-2xl font-bold font-heading text-slate-900">Booking Confirmed!</h3>
        <p class="text-xs text-slate-500 mt-1">Order #SUGU-${Math.floor(100000 + Math.random() * 900000)} • 30-Day Guarantee Backed</p>
      </div>

      <!-- Live Partner Dispatch Card -->
      <div class="p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-xl mb-5">
        <div class="flex items-center justify-between text-xs text-sky-400 font-semibold mb-3">
          <span class="flex items-center">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-2"></span>
            PRO EN ROUTE
          </span>
          <span>ETA ~${p.arrivalMins} Mins</span>
        </div>
        <div class="flex items-center space-x-3">
          <img src="${p.avatar}" alt="${p.name}" class="w-14 h-14 rounded-full object-cover border-2 border-sky-400">
          <div class="flex-1">
            <h4 class="font-bold text-white text-base">${p.name}</h4>
            <span class="text-xs text-slate-300 block">${p.badge}</span>
            <span class="text-xs text-amber-400 font-semibold">${p.rating}</span>
          </div>
          <button onclick="showToast('Calling Pro: ' + '${p.phone}')" class="w-10 h-10 rounded-full bg-sky-600 hover:bg-sky-500 text-white flex items-center justify-center shadow-lg transition">
            <i data-lucide="phone" class="w-4 h-4"></i>
          </button>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-700/80 flex items-center justify-between text-xs text-slate-300">
          <span>Start Service OTP:</span>
          <span class="font-mono font-extrabold text-base bg-white/20 text-white px-2.5 py-0.5 rounded tracking-widest">${p.otp}</span>
        </div>
      </div>

      <!-- Slot details -->
      <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1 mb-6">
        <div class="flex justify-between text-slate-700">
          <span>Scheduled Slot:</span>
          <strong class="text-slate-900">${appState.selectedSlotDate}, ${appState.selectedSlotTime}</strong>
        </div>
        <div class="flex justify-between text-slate-700">
          <span>Destination:</span>
          <strong class="text-slate-900">${appState.userLocation}</strong>
        </div>
      </div>

      <button onclick="closeOrderSuccessModal()" class="w-full py-3 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold text-sm shadow transition">
        Done & Track in My Bookings
      </button>
    `;
    initLucideIcons();
  }
}

function closeOrderSuccessModal() {
  const modal = document.getElementById("order-success-modal");
  if (modal) modal.classList.add("hidden");
  switchRoute('home');
}

// ----------------------------------------------------
// 3. BIDDING HUB VIEW (END-USER BIDDING PORTAL - EASY MODE)
// ----------------------------------------------------
function renderBiddingView() {
  if (!appState.biddingTab) {
    appState.biddingTab = 'tenders';
  }
  const tabTenders = document.getElementById("bid-tab-tenders-btn");
  const tabPost = document.getElementById("bid-tab-post-btn");
  const tabTemplates = document.getElementById("bid-tab-templates-btn");

  const secTenders = document.getElementById("bidding-tenders-section");
  const secPost = document.getElementById("bidding-post-section");
  const secTemplates = document.getElementById("bidding-templates-section");

  // Calculate total bids across all active tenders
  const totalBids = (appState.biddingJobs || []).reduce((sum, j) => sum + (j.bids ? j.bids.length : 0), 0);
  const badgeCountEl = document.getElementById("bid-badge-count");
  if (badgeCountEl) badgeCountEl.innerText = totalBids;

  // Reset tab button states
  [tabTenders, tabPost, tabTemplates].forEach(btn => {
    if (!btn) return;
    btn.classList.remove("bg-amber-600", "text-white", "shadow");
    btn.classList.add("bg-white", "text-slate-700");
  });

  // Hide all sections
  if (secTenders) secTenders.classList.add("hidden");
  if (secPost) secPost.classList.add("hidden");
  if (secTemplates) secTemplates.classList.add("hidden");

  if (appState.biddingTab === 'tenders') {
    if (tabTenders) {
      tabTenders.classList.add("bg-amber-600", "text-white", "shadow");
      tabTenders.classList.remove("bg-white", "text-slate-700");
    }
    if (secTenders) secTenders.classList.remove("hidden");
    renderActiveBiddingTenders();
  } else if (appState.biddingTab === 'post-job') {
    if (tabPost) {
      tabPost.classList.add("bg-amber-600", "text-white", "shadow");
      tabPost.classList.remove("bg-white", "text-slate-700");
    }
    if (secPost) secPost.classList.remove("hidden");
    renderPostJobWizard();
  } else if (appState.biddingTab === 'templates') {
    if (tabTemplates) {
      tabTemplates.classList.add("bg-amber-600", "text-white", "shadow");
      tabTemplates.classList.remove("bg-white", "text-slate-700");
    }
    if (secTemplates) secTemplates.classList.remove("hidden");
    renderBiddingTemplates();
  }
}

function setBiddingTab(tab) {
  appState.biddingTab = tab;
  renderBiddingView();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function getTradeCategoryIcon(catName) {
  const c = (catName || '').toLowerCase();
  if (c.includes('carpent')) return '🪚';
  if (c.includes('clean')) return '🧹';
  if (c.includes('electr')) return '⚡';
  if (c.includes('paint')) return '🎨';
  if (c.includes('plumb')) return '🔧';
  if (c.includes('renov')) return '🏡';
  if (c.includes('improv')) return '🛠️';
  if (c.includes('ac') || c.includes('appliance')) return '❄️';
  if (c.includes('pest')) return '🐜';
  if (c.includes('kitchen')) return '🍳';
  return '📋';
}

function setBiddingCategoryFilter(catKey) {
  appState.biddingCategoryFilter = catKey;
  appState.biddingPage = 1;
  renderActiveBiddingTenders();
}

function resetBiddingFilters() {
  appState.biddingCategoryFilter = 'all';
  renderActiveBiddingTenders();
}

function renderActiveBiddingTenders() {
  const container = document.getElementById("active-tenders-list");
  const filterBar = document.getElementById("bidding-filter-bar");
  if (!container) return;

  const allJobs = appState.biddingJobs || [];
  const totalJobsCount = allJobs.length;

  // Calculate total bids across all active tenders
  const totalBids = allJobs.reduce((sum, j) => sum + (j.bids ? j.bids.length : 0), 0);
  const badgeCountEl = document.getElementById("bid-badge-count");
  if (badgeCountEl) badgeCountEl.innerText = totalBids;

  // If no jobs exist at all
  if (totalJobsCount === 0) {
    if (filterBar) filterBar.innerHTML = '';
    container.innerHTML = `
      <div class="bg-white rounded-3xl p-12 text-center border border-slate-200 shadow-sm mb-8">
        <div class="w-16 h-16 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="layers" class="w-8 h-8"></i>
        </div>
        <h3 class="text-xl font-bold text-slate-800 mb-2">No Active Tenders Yet</h3>
        <p class="text-xs text-slate-500 max-w-md mx-auto mb-6">Be the first to post a home renovation or custom project requirement and get competitive bids in minutes!</p>
        <button onclick="setBiddingTab('post-job')" class="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-lg transition">
          ⚡ Post Your First Requirement
        </button>
      </div>
    `;
    initLucideIcons();
    return;
  }

  // Extract unique categories present in jobs
  const categoryMap = new Map();
  allJobs.forEach(j => {
    const c = j.category ? j.category.trim() : 'Home Improvement';
    categoryMap.set(c, (categoryMap.get(c) || 0) + 1);
  });
  const uniqueCategories = Array.from(categoryMap.keys()).sort();

  // Filter jobs by active Category
  let filteredJobs = [...allJobs];
  if (appState.biddingCategoryFilter && appState.biddingCategoryFilter !== 'all') {
    const targetCat = appState.biddingCategoryFilter.toLowerCase();
    filteredJobs = filteredJobs.filter(j => (j.category || '').toLowerCase() === targetCat);
  }

  // Sort jobs by newest/recent
  filteredJobs.sort((a, b) => (b.dbId || 0) - (a.dbId || 0));

  // Calculate Bidding Pagination
  const filteredCount = filteredJobs.length;
  const perPage = appState.biddingPerPage || 5;
  const totalPages = Math.ceil(filteredCount / perPage) || 1;
  if (appState.biddingPage > totalPages) appState.biddingPage = totalPages;
  if (appState.biddingPage < 1) appState.biddingPage = 1;
  const startIdx = (appState.biddingPage - 1) * perPage;
  const endIdx = Math.min(startIdx + perPage, filteredCount);
  const pagedJobs = filteredJobs.slice(startIdx, endIdx);

  // Render Category Filter Bar
  if (filterBar) {
    filterBar.innerHTML = `
      <div class="w-full bg-white p-4 sm:p-5 rounded-3xl border border-slate-200/90 shadow-sm mb-6">
        <!-- Header Row -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3.5">
          <div class="flex items-center space-x-2.5">
            <div class="w-8 h-8 rounded-xl bg-sugu-blue/10 text-sugu-blue flex items-center justify-center font-bold">
              <i data-lucide="layers" class="w-4 h-4"></i>
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-extrabold uppercase tracking-wider text-slate-800">Category Filter</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-sugu-blue border border-blue-200">${uniqueCategories.length} Trades</span>
              </div>
              <p class="text-[11px] text-slate-500">Filter open customer tenders by trade specialization</p>
            </div>
          </div>
          <div class="text-xs text-slate-500 font-medium bg-slate-50 px-3.5 py-1.5 rounded-xl border border-slate-200 shrink-0">
            Showing <strong class="text-slate-900 font-bold">${filteredCount > 0 ? (startIdx + 1) : 0}–${endIdx}</strong> of ${filteredCount} open projects
          </div>
        </div>

        <!-- Category Pills List -->
        <div class="flex flex-wrap items-center gap-2 pt-1">
          <!-- All Categories Pill -->
          <button onclick="setBiddingCategoryFilter('all')" 
            class="px-4 py-2 rounded-2xl text-xs font-bold transition-all flex items-center space-x-2 border
            ${appState.biddingCategoryFilter === 'all' 
              ? 'bg-gradient-to-r from-slate-900 via-sugu-navy to-slate-900 text-white border-slate-900 shadow-md shadow-slate-900/15 scale-[1.02]' 
              : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'}">
            <span>🌐</span>
            <span>All</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ${appState.biddingCategoryFilter === 'all' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-700'}">${totalJobsCount}</span>
          </button>

          <!-- Dynamic Trade Categories -->
          ${uniqueCategories.map(c => {
            const count = categoryMap.get(c) || 0;
            const isActive = appState.biddingCategoryFilter.toLowerCase() === c.toLowerCase();
            const icon = getTradeCategoryIcon(c);
            return `
              <button onclick="setBiddingCategoryFilter('${c}')" 
                class="px-4 py-2 rounded-2xl text-xs font-bold transition-all flex items-center space-x-2 border
                ${isActive 
                  ? 'bg-gradient-to-r from-sugu-blue to-blue-700 text-white border-blue-600 shadow-md shadow-blue-600/20 scale-[1.02]' 
                  : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'}">
                <span>${icon}</span>
                <span>${c}</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ${isActive ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-700'}">${count}</span>
              </button>
            `;
          }).join("")}
        </div>
      </div>
    `;
  }

  // If no jobs match category filter
  if (filteredJobs.length === 0) {
    container.innerHTML = `
      <div class="bg-white rounded-3xl p-10 text-center border border-slate-200 shadow-sm mb-8">
        <div class="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
          <i data-lucide="filter-x" class="w-7 h-7"></i>
        </div>
        <h4 class="text-lg font-bold text-slate-800 mb-1">No Projects in "${appState.biddingCategoryFilter}"</h4>
        <p class="text-xs text-slate-500 max-w-sm mx-auto mb-4">No open customer requirements currently match this trade category.</p>
        <button onclick="resetBiddingFilters()" class="px-5 py-2.5 bg-sugu-blue hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow transition">
          View All Categories
        </button>
      </div>
    `;
    initLucideIcons();
    return;
  }

  // Render Paged Job Opportunity Cards with Small Category Icon & "Send Bid"
  const cardsHtml = pagedJobs.map(job => {
    const iconSrc = (job.icon && (job.icon.startsWith('http') || job.icon.startsWith('/') || job.icon.includes('/')))
      ? job.icon
      : (job.icon ? `/static/assets/icons/${job.icon}` : '/static/assets/icons/painting_upgrade.png');

    const primaryJobPhoto = (job.main_image && (job.main_image.startsWith('http') || job.main_image.startsWith('/')))
      ? job.main_image
      : ((job.photos && job.photos.length > 0) ? job.photos[0] : iconSrc);

    const tradeIcon = getTradeCategoryIcon(job.category);
    const bidsReceived = job.bidsCount || (job.bids ? job.bids.length : 0);

    return `
      <div class="bg-white rounded-3xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden mb-6">
        <!-- Card Main Container -->
        <div class="p-6 sm:p-7">
          
          <!-- Top Row: Small Category Icon, Category, Job ID, Status, Target Budget -->
          <div class="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-4 border-b border-slate-100">
            <div class="flex items-start space-x-3.5 sm:space-x-4">
              <!-- Small Category Thumbnail (Compact & Clean) -->
              <div class="relative w-12 h-12 sm:w-14 sm:h-14 rounded-xl overflow-hidden border border-slate-200/90 shadow-xs shrink-0 bg-slate-50 flex items-center justify-center p-0.5 group cursor-pointer" 
                   onclick="window.open('${primaryJobPhoto}', '_blank')" 
                   title="Click to view full photo">
                <img src="${primaryJobPhoto}" alt="${job.title}" class="w-full h-full object-cover rounded-lg group-hover:scale-110 transition-transform duration-300" onerror="this.src='${iconSrc}'">
                <div class="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-[10px]">
                  <i data-lucide="zoom-in" class="w-3.5 h-3.5"></i>
                </div>
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1">
                  <span class="px-2 py-0.5 text-xs font-bold rounded-lg bg-amber-100 text-amber-900 border border-amber-200/90 flex items-center space-x-1">
                    <span>${tradeIcon}</span>
                    <span>${job.category}</span>
                  </span>
                  <span class="text-xs text-slate-400 font-mono font-bold">${job.id}</span>
                  <span class="text-xs text-slate-400 font-medium">• Posted ${job.postedDate}</span>
                  ${bidsReceived > 0 ? `
                    <span class="px-2.5 py-0.5 text-xs font-bold rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center">
                      <span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                      ${bidsReceived} ${bidsReceived === 1 ? 'Bid Received' : 'Bids Received'}
                    </span>
                  ` : `
                    <span class="px-2.5 py-0.5 text-xs font-bold rounded-lg bg-blue-50 text-sugu-blue border border-blue-200">
                      ⚡ Be First to Bid
                    </span>
                  `}
                </div>
                <h3 class="text-lg sm:text-xl font-extrabold font-heading text-slate-900 leading-snug">${job.title}</h3>
                <p class="text-xs text-slate-500 mt-0.5 line-clamp-1">${job.description}</p>
              </div>
            </div>

            <!-- Target Budget Box -->
            <div class="shrink-0 bg-gradient-to-br from-slate-50 via-white to-amber-50/30 p-4 rounded-2xl border border-slate-200/90 shadow-xs min-w-[200px] text-left md:text-right">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Client Target Budget</span>
              <span class="text-2xl font-black text-slate-900 block mt-0.5">${job.budgetRange}</span>
              <span class="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md mt-1 inline-block border border-emerald-200">
                100% Payment Protected
              </span>
            </div>
          </div>

          <!-- Description & Scope Section -->
          <div class="py-4 space-y-3">
            <div>
              <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1">Requirement & Scope Details</span>
              <p class="text-sm text-slate-700 leading-relaxed font-normal">${job.description}</p>
            </div>

            ${(job.scopeOfWork && job.scopeOfWork.trim() && job.scopeOfWork.trim() !== job.description.trim()) ? `
              <div class="p-3.5 bg-amber-50/50 rounded-2xl border border-amber-200/70 text-xs text-amber-950">
                <span class="font-bold text-amber-900 block mb-0.5 flex items-center">
                  <i data-lucide="clipboard-list" class="w-3.5 h-3.5 mr-1 text-amber-700"></i> Scope of Work Specification:
                </span>
                <p class="leading-relaxed font-medium">${job.scopeOfWork}</p>
              </div>
            ` : ''}

            ${(job.materialsDetails && job.materialsDetails.trim()) ? `
              <div class="p-3 bg-blue-50/50 rounded-xl border border-blue-200/60 text-xs text-slate-700 flex items-start space-x-2">
                <i data-lucide="package" class="w-4 h-4 text-sugu-blue shrink-0 mt-0.5"></i>
                <div>
                  <strong class="text-slate-800">Materials & Supply Notes:</strong> ${job.materialsDetails}
                </div>
              </div>
            ` : ''}

            <!-- Project Specifications Grid -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Location</span>
                <span class="text-xs font-bold text-slate-800 flex items-center mt-1 truncate" title="${job.location}">
                  <i data-lucide="map-pin" class="w-3.5 h-3.5 mr-1 text-slate-400 shrink-0"></i>
                  ${job.location}
                </span>
              </div>

              <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Turnaround</span>
                <span class="text-xs font-bold text-slate-800 flex items-center mt-1">
                  <i data-lucide="clock" class="w-3.5 h-3.5 mr-1 text-amber-500 shrink-0"></i>
                  ${job.urgency}
                </span>
              </div>

              <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Start Date</span>
                <span class="text-xs font-bold text-slate-800 flex items-center mt-1">
                  <i data-lucide="calendar" class="w-3.5 h-3.5 mr-1 text-sugu-blue shrink-0"></i>
                  ${job.preferredStartDate || 'Immediate'}
                </span>
              </div>

              <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Bidding Slots</span>
                <span class="text-xs font-bold text-slate-800 flex items-center mt-1">
                  <i data-lucide="users" class="w-3.5 h-3.5 mr-1 text-emerald-600 shrink-0"></i>
                  ${bidsReceived} of ${job.maxBids || 10} filled
                </span>
              </div>
            </div>

            <!-- Site Photos Gallery (If available) -->
            ${job.photos && job.photos.length > 0 ? `
              <div class="pt-3 border-t border-slate-100">
                <div class="flex items-center justify-between mb-2.5">
                  <span class="text-xs uppercase font-extrabold text-slate-700 tracking-wider flex items-center">
                    <i data-lucide="camera" class="w-4 h-4 mr-1.5 text-sugu-blue"></i>
                    Project Site &amp; Requirement Photos (${job.photos.length})
                  </span>
                  <span class="text-[11px] text-slate-400 font-medium">Click any photo to view full size</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3">
                  ${job.photos.map((p, pIdx) => `
                    <div class="relative group cursor-pointer overflow-hidden rounded-2xl border border-slate-200 shadow-xs aspect-[4/3] bg-slate-50" onclick="window.open('${p}', '_blank')" title="View site photo ${pIdx+1}">
                      <img src="${p}" class="w-full h-full object-cover group-hover:scale-108 transition-transform duration-300" alt="Job Site Photo ${pIdx+1}">
                      <div class="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold space-x-1">
                        <i data-lucide="zoom-in" class="w-4 h-4"></i>
                        <span>Enlarge</span>
                      </div>
                    </div>
                  `).join("")}
                </div>
              </div>
            ` : ''}
          </div>

          <!-- Footer Action Bar: Trust Guarantee & "Send Bid" -->
          <div class="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="flex items-center space-x-2 text-xs text-slate-500 font-medium">
              <i data-lucide="shield-check" class="w-4 h-4 text-emerald-600 shrink-0"></i>
              <span>Verified Homeowner Requirement • Payment Secured &amp; Released On Satisfaction</span>
            </div>

            <button onclick="handleSendBid('${job.dbId}')" 
              class="px-7 py-3 rounded-2xl bg-gradient-to-r from-sugu-navy via-sugu-blue to-blue-600 hover:from-blue-700 hover:to-sugu-navy text-white font-bold text-xs sm:text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center space-x-2 group shrink-0">
              <i data-lucide="send" class="w-4 h-4 group-hover:translate-x-0.5 transition-transform"></i>
              <span>Send Bid</span>
            </button>
          </div>

        </div>
      </div>
    `;
  }).join("");

  // Bidding Pagination Controls
  let paginationHtml = '';
  if (totalPages > 1) {
    let pagesHtml = '';
    for (let p = 1; p <= totalPages; p++) {
      const isCur = p === appState.biddingPage;
      pagesHtml += `
        <button onclick="changeBiddingPage(${p})" 
          class="w-8 h-8 rounded-xl text-xs font-bold transition flex items-center justify-center border
          ${isCur ? 'bg-sugu-blue text-white border-sugu-blue shadow-sm' : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'}">
          ${p}
        </button>
      `;
    }

    paginationHtml = `
      <div class="mt-8 p-4 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="text-xs text-slate-500 font-medium">
          Showing <strong class="text-slate-900 font-bold">${startIdx + 1}–${endIdx}</strong> of <strong class="text-slate-900 font-bold">${filteredCount}</strong> projects (Page ${appState.biddingPage} of ${totalPages})
        </div>
        <div class="flex items-center space-x-1.5">
          <button onclick="changeBiddingPage(${appState.biddingPage - 1})" 
            ${appState.biddingPage === 1 ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
            <i data-lucide="chevron-left" class="w-4 h-4"></i>
            <span>Previous</span>
          </button>
          ${pagesHtml}
          <button onclick="changeBiddingPage(${appState.biddingPage + 1})" 
            ${appState.biddingPage === totalPages ? 'disabled class="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 flex items-center space-x-1"' : 'class="px-3 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-xs transition hover:text-sugu-blue flex items-center space-x-1"'}>
            <span>Next</span>
            <i data-lucide="chevron-right" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    `;
  }

  container.innerHTML = cardsHtml + paginationHtml;
  initLucideIcons();
}

function changeBiddingPage(newPage) {
  appState.biddingPage = newPage;
  renderActiveBiddingTenders();
  const el = document.getElementById("bidding-filter-bar");
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
window.changeBiddingPage = changeBiddingPage;

// ----------------------------------------------------
// VENDOR AUTH & "SEND BID" SUBMISSION FLOW
// ----------------------------------------------------
function handleSendBid(jobDbId) {
  const allJobs = appState.biddingJobs || [];
  const job = allJobs.find(j => String(j.dbId) === String(jobDbId) || String(j.id) === String(jobDbId));
  if (!job) return;

  const user = window.CURRENT_USER || {};

  // Case 1: Visitor is NOT logged in
  if (!user.isAuthenticated) {
    openVendorAuthPromptModal(job, false);
    return;
  }

  // Case 2: User is logged in, but is NOT a Vendor Partner (e.g. standard Customer)
  if (user.role !== 'VENDOR' && !user.isStaff) {
    openVendorAuthPromptModal(job, true);
    return;
  }

  // Case 3: Verified Vendor is logged in -> Open Bid Form Modal!
  openSendBidModal(job);
}

function openVendorAuthPromptModal(job, isNonVendorRole) {
  const modal = document.getElementById("vendor-auth-prompt-modal");
  if (!modal) return;

  const titleEl = document.getElementById("vendor-prompt-job-title");
  const budgetEl = document.getElementById("vendor-prompt-job-budget");
  const msgEl = document.getElementById("vendor-prompt-message");
  const loginBtn = document.getElementById("vendor-prompt-login-btn");

  if (titleEl) titleEl.innerText = job.title || "Project Requirement";
  if (budgetEl) budgetEl.innerText = `Target Budget: ${job.budgetRange || 'Competitive'}`;

  if (isNonVendorRole) {
    const userName = (window.CURRENT_USER && window.CURRENT_USER.name) || "Customer";
    if (msgEl) {
      msgEl.innerHTML = `You are currently logged into a Customer account (<strong>${userName}</strong>). Only verified <strong>Vendor Partners</strong> can send quotations on client projects.`;
    }
    if (loginBtn) {
      loginBtn.href = "/login/?next=" + encodeURIComponent(window.location.pathname + "#view-bidding");
      loginBtn.querySelector("span").innerText = "Switch to Vendor Partner Account";
    }
  } else {
    if (msgEl) {
      msgEl.innerHTML = `To submit an itemized bid on <strong>${job.title}</strong>, please log in with your verified <strong>Sugu Vendor Partner</strong> account.`;
    }
    if (loginBtn) {
      loginBtn.href = "/login/?next=" + encodeURIComponent(window.location.pathname + "#view-bidding");
      loginBtn.querySelector("span").innerText = "Log In as Vendor Partner";
    }
  }

  modal.classList.remove("hidden");
  initLucideIcons();
}

function closeVendorAuthPromptModal() {
  const modal = document.getElementById("vendor-auth-prompt-modal");
  if (modal) modal.classList.add("hidden");
}

let currentBiddingJob = null;

function openSendBidModal(job) {
  currentBiddingJob = job;
  const modal = document.getElementById("send-bid-modal");
  if (!modal) return;

  // Set header details
  const idEl = document.getElementById("send-bid-job-id");
  const titleEl = document.getElementById("send-bid-job-title");
  const catEl = document.getElementById("send-bid-job-category");
  const budgetEl = document.getElementById("send-bid-job-budget");
  const dbIdEl = document.getElementById("send-bid-job-dbid");
  const boundsEl = document.getElementById("send-bid-price-bounds");
  const amountInput = document.getElementById("send-bid-amount-input");
  const timelineInput = document.getElementById("send-bid-timeline-input");
  const proposalInput = document.getElementById("send-bid-proposal-input");
  const attachmentInput = document.getElementById("send-bid-attachment-input");
  const errorBanner = document.getElementById("send-bid-error-banner");
  const formContainer = document.getElementById("send-bid-form-container");
  const successContainer = document.getElementById("send-bid-success-container");

  if (idEl) idEl.innerText = job.id || `JOB-${job.dbId}`;
  if (titleEl) titleEl.innerText = job.title || "Custom Project";
  if (catEl) catEl.innerText = `${job.category || 'General'} • ${job.location || 'Local'}`;
  if (budgetEl) budgetEl.innerText = job.budgetRange || "Negotiable";
  if (dbIdEl) dbIdEl.value = job.dbId;

  // Price bounds helper
  if (boundsEl) {
    if (job.minBidAmount && job.maxBidAmount) {
      boundsEl.innerText = `Allowed range: ₹${Math.round(job.minBidAmount).toLocaleString('en-IN')} - ₹${Math.round(job.maxBidAmount).toLocaleString('en-IN')}`;
    } else {
      boundsEl.innerText = `Client target: ${job.budgetRange || 'Competitive'}`;
    }
  }

  // Pre-fill amount with numeric target budget if available
  const numBudget = parseInt(String(job.budgetRange || '').replace(/[^0-9]/g, '')) || job.budget || '';
  if (amountInput) {
    amountInput.value = numBudget ? Math.round(numBudget) : '';
  }

  if (timelineInput) {
    timelineInput.value = job.urgency || "3-5 Working Days";
  }

  if (proposalInput) {
    proposalInput.value = `Professional quotation for ${job.title}. Includes certified materials, trained labor, and complete cleanup.`;
  }

  if (attachmentInput) attachmentInput.value = '';
  if (errorBanner) {
    errorBanner.classList.add("hidden");
    errorBanner.innerText = '';
  }

  if (formContainer) formContainer.classList.remove("hidden");
  if (successContainer) successContainer.classList.add("hidden");

  updateBidCalculationBreakdown();
  modal.classList.remove("hidden");
  initLucideIcons();
}

function closeSendBidModal() {
  const modal = document.getElementById("send-bid-modal");
  if (modal) modal.classList.add("hidden");
  currentBiddingJob = null;
}

function setBidTimelinePreset(val) {
  const input = document.getElementById("send-bid-timeline-input");
  if (input) input.value = val;
  document.querySelectorAll(".timeline-preset-btn").forEach(btn => {
    if (btn.innerText.trim() === val) {
      btn.classList.add("border-sugu-blue", "bg-blue-50", "text-sugu-blue", "font-bold");
    } else {
      btn.classList.remove("border-sugu-blue", "bg-blue-50", "text-sugu-blue", "font-bold");
    }
  });
}

function insertProBidTemplate() {
  const textarea = document.getElementById("send-bid-proposal-input");
  if (!textarea) return;
  const jobTitle = (currentBiddingJob && currentBiddingJob.title) || "this requirement";
  textarea.value = `Comprehensive proposal for ${jobTitle}:\n1. Complete labor by verified certified technicians\n2. Premium grade materials & proper surface preparation\n3. Daily site hygiene & post-work debris cleanup\n4. 30-day workmanship warranty backed by Sugu Payment Guarantee.`;
}

function updateBidCalculationBreakdown() {
  const amountInput = document.getElementById("send-bid-amount-input");
  const baseEl = document.getElementById("calc-bid-base");
  const feeEl = document.getElementById("calc-bid-fee");
  const netEl = document.getElementById("calc-bid-net");

  const val = parseFloat(amountInput ? amountInput.value : 0) || 0;
  const fee = Math.round(val * 0.10);
  const net = Math.max(0, val - fee);

  if (baseEl) baseEl.innerText = `₹${val.toLocaleString('en-IN')}`;
  if (feeEl) feeEl.innerText = `- ₹${fee.toLocaleString('en-IN')}`;
  if (netEl) netEl.innerText = `₹${net.toLocaleString('en-IN')}`;
}

async function submitVendorQuotation(event) {
  event.preventDefault();
  const submitBtn = document.getElementById("send-bid-submit-btn");
  const errorBanner = document.getElementById("send-bid-error-banner");
  const formContainer = document.getElementById("send-bid-form-container");
  const successContainer = document.getElementById("send-bid-success-container");
  const successMsg = document.getElementById("send-bid-success-msg");

  const jobDbId = document.getElementById("send-bid-job-dbid").value;
  const amount = document.getElementById("send-bid-amount-input").value;
  const timeline = document.getElementById("send-bid-timeline-input").value;
  const proposal = document.getElementById("send-bid-proposal-input").value;
  const attachmentInput = document.getElementById("send-bid-attachment-input");

  if (!amount || parseFloat(amount) <= 0) {
    if (errorBanner) {
      errorBanner.innerText = "Please enter a valid quotation amount greater than 0.";
      errorBanner.classList.remove("hidden");
    }
    return;
  }

  if (errorBanner) errorBanner.classList.add("hidden");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="inline-block animate-spin mr-2">⏳</span> Transmitting Bid...';
  }

  const formData = new FormData();
  formData.append("job_id", jobDbId);
  formData.append("amount", amount);
  formData.append("estimated_time", timeline);
  formData.append("proposal", proposal);
  if (attachmentInput && attachmentInput.files[0]) {
    formData.append("attachment", attachmentInput.files[0]);
  }

  // Get CSRF Token
  const csrfToken = window.CSRF_TOKEN || (function() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue;
  })();

  try {
    const res = await fetch("/api/vendor/send-quotation/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrfToken || ""
      },
      credentials: "same-origin"
    });

    const data = await res.json().catch(() => ({}));

    if (res.ok && (data.status === 'success' || data.bid_id || !data.status || data.status === 200)) {
      // Success!
      if (formContainer) formContainer.classList.add("hidden");
      if (successContainer) successContainer.classList.remove("hidden");
      if (successMsg) {
        successMsg.innerHTML = `Your quotation of <strong>₹${Number(amount).toLocaleString('en-IN')}</strong> (${timeline}) has been submitted directly to the client. Track status in your Vendor Dashboard.`;
      }

      // Increment local job bids count
      if (currentBiddingJob) {
        currentBiddingJob.bidsCount = (currentBiddingJob.bidsCount || 0) + 1;
        renderActiveBiddingTenders();
      }
    } else {
      const errMsg = data.message || data.error || "Failed to submit quotation. Please try again.";
      if (errorBanner) {
        errorBanner.innerText = errMsg;
        errorBanner.classList.remove("hidden");
      }
    }
  } catch (err) {
    console.error("Bid submission error:", err);
    if (errorBanner) {
      errorBanner.innerText = "Network error while submitting quotation. Please check your connection.";
      errorBanner.classList.remove("hidden");
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i data-lucide="send" class="w-4 h-4 mr-2"></i><span>Send Bid to Client</span>';
      initLucideIcons();
    }
  }
}

// ----------------------------------------------------
// POST JOB WIZARD (COMPLETELY DROPDOWN-FREE & VISUAL)
// ----------------------------------------------------
function selectBiddingCategory(catId) {
  const cat = findCategory(catId);
  if (cat) {
    appState.biddingSelectedCategory = cat.id;
    const titleInput = document.getElementById("job-title");
    if (titleInput) {
      titleInput.value = `${appState.biddingSelectedSize} ${cat.name} Custom Requirement`;
    }
  } else {
    appState.biddingSelectedCategory = catId;
  }
  renderPostJobWizard();
}

function selectBiddingSize(sizeLabel) {
  appState.biddingSelectedSize = sizeLabel;
  const cat = findCategory(appState.biddingSelectedCategory) || SUGU_DATA.categories[0];
  const titleInput = document.getElementById("job-title");
  if (titleInput && cat) {
    titleInput.value = `${sizeLabel} ${cat.name} Custom Requirement`;
  }
  renderPostJobWizard();
}

function selectBiddingUrgency(urgencyLabel) {
  appState.biddingSelectedUrgency = urgencyLabel;
  renderPostJobWizard();
}

function selectBiddingBudgetPreset(budgetLabel) {
  appState.biddingSelectedBudget = budgetLabel;
  const budgetInput = document.getElementById("job-budget");
  if (budgetInput) budgetInput.value = budgetLabel;
  renderPostJobWizard();
}

function renderPostJobWizard() {
  const container = document.getElementById("bidding-post-form-container");
  if (!container) return;

  const currentCat = findCategory(appState.biddingSelectedCategory) || SUGU_DATA.categories[0];
  if (currentCat) {
    appState.biddingSelectedCategory = currentCat.id;
  }

  const sizeOptions = ["1 BHK", "2 BHK", "3 BHK", "4+ BHK / Villa", "Custom Scope"];
  const urgencyOptions = [
    { label: "⚡ Urgent (24-48 Hours)", val: "Immediate (Next 24-48 Hours)" },
    { label: "📅 This Weekend", val: "Within 1 Week" },
    { label: "🗓️ Flexible (1-2 Weeks)", val: "Flexible (Planning Phase)" }
  ];
  const budgetPresets = ["₹5,000 - ₹15,000", "₹15,000 - ₹30,000", "₹30,000 - ₹50,000", "₹50,000+"];

  // Dynamic Bidding categories straight from Super Admin DB categories
  const biddingCats = (window.DB_CATEGORIES && window.DB_CATEGORIES.length > 0)
    ? window.DB_CATEGORIES
    : ((typeof SUGU_DATA !== 'undefined' && SUGU_DATA.categories) ? SUGU_DATA.categories : []);

  container.innerHTML = `
    <div class="max-w-4xl mx-auto bg-white rounded-3xl p-6 sm:p-10 border border-slate-200 shadow-2xl">
      <!-- Wizard Title -->
      <div class="text-center mb-8">
        <span class="px-3.5 py-1 text-xs font-extrabold uppercase tracking-wider bg-amber-100 text-amber-800 rounded-full border border-amber-300">
          3 Easy Taps • Zero Dropdowns • 100% Free
        </span>
        <h2 class="text-3xl font-extrabold font-heading text-slate-900 mt-2">Post Your Requirement</h2>
        <p class="text-xs sm:text-sm text-slate-500 mt-1">Tap your category and scope below to receive 3-5 itemized bids from verified local contractors in 30 minutes.</p>
      </div>

      <form id="post-job-form" onsubmit="handlePostJobSubmit(event)" class="space-y-8">
        
        <!-- STEP 1: VISUAL 3D CATEGORY SELECTION (NO DROPDOWNS!) -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <label class="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center">
              <span class="w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs mr-2 font-black">1</span>
              Tap Your Service Category
            </label>
            <span class="text-xs font-semibold text-amber-700">Selected: <strong>${currentCat ? currentCat.name : 'Category'}</strong></span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            ${biddingCats.map(c => {
              const catImg = c.image || (c.isCustomImage ? c.iconFile : (c.iconFile ? '/static/assets/icons/' + c.iconFile : '/static/assets/icons/home_renovation.png'));
              return `
              <div onclick="selectBiddingCategory('${c.id}')" 
                class="relative p-3 rounded-2xl border-2 cursor-pointer transition-all duration-300 flex flex-col items-center text-center 
                ${String(c.id) === String(appState.biddingSelectedCategory) ? 'border-amber-500 bg-amber-50/60 shadow-md ring-2 ring-amber-400/20 scale-[1.02]' : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'}">
                <div class="w-16 h-16 rounded-xl overflow-hidden mb-2 bg-slate-50 p-1 flex items-center justify-center">
                  <img src="${catImg}" alt="${c.name}" class="w-full h-full object-contain" onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/1063/1063376.png'">
                </div>
                <span class="text-xs font-bold text-slate-900 leading-tight">${c.name}</span>
                ${String(c.id) === String(appState.biddingSelectedCategory) ? `
                  <div class="absolute top-2 right-2 w-5 h-5 rounded-full bg-amber-500 text-white flex items-center justify-center shadow">
                    <i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>
                  </div>
                ` : ''}
              </div>
            `;
            }).join("")}
          </div>
        </div>

        <!-- STEP 2: 1-TAP SCOPE SIZE & TIMELINE CHIPS (NO DROPDOWNS!) -->
        <div class="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-5">
          <!-- Size Selector -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2.5 flex items-center">
              <span class="w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs mr-2 font-black">2</span>
              Select Project Size / Scope
            </label>
            <div class="flex flex-wrap gap-2">
              ${sizeOptions.map(sz => `
                <button type="button" onclick="selectBiddingSize('${sz}')" 
                  class="px-4 py-2.5 rounded-xl text-xs font-bold transition border 
                  ${appState.biddingSelectedSize === sz ? 'bg-amber-600 text-white border-amber-600 shadow' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'}">
                  ${sz}
                </button>
              `).join("")}
            </div>
          </div>

          <!-- Urgency Selector -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2.5">
              When Should Work Start?
            </label>
            <div class="flex flex-wrap gap-2">
              ${urgencyOptions.map(u => `
                <button type="button" onclick="selectBiddingUrgency('${u.val}')" 
                  class="px-4 py-2.5 rounded-xl text-xs font-bold transition border 
                  ${appState.biddingSelectedUrgency === u.val ? 'bg-slate-900 text-white border-slate-900 shadow' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'}">
                  ${u.label}
                </button>
              `).join("")}
            </div>
          </div>
        </div>

        <!-- STEP 3: 1-TAP BUDGET RANGE PRESETS & PROJECT TITLE -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2 flex items-center">
            <span class="w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs mr-2 font-black">3</span>
            Target Budget & Description
          </label>
          
          <!-- Preset Budget Chips -->
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <span class="text-xs text-slate-500 font-semibold mr-1">Quick Budget:</span>
            ${budgetPresets.map(bp => `
              <button type="button" onclick="selectBiddingBudgetPreset('${bp}')" 
                class="px-3 py-1.5 rounded-lg text-xs font-bold transition border 
                ${appState.biddingSelectedBudget === bp ? 'bg-amber-50 text-amber-800 border-amber-400' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'}">
                ${bp}
              </button>
            `).join("")}
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Project Title</label>
              <input type="text" id="job-title" required 
                value="${appState.biddingSelectedSize} ${currentCat.name} Custom Requirement" 
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:border-amber-600 text-xs font-bold bg-white">
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Budget Expectation (₹)</label>
              <input type="text" id="job-budget" required 
                value="${appState.biddingSelectedBudget}" 
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:border-amber-600 text-xs font-bold bg-white">
            </div>
          </div>

          <div>
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Specific Details / Brand Preference (Optional)</label>
            <textarea id="job-desc" rows="3" placeholder="e.g. Prefer Asian Paints Royale or Century Ply, need dustless sanding, site inspection required before start..." 
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:border-amber-600 text-xs text-slate-800 bg-white">Need quality execution for ${appState.biddingSelectedSize} with verified contractor warranty and proper surface preparation.</textarea>
          </div>
        </div>

        <!-- Optional Site Photos Upload Simulation -->
        <div class="border-2 border-dashed border-slate-300 hover:border-amber-500 rounded-2xl p-5 text-center cursor-pointer transition bg-slate-50/50" onclick="showToast('Sample site photos attached!')">
          <i data-lucide="camera" class="w-6 h-6 text-amber-600 mx-auto mb-1.5"></i>
          <span class="text-xs font-bold text-slate-700 block">Tap to attach room photos or drawings (Optional)</span>
          <span class="text-[10px] text-slate-400">Pros provide more accurate quotes with photos</span>
        </div>

        <!-- Big 1-Click Action Button -->
        <button type="submit" class="w-full py-4 bg-gradient-to-r from-amber-600 via-amber-700 to-amber-600 hover:from-amber-700 hover:to-amber-800 text-white rounded-2xl font-black text-base shadow-xl transition-all duration-300 flex items-center justify-center space-x-2">
          <i data-lucide="send" class="w-5 h-5"></i>
          <span>Publish Requirement & Get 3-5 Quotes Free</span>
        </button>

      </form>
    </div>
  `;
  initLucideIcons();
}

function handlePostJobSubmit(e) {
  e.preventDefault();
  const title = document.getElementById("job-title").value;
  const desc = document.getElementById("job-desc").value;
  const budget = document.getElementById("job-budget").value;

  const catObj = SUGU_DATA.categories.find(c => c.id === appState.biddingSelectedCategory) || SUGU_DATA.categories[0];

  const newJob = {
    id: `JOB-${Math.floor(8000 + Math.random() * 1000)}`,
    title: title,
    category: catObj.name,
    icon: catObj.iconFile,
    postedDate: "Just now",
    budgetRange: budget,
    urgency: appState.biddingSelectedUrgency,
    location: appState.userLocation,
    description: desc,
    photos: [
      "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=400&q=80"
    ],
    status: "Receiving Bids",
    bids: [
      {
        id: `BID-${Math.floor(300 + Math.random() * 100)}`,
        bidderName: "Star Pro Builders & Renovators",
        contractor: "Harish Gowda",
        rating: "4.91",
        jobsDone: 184,
        avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=150&q=80",
        bidAmount: parseInt(budget.replace(/\D/g, '')) || 24000,
        timeline: "4 Days",
        included: "All premium labor + equipment + free surface sanding & dust mask vacuum cleanup.",
        verified: true,
        isRecommended: true
      },
      {
        id: `BID-${Math.floor(400 + Math.random() * 100)}`,
        bidderName: "Elite Craft Solutions",
        contractor: "Naveen Raj",
        rating: "4.85",
        jobsDone: 96,
        avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80",
        bidAmount: Math.round((parseInt(budget.replace(/\D/g, '')) || 24000) * 0.92),
        timeline: "5 Days",
        included: "Complete execution + branded consumables + 2-year warranty card.",
        verified: true,
        isRecommended: false
      }
    ]
  };

  appState.biddingJobs.unshift(newJob);
  showToast("Your job was published! 2 verified contractors have already submitted quotes.");
  setBiddingTab('tenders');
}

// ----------------------------------------------------
// 1-TAP POPULAR TEMPLATES (EASIEST OPTION FOR END USERS)
// ----------------------------------------------------
function renderBiddingTemplates() {
  const container = document.getElementById("bidding-templates-container");
  if (!container) return;

  const templates = (typeof SUGU_DATA !== 'undefined' && SUGU_DATA.biddingDemo && SUGU_DATA.biddingDemo.popularTemplates) ? SUGU_DATA.biddingDemo.popularTemplates : [];

  container.innerHTML = `
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-8">
        <span class="px-3 py-1 text-xs font-extrabold uppercase tracking-wider bg-emerald-100 text-emerald-800 rounded-full">1-Click Fast Start</span>
        <h3 class="text-2xl sm:text-3xl font-bold font-heading text-slate-900 mt-2">Popular Job Presets</h3>
        <p class="text-xs sm:text-sm text-slate-500 mt-1">Don't want to type descriptions? Tap any template below to post with verified scopes and expected budget ranges.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        ${templates.map(tpl => {
          const tplIcon = (tpl.icon && (tpl.icon.startsWith('http') || tpl.icon.startsWith('/'))) ? tpl.icon : '/static/assets/icons/' + (tpl.icon || 'home_renovation.png');
          return `
          <div class="p-6 rounded-3xl bg-white border border-slate-200 shadow-md hover:shadow-xl transition-all duration-300 flex flex-col justify-between group">
            <div>
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-14 h-14 rounded-2xl bg-slate-50 border border-slate-200 p-2 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition">
                  <img src="${tplIcon}" alt="${tpl.category}" class="w-full h-full object-contain" onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/1063/1063376.png'">
                </div>
                <div>
                  <span class="text-[11px] font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">${tpl.category}</span>
                  <h4 class="font-bold text-slate-900 text-sm mt-1 leading-snug">${tpl.title}</h4>
                </div>
              </div>

              <div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 mb-3 space-y-1.5 text-xs">
                <div class="flex justify-between text-slate-500">
                  <span>Est. Budget:</span>
                  <strong class="text-slate-900">${tpl.budgetRange}</strong>
                </div>
                <div class="flex justify-between text-slate-500">
                  <span>Average Response:</span>
                  <strong class="text-emerald-700">${tpl.avgQuotes}</strong>
                </div>
                <div class="flex justify-between text-slate-500">
                  <span>Timeline:</span>
                  <strong class="text-slate-700">${tpl.urgency}</strong>
                </div>
              </div>

              <p class="text-xs text-slate-600 mb-4 line-clamp-3 leading-relaxed">${tpl.description}</p>
            </div>

            <div class="space-y-2 pt-3 border-t border-slate-100">
              <button onclick="postFromTemplate('${tpl.id}')" 
                class="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold shadow transition flex items-center justify-center space-x-1.5">
                <i data-lucide="zap" class="w-4 h-4 fill-white"></i>
                <span>Post This Job in 1-Click</span>
              </button>
              <button onclick="customizeTemplate('${tpl.id}')" 
                class="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition text-center">
                Customize Before Posting
              </button>
            </div>
          </div>
        `;
        }).join("")}
      </div>
    </div>
  `;
  initLucideIcons();
}

function postFromTemplate(tplId) {
  const tpl = (SUGU_DATA.biddingDemo.popularTemplates || []).find(t => t.id === tplId);
  if (!tpl) return;

  const newJob = {
    id: `JOB-${Math.floor(8000 + Math.random() * 1000)}`,
    title: tpl.title,
    category: tpl.category,
    icon: tpl.icon,
    postedDate: "Just now",
    budgetRange: tpl.budgetRange,
    urgency: tpl.urgency,
    location: appState.userLocation,
    description: tpl.description,
    photos: [
      "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=400&q=80"
    ],
    status: "Receiving Bids",
    bids: [
      {
        id: `BID-${Math.floor(500 + Math.random() * 100)}`,
        bidderName: "Royal Craftsmen Guild",
        contractor: "Ravi Shankar (Verified Pro)",
        rating: "4.93",
        jobsDone: 240,
        avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        bidAmount: parseInt(tpl.budgetRange.replace(/\D/g, '').substring(0, 5)) || 22000,
        timeline: "4 Working Days",
        included: "Complete standard labor, warranty certificate, branded consumables and site clean up.",
        verified: true,
        isRecommended: true
      },
      {
        id: `BID-${Math.floor(600 + Math.random() * 100)}`,
        bidderName: "Prime City Projects",
        contractor: "Karthik Reddy",
        rating: "4.84",
        jobsDone: 110,
        avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80",
        bidAmount: Math.round((parseInt(tpl.budgetRange.replace(/\D/g, '').substring(0, 5)) || 22000) * 0.95),
        timeline: "5 Working Days",
        included: "All tools & scaffold setup included + 3-stage milestone delivery.",
        verified: true,
        isRecommended: false
      }
    ]
  };

  appState.biddingJobs.unshift(newJob);
  showToast(`Created job from template: "${tpl.title}" with 2 live contractor quotes!`);
  setBiddingTab('tenders');
}

function customizeTemplate(tplId) {
  const tpl = (SUGU_DATA.biddingDemo.popularTemplates || []).find(t => t.id === tplId);
  if (!tpl) return;

  appState.biddingSelectedCategory = tpl.categoryId || "painting_upgrade";
  appState.biddingSelectedBudget = tpl.budgetRange;
  setBiddingTab('post-job');

  setTimeout(() => {
    const titleInput = document.getElementById("job-title");
    const descInput = document.getElementById("job-desc");
    const budgetInput = document.getElementById("job-budget");
    if (titleInput) titleInput.value = tpl.title;
    if (descInput) descInput.value = tpl.description;
    if (budgetInput) budgetInput.value = tpl.budgetRange;
  }, 100);
}

function acceptBid(jobId, bidId, amount, proName) {
  showToast(`Accepted bid from ${proName}! Sugu Payment Protection active.`);
  setTimeout(() => {
    alert(`🎉 Congratulations! You have successfully hired ${proName} for ₹${amount.toLocaleString()}.\n\nNext Steps:\n1. Advance payment secured in Sugu Payment Protection Guarantee.\n2. Contractor will visit for pre-execution inspection.\n3. Contract & 100% Satisfaction Guarantee activated.`);
  }, 300);
}

// ----------------------------------------------------
// COUNTER-OFFER WITH 1-TAP PRESETS
// ----------------------------------------------------
function openCounterOfferModal(jobId, bidId, currentBid, proName) {
  appState.counterBidTarget = { jobId, bidId, currentBid, proName };
  const modal = document.getElementById("counter-offer-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  document.getElementById("counter-modal-pro-name").innerText = proName;
  document.getElementById("counter-modal-current-bid").innerText = `₹${currentBid.toLocaleString()}`;
  document.getElementById("counter-offer-price").value = Math.round(currentBid * 0.9);

  // Render quick preset discount chips in modal
  const presetContainer = document.getElementById("counter-presets-container");
  if (presetContainer) {
    const discount5 = Math.round(currentBid * 0.95);
    const discount10 = Math.round(currentBid * 0.90);
    const discount15 = Math.round(currentBid * 0.85);

    presetContainer.innerHTML = `
      <div class="flex flex-wrap gap-2 mb-3">
        <button type="button" onclick="setQuickCounter(${discount5})" class="px-3 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 text-xs font-bold">
          -5% (₹${discount5.toLocaleString()})
        </button>
        <button type="button" onclick="setQuickCounter(${discount10})" class="px-3 py-1.5 rounded-lg bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-400 text-xs font-black shadow-sm">
          -10% (₹${discount10.toLocaleString()})
        </button>
        <button type="button" onclick="setQuickCounter(${discount15})" class="px-3 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 text-xs font-bold">
          -15% (₹${discount15.toLocaleString()})
        </button>
      </div>
    `;
  }
}

function setQuickCounter(amount) {
  const input = document.getElementById("counter-offer-price");
  if (input) input.value = amount;
}

function closeCounterOfferModal() {
  const modal = document.getElementById("counter-offer-modal");
  if (modal) modal.classList.add("hidden");
}

function submitCounterOffer() {
  const price = document.getElementById("counter-offer-price").value;
  const note = document.getElementById("counter-offer-note").value;

  closeCounterOfferModal();
  showToast(`Counter-offer of ₹${Number(price).toLocaleString()} sent to ${appState.counterBidTarget.proName}!`);

  setTimeout(() => {
    showToast(`🔔 ${appState.counterBidTarget.proName} responded: "Accepted your counter-offer of ₹${Number(price).toLocaleString()}! Ready to start."`);
  }, 2500);
}

function openChatModal(proName, avatar) {
  const modal = document.getElementById("chat-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  document.getElementById("chat-pro-name").innerText = proName;
  document.getElementById("chat-pro-avatar").src = avatar;
  initLucideIcons();
}

function closeChatModal() {
  const modal = document.getElementById("chat-modal");
  if (modal) modal.classList.add("hidden");
}

function sendChatMessage(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  const stream = document.getElementById("chat-stream");
  const userBubble = document.createElement("div");
  userBubble.className = "flex justify-end mb-3";
  userBubble.innerHTML = `
    <div class="bg-sky-600 text-white rounded-2xl rounded-tr-none px-4 py-2.5 text-xs max-w-xs shadow">
      ${msg}
    </div>
  `;
  stream.appendChild(userBubble);
  input.value = "";
  stream.scrollTop = stream.scrollHeight;

  // Auto simulated reply from contractor
  setTimeout(() => {
    const proBubble = document.createElement("div");
    proBubble.className = "flex justify-start mb-3";
    proBubble.innerHTML = `
      <div class="bg-slate-100 text-slate-800 rounded-2xl rounded-tl-none px-4 py-2.5 text-xs max-w-xs border border-slate-200 shadow-sm">
        "Thank you for the message! I can bring the paint shade card and wood samples tomorrow morning at 10 AM. Will that work?"
      </div>
    `;
    stream.appendChild(proBubble);
    stream.scrollTop = stream.scrollHeight;
  }, 1200);
}

// ----------------------------------------------------
// VIDEO MODAL
// ----------------------------------------------------
function openVideoModal(videoId) {
  let v = null;
  if (window.DB_VIDEOS && Array.isArray(window.DB_VIDEOS)) {
    v = window.DB_VIDEOS.find(item => String(item.id) === String(videoId));
  }
  if (!v && typeof SUGU_DATA !== 'undefined' && SUGU_DATA.videos) {
    v = SUGU_DATA.videos.find(item => String(item.id) === String(videoId));
  }
  if (!v) return;

  const modal = document.getElementById("video-modal");
  if (!modal) return;
  modal.classList.remove("hidden");

  document.getElementById("video-modal-title").innerText = v.title;
  document.getElementById("video-modal-author").innerText = `${v.author} • ${v.city}`;
  document.getElementById("video-modal-quote").innerText = `"${v.quote}"`;

  const videoElement = document.getElementById("video-modal-player");
  if (videoElement) {
    videoElement.src = v.videoUrl || v.video_url || v.src || "";
    videoElement.play().catch(e => console.log("Autoplay prevented:", e));
  }
}

function closeVideoModal() {
  const modal = document.getElementById("video-modal");
  if (!modal) return;
  modal.classList.add("hidden");
  const videoElement = document.getElementById("video-modal-player");
  if (videoElement) {
    videoElement.pause();
    videoElement.src = "";
  }
}

// ----------------------------------------------------
// LOCATION PICKER MODAL
// ----------------------------------------------------
function openLocationPicker() {
  const modal = document.getElementById("location-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeLocationPicker() {
  const modal = document.getElementById("location-modal");
  if (modal) modal.classList.add("hidden");
}

function setLocation(loc) {
  appState.userLocation = loc;
  const headerText = document.getElementById("header-location-text");
  if (headerText) headerText.innerText = loc;
  localStorage.setItem("sugu_user_location", loc);
  closeLocationPicker();
  showToast(`Location set to ${loc}`);
  renderApp();
}

// ----------------------------------------------------
// UTILITIES & TOASTS
// ----------------------------------------------------
function showToast(message) {
  const toast = document.getElementById("toast-notification");
  if (!toast) return;
  document.getElementById("toast-message").innerText = message;
  toast.classList.remove("translate-y-24", "opacity-0");
  toast.classList.add("translate-y-0", "opacity-100");

  setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-24", "opacity-0");
  }, 3200);
}

function copyPromoCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`Code "${code}" copied to clipboard!`);
  }).catch(() => {
    showToast(`Code: ${code}`);
  });
}

function showItemDetails(itemId) {
  showToast("Backed by Sugu 30-day rework warranty & ₹10,000 damage protection guarantee.");
}

function setupEventListeners() {
  // Global search bar handling
  const searchInput = document.getElementById("global-search-input");
  if (searchInput) {
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const val = searchInput.value.toLowerCase().trim();
        if (val) {
          // Find matching category
          const found = SUGU_DATA.categories.find(c => 
            c.name.toLowerCase().includes(val) || 
            c.tagline.toLowerCase().includes(val) ||
            c.subcategories.some(s => s.name.toLowerCase().includes(val))
          );
          if (found) {
            switchRoute('quick-service', found.id);
            showToast(`Showing results for "${val}" in ${found.name}`);
          } else {
            switchRoute('quick-service');
            showToast(`Browsing all quick services for "${val}"`);
          }
        }
      }
    });
  }
}

// Expose key router and bidding methods globally on window for inline handlers
window.appState = appState;
window.switchRoute = switchRoute;
window.renderApp = renderApp;
window.setBiddingTab = setBiddingTab;
window.setBiddingCategoryFilter = setBiddingCategoryFilter;
window.resetBiddingFilters = resetBiddingFilters;
window.handleSendBid = handleSendBid;
window.openVendorAuthPromptModal = openVendorAuthPromptModal;
window.closeVendorAuthPromptModal = closeVendorAuthPromptModal;
window.openSendBidModal = openSendBidModal;
window.closeSendBidModal = closeSendBidModal;
window.setBidTimelinePreset = setBidTimelinePreset;
window.insertProBidTemplate = insertProBidTemplate;
window.updateBidCalculationBreakdown = updateBidCalculationBreakdown;
window.submitVendorQuotation = submitVendorQuotation;
window.selectBiddingCategory = typeof selectBiddingCategory === 'function' ? selectBiddingCategory : null;
window.selectBiddingSize = typeof selectBiddingSize === 'function' ? selectBiddingSize : null;
window.selectBiddingUrgency = typeof selectBiddingUrgency === 'function' ? selectBiddingUrgency : null;
window.selectBiddingBudgetPreset = typeof selectBiddingBudgetPreset === 'function' ? selectBiddingBudgetPreset : null;
window.handlePostJobSubmit = typeof handlePostJobSubmit === 'function' ? handlePostJobSubmit : null;
window.postFromTemplate = typeof postFromTemplate === 'function' ? postFromTemplate : null;
window.customizeTemplate = typeof customizeTemplate === 'function' ? customizeTemplate : null;


