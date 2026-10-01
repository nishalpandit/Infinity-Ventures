// Suggu Services - Urban Company High Accuracy Device Geolocation & Search Engine
(function() {
  const STORAGE_KEY = "suggu_selected_location";

  const DEFAULT_LOCATION = {
    name: "Bengaluru, Karnataka",
    primary: "Bengaluru",
    secondary: "Karnataka, India",
    city: "Bengaluru",
    state: "Karnataka",
    is_live: false,
    lat: 12.9716,
    lon: 77.5946
  };

  // Pre-configured popular localities with precise coordinates for 10km range filtering
  const POPULAR_LOCATIONS = [
    { name: "Indiranagar, Bengaluru", primary: "Indiranagar", secondary: "100ft Road, 12th Main", city: "Bengaluru", state: "Karnataka", lat: 12.9784, lon: 77.6408 },
    { name: "Koramangala, Bengaluru", primary: "Koramangala", secondary: "Sony World Signal, 4th Block", city: "Bengaluru", state: "Karnataka", lat: 12.9352, lon: 77.6245 },
    { name: "HSR Layout, Bengaluru", primary: "HSR Layout", secondary: "27th Main, Sector 1", city: "Bengaluru", state: "Karnataka", lat: 12.9121, lon: 77.6446 },
    { name: "Whitefield, Bengaluru", primary: "Whitefield", secondary: "ITPL Main Road", city: "Bengaluru", state: "Karnataka", lat: 12.9698, lon: 77.7500 },
    { name: "Jayanagar, Bengaluru", primary: "Jayanagar", secondary: "4th Block, 11th Main", city: "Bengaluru", state: "Karnataka", lat: 12.9308, lon: 77.5838 },
    { name: "MG Road, Bengaluru", primary: "MG Road", secondary: "Brigade Road, Central", city: "Bengaluru", state: "Karnataka", lat: 12.9756, lon: 77.6066 },
    { name: "Lalpur, Ranchi", primary: "Lalpur", secondary: "Circular Road, Ranchi", city: "Ranchi", state: "Jharkhand", lat: 23.3697, lon: 85.3346 },
    { name: "Harmu Colony, Ranchi", primary: "Harmu Housing Colony", secondary: "Harmu, Ranchi", city: "Ranchi", state: "Jharkhand", lat: 23.3550, lon: 85.3050 },
    { name: "Doranda, Ranchi", primary: "Doranda", secondary: "High Court, AG Colony, Ranchi", city: "Ranchi", state: "Jharkhand", lat: 23.3340, lon: 85.3218 },
    { name: "Morabadi, Ranchi", primary: "Morabadi", secondary: "Tagore Hill, Ranchi University", city: "Ranchi", state: "Jharkhand", lat: 23.3850, lon: 85.3250 },
    { name: "Bariatu, Ranchi", primary: "Bariatu", secondary: "RIMS, Medical College, Ranchi", city: "Ranchi", state: "Jharkhand", lat: 23.3950, lon: 85.3500 },
    { name: "Ashok Nagar, Ranchi", primary: "Ashok Nagar", secondary: "Kadru, Argora, Ranchi", city: "Ranchi", state: "Jharkhand", lat: 23.3380, lon: 85.3120 },
    { name: "Saket, South Delhi", primary: "Saket", secondary: "Saket District Centre, PVR", city: "New Delhi", state: "Delhi", lat: 28.5245, lon: 77.2066 },
    { name: "Connaught Place", primary: "Connaught Place", secondary: "Rajiv Chowk, Central Delhi", city: "New Delhi", state: "Delhi", lat: 28.6315, lon: 77.2167 },
    { name: "Bandra West, Mumbai", primary: "Bandra West", secondary: "Hill Road, Pali Hill", city: "Mumbai", state: "Maharashtra", lat: 19.0596, lon: 72.8295 }
  ];

  function getStoredLocation() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.name) return parsed;
      }
    } catch(e) {}
    return null;
  }

  function setStoredLocation(locData) {
    if (typeof locData === 'string') {
      locData = { name: locData, primary: locData, secondary: "Selected Area", is_live: false, lat: 12.9716, lon: 77.5946 };
    }
    if (!locData.lat || !locData.lon) {
      locData.lat = 12.9716;
      locData.lon = 77.5946;
    }
    locData.timestamp = Date.now();
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(locData));
    } catch(e) {}
    updateNavbarDisplay(locData.name, locData.is_live);
    try {
      window.dispatchEvent(new CustomEvent('sugguLocationUpdated', { detail: locData }));
    } catch(err) {}
  }

  function updateNavbarDisplay(locName, isLive = false) {
    const displays = document.querySelectorAll('.uc-location-display');
    displays.forEach(el => {
      const text = locName.length > 28 ? locName.substring(0, 26) + '...' : locName;
      el.textContent = text;
      el.setAttribute('title', locName);
    });

    document.querySelectorAll('.uc-location-trigger').forEach(btn => {
      let liveBadge = btn.querySelector('.uc-live-pulse-badge');
      if (isLive) {
        if (!liveBadge) {
          const badgeHtml = '<span class="uc-live-pulse-badge" style="width:8px; height:8px; border-radius:50%; background:#10b981; display:inline-block; box-shadow:0 0 0 2px rgba(16,185,129,0.3); animation:pulseGreen 1.5s infinite; margin-right:4px;"></span>';
          const pin = btn.querySelector('.fa-location-dot');
          if (pin) pin.insertAdjacentHTML('beforebegin', badgeHtml);
        }
      } else {
        if (liveBadge) liveBadge.remove();
      }
    });
  }

  function renderModalHtml() {
    if (document.getElementById('uc-location-modal-backdrop')) return;

    const modalHtml = `
      <div id="uc-location-modal-backdrop" style="display:none; position:fixed; inset:0; z-index:9999; background:rgba(0,0,0,0.6); backdrop-filter:blur(5px); align-items:center; justify-content:center; padding:16px;">
        <div class="uc-loc-modal" style="background:#fff; border-radius:20px; width:min(540px, 94vw); max-height:88vh; box-shadow:0 30px 80px rgba(0,0,0,0.3); overflow:hidden; position:relative; display:flex; flex-direction:column; animation: ucModalIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);">
          
          <!-- Close button -->
          <button id="uc-loc-modal-close" style="position:absolute; right:16px; top:16px; width:36px; height:36px; border-radius:50%; background:#f1f3f5; border:none; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#495057; font-size:16px; z-index:10; transition:all 0.2s;">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <!-- Modal Header -->
          <div style="padding:24px 24px 16px; border-bottom:1px solid #f1f3f5;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">
              <div style="width:28px; height:28px; border-radius:8px; background:#f3e8ff; color:#7c3aed; display:flex; align-items:center; justify-content:center; font-size:14px;">
                <i class="fa-solid fa-location-dot"></i>
              </div>
              <h3 style="font-size:18px; font-weight:800; color:#111827; margin:0; letter-spacing:-0.01em;">Select your location</h3>
            </div>
            
            <!-- Real-time Live Search Input -->
            <div style="position:relative; display:flex; align-items:center;">
              <i class="fa-solid fa-magnifying-glass" style="position:absolute; left:14px; color:#9ca3af; font-size:14px;"></i>
              <input type="text" id="uc-loc-search-input" placeholder="Search your colony, apartment, street or landmark..." autocomplete="off"
                     style="width:100%; height:46px; border:1.5px solid #e5e7eb; background:#f9fafb; border-radius:12px; padding:0 16px 0 42px; font-size:14px; color:#111827; outline:none; transition:all 0.2s; box-sizing:border-box;">
              <div id="uc-search-spinner" style="display:none; position:absolute; right:14px; color:#7c3aed; font-size:14px;">
                <i class="fa-solid fa-circle-notch fa-spin"></i>
              </div>
            </div>
          </div>

          <!-- Geolocation GPS Trigger Button -->
          <div style="padding:16px 24px; border-bottom:1px solid #f1f3f5; background:#faf5ff;">
            <button id="uc-loc-use-gps" style="width:100%; display:flex; align-items:center; gap:14px; background:#fff; border:1.5px solid #e9d5ff; padding:12px 14px; border-radius:12px; cursor:pointer; text-align:left; box-shadow:0 2px 8px rgba(124,58,237,0.06); transition:all 0.2s;">
              <div style="width:40px; height:40px; border-radius:10px; background:#7c3aed; display:flex; align-items:center; justify-content:center; color:#fff; font-size:18px; flex-shrink:0; position:relative;">
                <i class="fa-solid fa-crosshairs" id="uc-gps-icon"></i>
                <span class="uc-gps-pulse" style="position:absolute; inset:-4px; border-radius:14px; border:2px solid #7c3aed; opacity:0; animation: gpsRadar 1.8s infinite;"></span>
              </div>
              <div style="flex:1;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="font-size:14.5px; font-weight:700; color:#6b21a8;" id="uc-gps-text">Detect my location</span>
                  <span style="background:#ecfdf5; color:#059669; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px;">DEVICE GPS</span>
                </div>
                <div style="font-size:12px; color:#6b7280; margin-top:2px;" id="uc-gps-sub">Detect exact street & building via device geolocation</div>
              </div>
              <i class="fa-solid fa-arrow-right" style="color:#a855f7; font-size:13px;"></i>
            </button>

            <!-- Error / Permission Hint Bar (Shown only if browser blocks GPS) -->
            <div id="uc-gps-hint-box" style="display:none; margin-top:10px; padding:10px 12px; background:#fef2f2; border:1px solid #fecaca; border-radius:10px; font-size:12px; color:#991b1b; line-height:1.4;">
              <div style="display:flex; align-items:center; gap:6px; font-weight:700; margin-bottom:2px;">
                <i class="fa-solid fa-circle-exclamation"></i>
                <span>Browser GPS permission required</span>
              </div>
              <span>Click the lock 🔒 or site settings icon in your address bar to <b>Allow Location</b>, or search your exact colony name below.</span>
            </div>

            <!-- Detected Live Address Preview Card -->
            <div id="uc-detected-card" style="display:none; margin-top:12px; background:#fff; border:1.5px solid #10b981; border-radius:12px; padding:12px 14px; box-shadow:0 4px 12px rgba(16,185,129,0.12);">
              <div style="display:flex; align-items:start; justify-content:space-between; gap:10px;">
                <div style="flex:1;">
                  <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
                    <span style="width:8px; height:8px; border-radius:50%; background:#10b981; display:inline-block; animation:pulseGreen 1.5s infinite;"></span>
                    <span style="font-size:11px; font-weight:700; color:#047857; text-transform:uppercase; letter-spacing:0.04em;">Exact GPS Position Detected</span>
                  </div>
                  <div id="uc-det-primary" style="font-size:14.5px; font-weight:800; color:#111827;">Lalpur, Ranchi</div>
                  <div id="uc-det-secondary" style="font-size:12px; color:#6b7280; margin-top:2px;">Ranchi, Jharkhand</div>
                </div>
                <button id="uc-confirm-live-btn" style="background:#10b981; color:#fff; border:none; padding:8px 14px; border-radius:8px; font-size:12.5px; font-weight:700; cursor:pointer; white-space:nowrap; transition:background 0.15s;">
                  Confirm & Use
                </button>
              </div>
            </div>
          </div>

          <!-- Locations List / Real-time Search Results -->
          <div id="uc-loc-list-container" style="padding:16px 24px; overflow-y:auto; flex:1; max-height:340px;">
            <div style="font-size:12px; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;" id="uc-loc-list-heading">
              Popular Localities (Ranchi & Metros)
            </div>
            <div id="uc-loc-items" style="display:flex; flex-direction:column; gap:8px;">
              <!-- Populated dynamically -->
            </div>
          </div>

          <!-- Modal Footer -->
          <div style="padding:12px 24px; background:#f9fafb; border-top:1px solid #e5e7eb; display:flex; align-items:center; justify-content:space-between; font-size:11.5px; color:#9ca3af;">
            <div style="display:flex; align-items:center; gap:6px;">
              <i class="fa-solid fa-map-pin" style="color:#7c3aed;"></i>
              <span>High Precision Device Geolocation</span>
            </div>
            <span>Suggu Services</span>
          </div>

        </div>
      </div>
      <style>
        @keyframes ucModalIn {
          from { opacity: 0; transform: scale(0.96) translateY(12px); }
          to { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes gpsRadar {
          0% { transform: scale(1); opacity: 0.8; }
          100% { transform: scale(1.4); opacity: 0; }
        }
        @keyframes pulseGreen {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(1.15); }
        }
        .uc-loc-item {
          display:flex; align-items:center; gap:12px; padding:10px 12px; border-radius:10px; cursor:pointer; transition:all 0.15s; background:#f8fafc; border:1px solid transparent;
        }
        .uc-loc-item:hover {
          background:#fff; border-color:#e2e8f0; transform:translateX(3px); box-shadow:0 3px 10px rgba(0,0,0,0.04);
        }
      </style>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    setupModalEvents();
  }

  function renderLocationsList(items) {
    const container = document.getElementById('uc-loc-items');
    if (!container) return;

    if (!items || items.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:32px 10px; color:#9ca3af; font-size:13px;">
          <i class="fa-solid fa-location-dot" style="font-size:26px; color:#d1d5db; margin-bottom:8px; display:block;"></i>
          No matching localities found. Try typing your colony name above.
        </div>
      `;
      return;
    }

    const currentSaved = getStoredLocation();
    const currentName = currentSaved ? currentSaved.name : "";

    container.innerHTML = items.map(loc => `
      <div class="uc-loc-item" data-name="${loc.name}" data-primary="${loc.primary || loc.name}" data-secondary="${loc.secondary || loc.desc || loc.city || ''}" data-lat="${loc.lat || ''}" data-lon="${loc.lon || ''}">
        <div style="width:34px; height:34px; border-radius:8px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; color:#64748b; font-size:14px; flex-shrink:0;">
          <i class="fa-solid fa-location-dot"></i>
        </div>
        <div style="flex:1; min-width:0;">
          <div style="font-size:13.5px; font-weight:700; color:#1e293b; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${loc.primary || loc.name}</div>
          <div style="font-size:12px; color:#64748b; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${loc.secondary || loc.desc || (loc.city ? loc.city + ', ' + loc.state : '')}</div>
        </div>
        <i class="fa-solid fa-check" style="color:#7c3aed; font-size:13px; opacity:${currentName === loc.name ? 1 : 0};"></i>
      </div>
    `).join('');

    container.querySelectorAll('.uc-loc-item').forEach(el => {
      el.addEventListener('click', () => {
        const name = el.getAttribute('data-name');
        const primary = el.getAttribute('data-primary');
        const secondary = el.getAttribute('data-secondary');
        const lat = el.getAttribute('data-lat') ? parseFloat(el.getAttribute('data-lat')) : null;
        const lon = el.getAttribute('data-lon') ? parseFloat(el.getAttribute('data-lon')) : null;
        setStoredLocation({ name, primary, secondary, is_live: false, lat, lon });
        closeModal();
      });
    });
  }

  function openModal() {
    renderModalHtml();
    const backdrop = document.getElementById('uc-location-modal-backdrop');
    if (backdrop) {
      backdrop.style.display = 'flex';
      const searchInput = document.getElementById('uc-loc-search-input');
      if (searchInput) {
        searchInput.value = '';
        setTimeout(() => searchInput.focus(), 150);
      }
      const hintBox = document.getElementById('uc-gps-hint-box');
      if (hintBox) hintBox.style.display = 'none';
      const detectedCard = document.getElementById('uc-detected-card');
      if (detectedCard) detectedCard.style.display = 'none';
      renderLocationsList(POPULAR_LOCATIONS);
    }
  }

  function closeModal() {
    const backdrop = document.getElementById('uc-location-modal-backdrop');
    if (backdrop) backdrop.style.display = 'none';
  }

  // Device Geolocation Execution
  let lastGpsPayload = null;

  function executeDeviceGeolocation() {
    const gpsIcon = document.getElementById('uc-gps-icon');
    const gpsText = document.getElementById('uc-gps-text');
    const gpsSub = document.getElementById('uc-gps-sub');
    const hintBox = document.getElementById('uc-gps-hint-box');
    const detectedCard = document.getElementById('uc-detected-card');

    if (hintBox) hintBox.style.display = 'none';
    if (detectedCard) detectedCard.style.display = 'none';

    if (!navigator.geolocation) {
      if (hintBox) {
        hintBox.style.display = 'block';
        hintBox.innerHTML = '<span>Geolocation is not supported by your browser. Please search your locality below.</span>';
      }
      return;
    }

    if (gpsIcon) gpsIcon.className = "fa-solid fa-spinner fa-spin";
    if (gpsText) gpsText.textContent = "Requesting device GPS...";
    if (gpsSub) gpsSub.textContent = "Please click [Allow] when browser prompts for location";

    // Direct HTML5 Geolocation API with high accuracy
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        if (gpsText) gpsText.textContent = "Pinpointing exact address...";

        try {
          const res = await fetch(`/api/detect-location/?lat=${lat}&lon=${lon}`);
          const data = await res.json();

          lastGpsPayload = {
            name: data.name || `${lat.toFixed(4)}, ${lon.toFixed(4)}`,
            primary: data.primary || data.name,
            secondary: data.secondary || (data.city + ', ' + data.state),
            full_address: data.full_address || data.name,
            lat: lat,
            lon: lon,
            is_live: true
          };

          if (detectedCard) {
            document.getElementById('uc-det-primary').textContent = lastGpsPayload.primary;
            document.getElementById('uc-det-secondary').textContent = lastGpsPayload.secondary;
            detectedCard.style.display = 'block';
          }

          if (gpsIcon) gpsIcon.className = "fa-solid fa-check";
          if (gpsText) gpsText.textContent = "Exact Location Detected!";
          if (gpsSub) gpsSub.textContent = lastGpsPayload.primary;

          // Auto-confirm in 900ms
          setTimeout(() => {
            setStoredLocation(lastGpsPayload);
            closeModal();
            resetGpsButton();
          }, 900);

        } catch(err) {
          console.error("Reverse geocode failed:", err);
          const fallbackName = `Live Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
          setStoredLocation({ name: fallbackName, primary: fallbackName, secondary: "GPS Coordinates", is_live: true });
          closeModal();
          resetGpsButton();
        }
      },
      (err) => {
        console.warn("Navigator Geolocation error:", err.code, err.message);
        resetGpsButton();
        if (hintBox) {
          hintBox.style.display = 'block';
          if (err.code === 1) {
            hintBox.innerHTML = '<div style="display:flex; align-items:center; gap:6px; font-weight:700; margin-bottom:2px;"><i class="fa-solid fa-lock"></i><span>Location permission was blocked</span></div><span>Please click the lock 🔒 or site settings icon in your browser address bar and select <b>Allow Location</b>. Or search your colony name below.</span>';
          } else {
            hintBox.innerHTML = '<div style="display:flex; align-items:center; gap:6px; font-weight:700; margin-bottom:2px;"><i class="fa-solid fa-circle-exclamation"></i><span>GPS unavailable on this network</span></div><span>Please type your exact colony or apartment name in the search box below.</span>';
          }
        }
        // Focus search input so user can quickly type
        const searchInput = document.getElementById('uc-loc-search-input');
        if (searchInput) searchInput.focus();
      },
      {
        enableHighAccuracy: true,
        timeout: 12000,
        maximumAge: 0
      }
    );
  }

  function resetGpsButton() {
    const gpsIcon = document.getElementById('uc-gps-icon');
    const gpsText = document.getElementById('uc-gps-text');
    const gpsSub = document.getElementById('uc-gps-sub');
    if (gpsIcon) gpsIcon.className = "fa-solid fa-crosshairs";
    if (gpsText) gpsText.textContent = "Use current live location";
    if (gpsSub) gpsSub.textContent = "Detect exact street & building via device geolocation";
  }

  // Real-time Search Handler
  let searchTimer = null;
  function handleLiveSearch(query) {
    const spinner = document.getElementById('uc-search-spinner');
    const heading = document.getElementById('uc-loc-list-heading');

    if (!query || query.length < 2) {
      if (spinner) spinner.style.display = 'none';
      if (heading) heading.textContent = "Popular Localities (Ranchi & Metros)";
      renderLocationsList(POPULAR_LOCATIONS);
      return;
    }

    if (spinner) spinner.style.display = 'block';
    if (heading) heading.textContent = `Search results for "${query}"`;

    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search-locations/?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (spinner) spinner.style.display = 'none';

        if (data && data.results && data.results.length > 0) {
          renderLocationsList(data.results);
        } else {
          const filtered = POPULAR_LOCATIONS.filter(item =>
            item.name.toLowerCase().includes(query.toLowerCase()) ||
            (item.primary && item.primary.toLowerCase().includes(query.toLowerCase())) ||
            (item.city && item.city.toLowerCase().includes(query.toLowerCase()))
          );
          if (filtered.length === 0) {
            filtered.push({ name: `${query}, Ranchi`, primary: query, secondary: "Ranchi, Jharkhand" });
          }
          renderLocationsList(filtered);
        }
      } catch(e) {
        if (spinner) spinner.style.display = 'none';
        renderLocationsList(POPULAR_LOCATIONS);
      }
    }, 250);
  }

  function setupModalEvents() {
    const backdrop = document.getElementById('uc-location-modal-backdrop');
    const closeBtn = document.getElementById('uc-loc-modal-close');
    const searchInput = document.getElementById('uc-loc-search-input');
    const gpsBtn = document.getElementById('uc-loc-use-gps');
    const confirmBtn = document.getElementById('uc-confirm-live-btn');

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) closeModal();
      });
    }

    if (gpsBtn) gpsBtn.addEventListener('click', executeDeviceGeolocation);
    if (confirmBtn) {
      confirmBtn.addEventListener('click', () => {
        if (lastGpsPayload) {
          setStoredLocation(lastGpsPayload);
          closeModal();
          resetGpsButton();
        }
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        handleLiveSearch(e.target.value.trim());
      });
    }
  }

  // Initialize
  function initLocation() {
    const stored = getStoredLocation();
    // If a live location was detected via GPS (stored.is_live is true), use it;
    // Otherwise, default to Bengaluru on the navbar
    if (stored && stored.is_live) {
      updateNavbarDisplay(stored.name, true);
      try {
        window.dispatchEvent(new CustomEvent('sugguLocationUpdated', { detail: stored }));
      } catch(e) {}
    } else {
      // Default to Bengaluru on navbar
      setStoredLocation(DEFAULT_LOCATION);
    }

    document.querySelectorAll('.uc-location-trigger').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', initLocation);

  window.SugguLocation = {
    openModal,
    closeModal,
    getLocation: getStoredLocation,
    setLocation: setStoredLocation,
    detectGps: executeDeviceGeolocation
  };
})();
