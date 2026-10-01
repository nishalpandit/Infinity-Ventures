// Sugu - Urban Company Sub-Category Drill-Down Modal
(function() {
  const SUB_CATEGORIES_MAP = {
    "Plumbing": {
      id: 26,
      sections: [
        {
          title: "Bath & Basin Fittings",
          items: [
            { name: "Tap & Mixer Repair", icon: "fa-faucet-drip", eta: "In 35 mins" },
            { name: "Wash Basin & Sink", icon: "fa-sink", eta: "In 45 mins" },
            { name: "Shower & Bath Valve", icon: "fa-shower", eta: "In 40 mins" },
            { name: "Toilet & Cistern", icon: "fa-toilet", eta: "In 50 mins" }
          ]
        },
        {
          title: "Drainage & Water Supply",
          items: [
            { name: "Drainage Unclogging", icon: "fa-water", eta: "In 30 mins" },
            { name: "Pipe Leakage & Repair", icon: "fa-screwdriver-wrench", eta: "In 45 mins" },
            { name: "Water Tank Cleaning", icon: "fa-boxes-stacked", eta: "In 60 mins" },
            { name: "Motor & Pump Service", icon: "fa-gears", eta: "In 55 mins" }
          ]
        }
      ]
    },
    "Electrical": {
      id: 27,
      sections: [
        {
          title: "Switches & Lighting",
          items: [
            { name: "Switch & Socket", icon: "fa-toggle-on", eta: "In 25 mins" },
            { name: "Ceiling & Exhaust Fan", icon: "fa-fan", eta: "In 35 mins" },
            { name: "Chandelier & Lights", icon: "fa-lightbulb", eta: "In 40 mins" },
            { name: "Doorbell & Intercom", icon: "fa-bell", eta: "In 30 mins" }
          ]
        },
        {
          title: "Heavy Electricals & Safety",
          items: [
            { name: "MCB & Fuse Box", icon: "fa-bolt-lightning", eta: "In 30 mins" },
            { name: "House Full Wiring", icon: "fa-network-wired", eta: "In 90 mins" },
            { name: "Inverter & Battery", icon: "fa-car-battery", eta: "In 45 mins" },
            { name: "Appliance Wiring", icon: "fa-plug", eta: "In 35 mins" }
          ]
        }
      ]
    },
    "AC & Appliance": {
      id: 28,
      sections: [
        {
          title: "Large appliances",
          items: [
            { name: "AC Service & Repair", icon: "fa-snowflake", eta: "In 44 mins" },
            { name: "Washing Machine", icon: "fa-soap", eta: "In 44 mins" },
            { name: "Refrigerator", icon: "fa-temperature-arrow-down", eta: "In 44 mins" },
            { name: "Television", icon: "fa-tv", eta: "In 55 mins" }
          ]
        },
        {
          title: "Other appliances",
          items: [
            { name: "Chimney Cleaning", icon: "fa-wind", eta: "In 55 mins" },
            { name: "Microwave Oven", icon: "fa-kitchen-set", eta: "In 45 mins" },
            { name: "Stove & Gas Hob", icon: "fa-fire-burner", eta: "In 40 mins" },
            { name: "RO / Water Purifier", icon: "fa-glass-water-droplet", eta: "In 44 mins" },
            { name: "Geyser Service", icon: "fa-temperature-high", eta: "In 50 mins" }
          ]
        }
      ]
    },
    "Cleaning": {
      id: 29,
      sections: [
        {
          title: "Home & Room Cleaning",
          items: [
            { name: "Full Home Deep Cleaning", icon: "fa-house-chimney", eta: "In 120 mins" },
            { name: "Bathroom Deep Cleaning", icon: "fa-bath", eta: "In 60 mins" },
            { name: "Kitchen Deep Cleaning", icon: "fa-kitchen-set", eta: "In 75 mins" },
            { name: "Mini Home Cleaning", icon: "fa-broom", eta: "In 45 mins" }
          ]
        },
        {
          title: "Furnishing & Upholstery",
          items: [
            { name: "Sofa & Cushion Cleaning", icon: "fa-couch", eta: "In 60 mins" },
            { name: "Carpet Cleaning", icon: "fa-rug", eta: "In 45 mins" },
            { name: "Mattress Sanitizing", icon: "fa-bed", eta: "In 50 mins" },
            { name: "Balcony & Window Glass", icon: "fa-spray-can-sparkles", eta: "In 40 mins" }
          ]
        }
      ]
    },
    "Painting": {
      id: 30,
      sections: [
        {
          title: "Painting & Waterproofing",
          items: [
            { name: "Full Home Painting", icon: "fa-paint-roller", eta: "In 1 day" },
            { name: "Single Room / Accent Wall", icon: "fa-brush", eta: "In 4 hrs" },
            { name: "Waterproofing & Seepage", icon: "fa-droplet-slash", eta: "In 3 hrs" },
            { name: "Wall Texture & Stencil", icon: "fa-palette", eta: "In 2 hrs" }
          ]
        }
      ]
    },
    "Carpentry": {
      id: 31,
      sections: [
        {
          title: "Repairs & Furniture",
          items: [
            { name: "Door & Window Locks", icon: "fa-lock", eta: "In 40 mins" },
            { name: "Furniture Repair & Assembly", icon: "fa-chair", eta: "In 60 mins" },
            { name: "Drill & Wall Hangings", icon: "fa-hammer", eta: "In 30 mins" },
            { name: "Cupboard & Drawer Hinge", icon: "fa-screwdriver", eta: "In 35 mins" }
          ]
        }
      ]
    },
    "Pest Control": {
      id: 32,
      sections: [
        {
          title: "Pest Management",
          items: [
            { name: "Cockroach & Ant Control", icon: "fa-bug-slash", eta: "In 45 mins" },
            { name: "Bed Bug Management", icon: "fa-shield-halved", eta: "In 60 mins" },
            { name: "Termite Treatment", icon: "fa-tree", eta: "In 90 mins" },
            { name: "Mosquito & Fly Control", icon: "fa-spray-can", eta: "In 40 mins" }
          ]
        }
      ]
    },
    "Home Renovation": {
      id: 33,
      sections: [
        {
          title: "Renovation Services",
          items: [
            { name: "Complete Bathroom Remodel", icon: "fa-bath", eta: "In 3 days" },
            { name: "Modular Kitchen Upgrade", icon: "fa-cubes", eta: "In 5 days" },
            { name: "Flooring & Tiling Work", icon: "fa-table-cells-large", eta: "In 2 days" },
            { name: "False Ceiling & POP", icon: "fa-trowel-bricks", eta: "In 2 days" }
          ]
        }
      ]
    }
  };

  function renderCategoryModalHtml() {
    if (document.getElementById('uc-cat-modal-backdrop')) return;

    const modalHtml = `
      <div id="uc-cat-modal-backdrop" style="display:none; position:fixed; inset:0; z-index:9998; background:rgba(0,0,0,0.6); backdrop-filter:blur(5px); align-items:center; justify-content:center; padding:16px;">
        <div id="uc-cat-modal-box" style="background:#fff; border-radius:22px; width:min(620px, 95vw); max-height:90vh; box-shadow:0 30px 80px rgba(0,0,0,0.3); overflow:hidden; position:relative; display:flex; flex-direction:column; animation: ucModalIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);">
          
          <!-- Close button -->
          <button id="uc-cat-modal-close" style="position:absolute; right:18px; top:18px; width:38px; height:38px; border-radius:50%; background:#f1f3f5; border:none; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#495057; font-size:16px; z-index:10; transition:background 0.15s;">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <!-- Header -->
          <div style="padding:28px 28px 16px; border-bottom:1px solid #f1f3f5;">
            <h2 id="uc-cat-modal-title" style="font-size:22px; font-weight:800; color:#111827; margin:0 0 6px; letter-spacing:-0.02em;">Category</h2>
            <p id="uc-cat-modal-sub" style="font-size:13px; color:#6b7280; margin:0;">Select a sub-service to book certified professionals</p>
          </div>

          <!-- Body -->
          <div id="uc-cat-modal-body" style="padding:20px 28px 28px; overflow-y:auto; flex:1; max-height:65vh;">
            <!-- Rendered dynamically -->
          </div>

        </div>
      </div>
      <style>
        .uc-subcat-card {
          background:#f8f9fa; border:1px solid #e9ecef; border-radius:14px; padding:14px 10px;
          display:flex; flex-direction:column; align-items:center; text-align:center; cursor:pointer;
          transition:all 0.2s cubic-bezier(0.16, 1, 0.3, 1); position:relative; text-decoration:none;
        }
        .uc-subcat-card:hover {
          background:#fff; border-color:#7c3aed; transform:translateY(-3px); box-shadow:0 8px 24px rgba(124,58,237,0.12);
        }
        .uc-subcat-card .icon-wrap {
          width:52px; height:52px; border-radius:14px; background:#eef2ff; color:#4f46e5;
          display:flex; align-items:center; justify-content:center; font-size:22px; margin-bottom:10px;
          transition:transform 0.2s ease;
        }
        .uc-subcat-card:hover .icon-wrap {
          transform:scale(1.08); background:#7c3aed; color:#fff;
        }
        .uc-subcat-card .badge-eta {
          position:absolute; top:8px; right:8px; font-size:10px; font-weight:700; color:#059669;
          background:#ecfdf5; padding:2px 6px; border-radius:6px; letter-spacing:0.02em;
        }
        .uc-subcat-card .item-name {
          font-size:13px; font-weight:600; color:#1f2937; line-height:1.3;
        }
      </style>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    setupEvents();
  }

  function setupEvents() {
    const backdrop = document.getElementById('uc-cat-modal-backdrop');
    const closeBtn = document.getElementById('uc-cat-modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeCategoryModal);
    if (backdrop) {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) closeCategoryModal();
      });
    }
  }

  function openCategoryModal(catName, catId) {
    renderCategoryModalHtml();
    const data = SUB_CATEGORIES_MAP[catName] || {
      id: catId,
      sections: [{
        title: "Available Services",
        items: [
          { name: `${catName} Standard Repair`, icon: "fa-screwdriver-wrench", eta: "In 45 mins" },
          { name: `${catName} Inspection`, icon: "fa-magnifying-glass", eta: "In 30 mins" },
          { name: `${catName} Full Overhaul`, icon: "fa-gears", eta: "In 60 mins" },
          { name: `${catName} Installation`, icon: "fa-wrench", eta: "In 45 mins" }
        ]
      }]
    };

    const targetCatId = catId || data.id || 26;

    document.getElementById('uc-cat-modal-title').textContent = catName;
    document.getElementById('uc-cat-modal-sub').textContent = `Explore verified ${catName.toLowerCase()} solutions at upfront prices`;

    const body = document.getElementById('uc-cat-modal-body');
    body.innerHTML = data.sections.map(sec => `
      <div style="margin-bottom:24px;">
        <h4 style="font-size:14px; font-weight:700; color:#374151; margin:0 0 14px; letter-spacing:-0.01em;">${sec.title}</h4>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(130px, 1fr)); gap:12px;">
          ${sec.items.map(item => `
            <a href="/services/browse?category=${targetCatId}&sub=${encodeURIComponent(item.name)}" class="uc-subcat-card">
              <span class="badge-eta">${item.eta}</span>
              <div class="icon-wrap">
                <i class="fa-solid ${item.icon}"></i>
              </div>
              <div class="item-name">${item.name}</div>
            </a>
          `).join('')}
        </div>
      </div>
    `).join('');

    const backdrop = document.getElementById('uc-cat-modal-backdrop');
    backdrop.style.display = 'flex';
  }

  function closeCategoryModal() {
    const backdrop = document.getElementById('uc-cat-modal-backdrop');
    if (backdrop) backdrop.style.display = 'none';
  }

  // Intercept category tiles on homepage
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cat-tile').forEach(tile => {
      tile.addEventListener('click', (e) => {
        const nameEl = tile.querySelector('.cat-tile-name');
        const catName = nameEl ? nameEl.textContent.trim() : "";
        const href = tile.getAttribute('href') || "";
        const match = href.match(/category=(\d+)/);
        const catId = match ? match[1] : null;

        if (catName) {
          e.preventDefault();
          openCategoryModal(catName, catId);
        }
      });
    });
  });

  window.SugguCategoryModal = window.SuguCategoryModal = {
    open: openCategoryModal,
    close: closeCategoryModal
  };
})();
