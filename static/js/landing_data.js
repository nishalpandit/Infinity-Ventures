// Sugu Services - Master Data & Catalog
const SUGU_DATA = {
  company: {
    name: "Sugu Services",
    tagline: "India's Premier On-Demand Home Services & Bidding Platform",
    founded: "2021",
    customersServed: "10 Million+",
    verifiedPros: "50,000+",
    cities: "32 Cities Across India",
    rating: "4.86",
    warranty: "30-Day Money-Back & Free Re-work Guarantee",
    damageProtection: "Up to ₹10,000 Free Accidental Damage Cover",
    description: "Sugu Services revolutionizes how Indian households care for their homes. Whether you need standard maintenance in 15 minutes or want verified contractors to bid competitively on large renovation projects, Sugu gives you speed, transparent pricing, and unmatched craft quality."
  },

  offers: [
    {
      code: "SUGUFIRST",
      title: "Flat 50% OFF",
      desc: "On your first booking across any Quick Service",
      minOrder: "₹399",
      maxDiscount: "₹200",
      tag: "New User Special",
      color: "from-blue-600 to-indigo-700"
    },
    {
      code: "ACFEST200",
      title: "Save ₹200 on 2+ ACs",
      desc: "Powerjet AC Deep Cleaning & Gas Pressure Check",
      minOrder: "₹899",
      maxDiscount: "₹200",
      tag: "Summer Hit",
      color: "from-cyan-600 to-blue-700"
    },
    {
      code: "RENO40",
      title: "Up to 40% Savings",
      desc: "Post your renovation on Bidding Hub & compare 5+ quotes",
      minOrder: "₹10,000",
      maxDiscount: "Unlimited",
      tag: "Bidding Special",
      color: "from-amber-600 to-orange-700"
    },
    {
      code: "CLEANFREE",
      title: "Free Kitchen Deep Wash",
      desc: "On booking complete Full Home Deep Cleaning",
      minOrder: "₹2,499",
      maxDiscount: "₹799 value",
      tag: "Festival Offer",
      color: "from-emerald-600 to-teal-700"
    }
  ],

  howItWorks: {
    quickService: [
      {
        step: "01",
        title: "Select Service & Customize",
        desc: "Pick from 12 specialized categories with transparent fixed pricing and authentic manufacturer-grade consumables.",
        icon: "layout-grid"
      },
      {
        step: "02",
        title: "Choose Date & 30-Min Slot",
        desc: "Schedule for today or book ahead. We guarantee 15-minute pro assignment with live tracking on GPS.",
        icon: "calendar-clock"
      },
      {
        step: "03",
        title: "Certified Pro Arrives & Delivers",
        desc: "7-step background-checked partner arrives in full Sugu uniform with standardized tools and complete post-cleanup.",
        icon: "shield-check"
      },
      {
        step: "04",
        title: "Pay After Complete Satisfaction",
        desc: "Review the work, pay securely via UPI/Card/Cash, backed by our 30-day no-questions-asked warranty.",
        icon: "badge-check"
      }
    ],
    bidding: [
      {
        step: "01",
        title: "Post Job Requirements in 2 Mins",
        desc: "Specify your project scope (e.g., 3BHK Painting, Kitchen Remodeling), upload photos, and state your target budget.",
        icon: "clipboard-pen"
      },
      {
        step: "02",
        title: "Receive Competitive Bids",
        desc: "Top-rated local contractors and licensed teams review your job and submit itemized quotes within 30 minutes.",
        icon: "trending-down"
      },
      {
        step: "03",
        title: "Compare Profiles & Negotiate",
        desc: "Inspect pro portfolios, customer reviews, past project photos, and counter-offer prices in one click.",
        icon: "scale"
      },
      {
        step: "04",
        title: "Milestone Escrow & Completion",
        desc: "Funds are protected in Sugu Escrow. Payment is released stage-by-stage only when you sign off on milestones.",
        icon: "lock"
      }
    ]
  },

  videos: [
    {
      id: "v1",
      title: "How Sugu Transformed Our 3BHK Living Room via Bidding",
      author: "Pooja & Sameer Kulkarni",
      city: "Bengaluru",
      rating: 5,
      duration: "1:42",
      thumbnail: "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80",
      service: "Home Renovation & Bidding",
      quote: "We got 4 contractor quotes in 2 hours and saved ₹42,000 on our interior revamp! Escrow milestone payment gave us total peace of mind.",
      videoUrl: "https://assets.mixkit.co/videos/preview/mixkit-living-room-with-decorations-and-furniture-41484-large.mp4"
    },
    {
      id: "v2",
      title: "Powerjet AC Deep Clean Review: 15-Min Quick Service",
      author: "Aditya Verma",
      city: "Gurugram",
      rating: 5,
      duration: "1:15",
      thumbnail: "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=800&q=80",
      service: "AC & Appliance Quick Service",
      quote: "The foam-jet washed out 2 years of trapped dust inside our split AC. Cooling returned like a brand new AC, zero mess left behind.",
      videoUrl: "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-working-with-a-screwdriver-42611-large.mp4"
    },
    {
      id: "v3",
      title: "Salon Luxe At Home: Complete Bridal Glow Routine",
      author: "Sneha Mukherjee",
      city: "Mumbai",
      rating: 5,
      duration: "2:04",
      thumbnail: "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=800&q=80",
      service: "Women's Salon & Spa",
      quote: "Single-use sealed hygiene kits and salon-grade O3+ products right in my bedroom. Hands down the safest and most relaxing salon experience.",
      videoUrl: "https://assets.mixkit.co/videos/preview/mixkit-applying-face-cream-at-the-spa-41718-large.mp4"
    }
  ],

  reviews: [
    {
      name: "Dr. Ananya Roy",
      role: "Verified Homeowner",
      city: "South Delhi",
      rating: 5,
      service: "Full Home Deep Cleaning",
      avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80",
      date: "2 days ago",
      comment: "The team of 3 pros spent 5 hours scrubbing every corner, tile grout, and grease stain behind the kitchen hob. Looks even cleaner than handover day!",
      badge: "Quick Service Verified"
    },
    {
      name: "Rajeshwar Iyer",
      role: "Apartment Secretary",
      city: "Chennai",
      rating: 5,
      service: "Septic Tank & Pipeline Desilting",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
      date: "Last week",
      comment: "Posted our society requirement on Sugu Bidding. We shortlisted a licensed vacuum truck operator who bid ₹8,000 lower than our previous vendor. Work was flawless.",
      badge: "Bidding Champion"
    },
    {
      name: "Meera Nair",
      role: "Architect & Designer",
      city: "Kochi",
      rating: 5,
      service: "Carpentry & Custom Wardrobes",
      avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=200&q=80",
      date: "3 days ago",
      comment: "The carpenter had laser measurement tools and German fittings in stock. Finished soft-close hinge alignment for 6 cabinets in under 2 hours.",
      badge: "Quick Service Verified"
    }
  ],

  categories: [
    {
      id: "ac_services",
      name: "AC Services",
      iconFile: "ac_appliance.png",
      tagline: "Powerjet Clean, Gas Refill, Repair & Installation",
      rating: "4.86 (2.1M Reviews)",
      startingPrice: "₹399",
      subcategories: [
        {
          id: "ac_service",
          name: "AC Service & Deep Clean",
          items: [
            {
              id: "ac_foam_jet",
              title: "Powerjet AC Deep Cleaning (Foam Wash)",
              rating: "4.87",
              reviews: "640K+",
              price: 499,
              originalPrice: 699,
              time: "45 mins",
              badge: "Bestseller",
              image: "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=600&q=80",
              features: [
                "2X deeper foam wash of indoor cooling coils & blower",
                "High-pressure jet wash of outdoor unit",
                "Free gas leak & ampere inspection check",
                "30-day cooling & leakage guarantee"
              ]
            },
            {
              id: "ac_anti_rust",
              title: "AC Deep Clean + Anti-Rust Shield",
              rating: "4.91",
              reviews: "180K+",
              price: 749,
              originalPrice: 999,
              time: "60 mins",
              badge: "Recommended",
              image: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
              features: [
                "Includes complete Powerjet Foam wash",
                "Hydrophobic anti-rust coating on condenser coils",
                "Extends AC lifespan & prevents premature gas leak",
                "60-day warranty card included"
              ]
            }
          ]
        },
        {
          id: "ac_repair",
          name: "AC Repair & Gas Refill",
          items: [
            {
              id: "ac_gas_refill",
              title: "Complete AC Gas Top-up & Refill",
              rating: "4.82",
              reviews: "220K+",
              price: 1899,
              originalPrice: 2499,
              time: "75 mins",
              badge: "Cooling Fix",
              image: "https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=600&q=80",
              features: [
                "Nitrogen leak testing & vacuum pressurization",
                "100% pure R32 / R410A / R22 refrigerant cylinder filling",
                "Current amp & temperature differential check",
                "90-day comprehensive gas warranty"
              ]
            },
            {
              id: "ac_checkup",
              title: "AC Diagnostic Checkup & Minor Repair",
              rating: "4.79",
              reviews: "95K+",
              price: 249,
              originalPrice: 399,
              time: "30 mins",
              badge: "Affordable",
              image: "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=600&q=80",
              features: [
                "Complete inspection of compressor, PCB, and capacitor",
                "Inspection fee waived if repair accepted",
                "Transparent quote before replacing any spare parts"
              ]
            }
          ]
        },
        {
          id: "ac_install",
          name: "AC Installation & Uninstallation",
          items: [
            {
              id: "ac_install_split",
              title: "Split AC Standard Installation",
              rating: "4.85",
              reviews: "150K+",
              price: 999,
              originalPrice: 1499,
              time: "90 mins",
              badge: "Expert Fit",
              image: "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=600&q=80",
              features: [
                "Heavy-duty vibration-free outdoor wall bracket mounting",
                "Copper pipe flare connection with vacuum test",
                "Drilling & drain pipe alignment with neat wall sealing"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "home_appliances",
      name: "Home Appliances Repair",
      iconFile: "ac_appliance.png",
      tagline: "Washing Machine, Refrigerator, Microwave & RO Repair",
      rating: "4.87 (1.4M Reviews)",
      startingPrice: "₹299",
      subcategories: [
        {
          id: "wm_service_sub",
          name: "Washing Machine",
          items: [
            {
              id: "wm_service",
              title: "Front/Top Load Washing Machine Deep Scrub",
              rating: "4.83",
              reviews: "110K+",
              price: 599,
              originalPrice: 849,
              time: "60 mins",
              badge: "Hygiene",
              image: "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?auto=format&fit=crop&w=600&q=80",
              features: [
                "Drum disassembly & descaling of tub mildew",
                "Drain pump & lint filter clearing",
                "Vibration & noise balancing check"
              ]
            },
            {
              id: "wm_repair",
              title: "Washing Machine Motor & Drain Issue Repair",
              rating: "4.81",
              reviews: "85K+",
              price: 349,
              originalPrice: 499,
              time: "45 mins",
              badge: "Quick Fix",
              image: "https://images.unsplash.com/photo-1582735689369-4fe89db7114c?auto=format&fit=crop&w=600&q=80",
              features: [
                "Belt, clutch, inlet valve or drum suspension repair",
                "Factory authentic spares provided",
                "30-day post-service warranty"
              ]
            }
          ]
        },
        {
          id: "fridge_service_sub",
          name: "Refrigerator & Freezer",
          items: [
            {
              id: "fridge_service",
              title: "Refrigerator Cooling & Compressor Tune-Up",
              rating: "4.85",
              reviews: "82K+",
              price: 399,
              originalPrice: 599,
              time: "45 mins",
              badge: "Popular",
              image: "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80",
              features: [
                "Thermostat & defrost timer calibration",
                "Condenser coil dust evacuation",
                "Door gasket magnetic seal leak test"
              ]
            }
          ]
        },
        {
          id: "microwave_ro_sub",
          name: "Microwave & Water Purifier",
          items: [
            {
              id: "ro_service",
              title: "RO Water Purifier Filter & Membrane Replacement",
              rating: "4.88",
              reviews: "190K+",
              price: 499,
              originalPrice: 699,
              time: "40 mins",
              badge: "Purity Check",
              image: "https://images.unsplash.com/photo-1585771724684-38269d6639fd?auto=format&fit=crop&w=600&q=80",
              features: [
                "Sediment, carbon filter & RO membrane test",
                "Digital TDS balancing and purity certification",
                "Food-grade pipe sanitization"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "cleaning",
      name: "Home Cleaning",
      iconFile: "cleaning.png",
      tagline: "Deep Home, Kitchen, Bathroom & Sofa Wash",
      rating: "4.88 (3.5M Reviews)",
      startingPrice: "₹449",
      subcategories: [
        {
          id: "home_deep_clean",
          name: "Full Home Deep Cleaning",
          items: [
            {
              id: "clean_2bhk",
              title: "Complete 2BHK Intensive Deep Cleaning",
              rating: "4.89",
              reviews: "450K+",
              price: 2699,
              originalPrice: 3499,
              time: "5-6 hours",
              badge: "Most Popular",
              image: "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=600&q=80",
              features: [
                "3-member verified expert crew with heavy single-disc machines",
                "Degreasing of kitchen tiles, chimney, and cabinets",
                "Descaling of bathroom tiles, taps, and sanitary fittings",
                "Dry vacuuming of carpets, sofa, and mattress"
              ]
            },
            {
              id: "clean_3bhk",
              title: "Complete 3BHK Intensive Deep Cleaning",
              rating: "4.92",
              reviews: "310K+",
              price: 3499,
              originalPrice: 4499,
              time: "6-7 hours",
              badge: "Value Pack",
              image: "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=600&q=80",
              features: [
                "4-member crew with industrial taski chemicals & wet vacuum",
                "Full balcony & window track scrubbing",
                "Door, switchboard & fan sterilization"
              ]
            }
          ]
        },
        {
          id: "room_specific",
          name: "Bathroom & Kitchen Intensive",
          items: [
            {
              id: "bath_deep",
              title: "Intensive Bathroom Descaling & Deep Scrub",
              rating: "4.86",
              reviews: "780K+",
              price: 499,
              originalPrice: 699,
              time: "60 mins",
              badge: "High Demand",
              image: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80",
              features: [
                "Hard water stain removal from glass partition & tiles",
                "Tap & shower chrome buffing to mirror finish",
                "Toilet pot deep acid-free sanitization"
              ]
            },
            {
              id: "kitchen_deep",
              title: "Kitchen Chimney & Cabinet Degreasing",
              rating: "4.84",
              reviews: "340K+",
              price: 999,
              originalPrice: 1399,
              time: "90 mins",
              badge: "Oil-Free",
              image: "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80",
              features: [
                "Chimney filter removal & carbon soak clean",
                "Tough oil splatter elimination from backsplash & hob",
                "Exterior cabinet wipe & countertop disinfection"
              ]
            }
          ]
        },
        {
          id: "upholstery",
          name: "Sofa & Carpet Wet Extraction",
          items: [
            {
              id: "sofa_3seater",
              title: "3-Seater Fabric Sofa Shampooing",
              rating: "4.87",
              reviews: "290K+",
              price: 799,
              originalPrice: 1099,
              time: "60 mins",
              badge: "Stain Buster",
              image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80",
              features: [
                "Deep dry vacuuming of allergen mites and food crumbs",
                "Foam shampooing with German Karcher extraction machine",
                "Quick-dry moisture extraction leaving fabric fresh"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "electrical",
      name: "Electrical",
      iconFile: "electrical.png",
      tagline: "Wiring, Fans, MCB, Switches & Smart Fixtures",
      rating: "4.86 (1.8M Reviews)",
      startingPrice: "₹149",
      subcategories: [
        {
          id: "elec_install",
          name: "Fan, Light & Chandelier",
          items: [
            {
              id: "fan_install",
              title: "Ceiling Fan Installation / Replacement",
              rating: "4.85",
              reviews: "320K+",
              price: 199,
              originalPrice: 299,
              time: "30 mins",
              badge: "Quick",
              image: "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=600&q=80",
              features: [
                "Safe ceiling mounting with balance check",
                "Hook & regulator connection check",
                "Post-installation speed test"
              ]
            },
            {
              id: "light_install",
              title: "Decorative Light / Chandelier Fitment",
              rating: "4.90",
              reviews: "95K+",
              price: 349,
              originalPrice: 499,
              time: "45 mins",
              badge: "Precision",
              image: "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=600&q=80",
              features: [
                "Secure anchor drilling for crystal chandeliers",
                "Concealed wiring dressing",
                "30-day electrical safety guarantee"
              ]
            }
          ]
        },
        {
          id: "elec_repair",
          name: "Switch, MCB & Fuse Repairs",
          items: [
            {
              id: "switch_replace",
              title: "Switch / Socket Replacement (Up to 2 Units)",
              rating: "4.82",
              reviews: "180K+",
              price: 149,
              originalPrice: 220,
              time: "20 mins",
              badge: "Essential",
              image: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
              features: [
                "Modular plate fitment & earthing verification",
                "Spark-proof insulated wire terminal crimping"
              ]
            },
            {
              id: "mcb_tripping",
              title: "MCB Tripping & Short Circuit Diagnosis",
              rating: "4.89",
              reviews: "140K+",
              price: 399,
              originalPrice: 599,
              time: "45 mins",
              badge: "Emergency",
              image: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=600&q=80",
              features: [
                "Megger insulation check & phase load balance",
                "Rapid detection of damaged concealed wires",
                "Instant replacement of faulty MCB/RCCB"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "plumbing",
      name: "Plumbing",
      iconFile: "plumbing.png",
      tagline: "Leakage, Pipe Blocks, Taps & Sanitary Fitments",
      rating: "4.85 (1.6M Reviews)",
      startingPrice: "₹149",
      subcategories: [
        {
          id: "plumb_tap",
          name: "Tap, Mixer & Shower Repair",
          items: [
            {
              id: "tap_repair",
              title: "Dripping Tap / Spindle Replacement",
              rating: "4.84",
              reviews: "260K+",
              price: 149,
              originalPrice: 249,
              time: "25 mins",
              badge: "Fast Fix",
              image: "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&w=600&q=80",
              features: [
                "Washer, ceramic disc cartridge or spindle change",
                "Teflon tape seal to prevent thread leaks",
                "Full pressure testing"
              ]
            },
            {
              id: "shower_mixer",
              title: "Wall Mixer / Diverter Cartridge Repair",
              rating: "4.88",
              reviews: "130K+",
              price: 399,
              originalPrice: 549,
              time: "45 mins",
              badge: "Expert",
              image: "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=600&q=80",
              features: [
                "Hot & cold water mixing ratio calibration",
                "Concealed diverter gasket overhaul",
                "Zero wall damage promise"
              ]
            }
          ]
        },
        {
          id: "plumb_blocks",
          name: "Blocked Drain & Leakages",
          items: [
            {
              id: "sink_block",
              title: "Kitchen Sink / Washbasin Drain Blockage Clearing",
              rating: "4.86",
              reviews: "310K+",
              price: 299,
              originalPrice: 420,
              time: "35 mins",
              badge: "Mess-Free",
              image: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80",
              features: [
                "Heavy-duty mechanical spring coil snake cleaning",
                "Food trap & bottle trap disassembly and flushing",
                "Free enzyme anti-clog treatment"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "carpentry",
      name: "Carpentry",
      iconFile: "carpentry.png",
      tagline: "Repairs, Furniture Assembly, Locks & Fittings",
      rating: "4.87 (950K Reviews)",
      startingPrice: "₹199",
      subcategories: [
        {
          id: "carp_repair",
          name: "Furniture & Door Fixes",
          items: [
            {
              id: "door_lock",
              title: "Main Door Cylindrical / Mortise Lock Installation",
              rating: "4.88",
              reviews: "140K+",
              price: 349,
              originalPrice: 499,
              time: "40 mins",
              badge: "High Security",
              image: "https://images.unsplash.com/photo-1558997519-83ea9252def8?auto=format&fit=crop&w=600&q=80",
              features: [
                "Precision router chiseling for Godrej/Europa locks",
                "Striker plate and keyhole alignment",
                "Smooth latch and deadbolt operation"
              ]
            },
            {
              id: "hinge_fix",
              title: "Wardrobe / Kitchen Cabinet Hinge Replacement",
              rating: "4.83",
              reviews: "190K+",
              price: 199,
              originalPrice: 299,
              time: "30 mins",
              badge: "Top Seller",
              image: "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=600&q=80",
              features: [
                "Soft-close hydraulic hinge installation",
                "Door sag correction and gap alignment"
              ]
            }
          ]
        },
        {
          id: "carp_drill",
          name: "Drill & Hang Services",
          items: [
            {
              id: "drill_hang",
              title: "Drill & Hang (TV, Paintings, Mirror, Rods)",
              rating: "4.90",
              reviews: "480K+",
              price: 249,
              originalPrice: 350,
              time: "30 mins",
              badge: "Precise",
              image: "https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?auto=format&fit=crop&w=600&q=80",
              features: [
                "Laser level alignment for zero tilt",
                "Rawl plugs & heavy duty anchors included",
                "Up to 3 hangings in single booking"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "painting_upgrade",
      name: "Painting",
      iconFile: "painting_upgrade.png",
      tagline: "Fresh Coat, Accent Walls, Waterproofing & Color Consult",
      rating: "4.91 (680K Reviews)",
      startingPrice: "₹1,499",
      subcategories: [
        {
          id: "paint_walls",
          name: "Room & Accent Painting",
          items: [
            {
              id: "single_room_paint",
              title: "Single Room Refresh (Asian Paints Tractor Emulsion)",
              rating: "4.89",
              reviews: "120K+",
              price: 1899,
              originalPrice: 2499,
              time: "1 Day",
              badge: "Quick Refresh",
              image: "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=600&q=80",
              features: [
                "2 coats of premium washable paint with roller finish",
                "Full floor and furniture masking with plastic sheets",
                "Minor putty crack filling included",
                "Post-painting clean up"
              ]
            },
            {
              id: "accent_wall",
              title: "Designer Accent Feature Wall & Texture",
              rating: "4.93",
              reviews: "88K+",
              price: 2499,
              originalPrice: 3200,
              time: "4-5 hours",
              badge: "Designer Pick",
              image: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=600&q=80",
              features: [
                "Metallic, Stucco or Geometric Stencil finish",
                "Free color consultancy by certified interior expert",
                "Long-lasting scratch resistant formulation"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "pest_control",
      name: "Pest Control",
      iconFile: "pest_control.png",
      tagline: "Cockroach, Termite, Bedbug & Mosquito Shield",
      rating: "4.87 (1.4M Reviews)",
      startingPrice: "₹499",
      subcategories: [
        {
          id: "pest_roach",
          name: "Cockroach & Ant Control",
          items: [
            {
              id: "roach_herbal",
              title: "Advanced Herbal Gel + Spray Cockroach Treatment",
              rating: "4.88",
              reviews: "610K+",
              price: 599,
              originalPrice: 899,
              time: "45 mins",
              badge: "Eco-Friendly",
              image: "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80",
              features: [
                "100% odorless Bayer gel dots in cabinets & hinges",
                "Drainage line insecticide boundary barrier",
                "Child & pet safe formulation",
                "90-day warranty with free retreatment"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "home_renovation",
      name: "Home Renovation & Remodeling",
      iconFile: "home_renovation.png",
      tagline: "Modular Kitchen, False Ceiling, Bath Remodel & Tiling",
      rating: "4.92 (420K Reviews)",
      startingPrice: "₹4,999",
      subcategories: [
        {
          id: "reno_pack",
          name: "Room Renovations",
          items: [
            {
              id: "kitchen_makeover",
              title: "Modular Kitchen Cabinet & Granite Overhaul",
              rating: "4.94",
              reviews: "54K+",
              price: 14999,
              originalPrice: 19999,
              time: "3-5 Days",
              badge: "Premium Upgrade",
              image: "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=600&q=80",
              features: [
                "3D design rendering & material consultation",
                "BWP marine plywood cabinets with Hafele fittings",
                "Quartz or granite counter replacement",
                "5-year structural warranty"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "septic_tank",
      name: "Septic Tank Cleaning",
      iconFile: "septic_tank.png",
      tagline: "Vacuum Sludge Pumping, Soak Pit & Desilting",
      rating: "4.86 (210K Reviews)",
      startingPrice: "₹2,499",
      subcategories: [
        {
          id: "septic_pump",
          name: "Vacuum Tank Evacuation",
          items: [
            {
              id: "septic_tank_3000l",
              title: "3000L - 5000L Vacuum Truck Sludge Evacuation",
              rating: "4.89",
              reviews: "45K+",
              price: 3199,
              originalPrice: 4200,
              time: "90 mins",
              badge: "Certified Fleet",
              image: "https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=600&q=80",
              features: [
                "High-power motorized vacuum suction pump",
                "Non-spill reinforced hose with zero road leakage",
                "Microbial odor neutralizing enzyme treatment",
                "Govt-approved eco dumping protocol"
              ]
            }
          ]
        }
      ]
    },

    {
      id: "womens_salon_spa",
      name: "Women's Salon & Spa",
      iconFile: "womens_salon_spa.png",
      tagline: "At-Home Beauty or Book Top Luxury Parlours",
      rating: "4.91 (4.2M Reviews)",
      startingPrice: "₹349",
      subcategories: [
        {
          id: "salon_facial",
          name: "Facials & Cleanup",
          items: [
            {
              id: "facial_o3",
              title: "O3+ Bridal Glow Luxury Facial",
              rating: "4.93",
              reviews: "720K+",
              price: 1399,
              originalPrice: 1999,
              time: "75 mins",
              badge: "Celebrity Glow",
              image: "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=600&q=80",
              features: [
                "Sealed single-dose mono pack for absolute hygiene",
                "Includes blackhead extraction & ultrasonic scrubber",
                "Revitalizing peel-off rubber mask",
                "Relaxing neck and shoulder acupressure massage"
              ]
            },
            {
              id: "facial_lotus",
              title: "Lotus Herbal Skin Radiance & De-Tan",
              rating: "4.86",
              reviews: "340K+",
              price: 899,
              originalPrice: 1299,
              time: "55 mins",
              badge: "Herbal Care",
              image: "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80",
              features: [
                "Natural fruit enzyme peel to lift sun tanning",
                "Gentle herbal walnut scrub exfoliation",
                "Cooling aloe vera gel hydrator"
              ]
            }
          ]
        },
        {
          id: "salon_waxing",
          name: "Waxing & Hair Removal",
          items: [
            {
              id: "waxing_rica",
              title: "Full Arms + Full Legs + Underarms Rica Wax",
              rating: "4.89",
              reviews: "890K+",
              price: 799,
              originalPrice: 1199,
              time: "50 mins",
              badge: "Painless",
              image: "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
              features: [
                "Imported Italian Rica liposoluble wax (colophony-free)",
                "Gentle on sensitive skin with pre & post wax lotions",
                "Disposable bedsheet, spatula, and sanitizing wipes"
              ]
            },
            {
              id: "waxing_bikini",
              title: "Rica Brazilian / Bikini Wax + Soothing Serum",
              rating: "4.92",
              reviews: "210K+",
              price: 999,
              originalPrice: 1499,
              time: "40 mins",
              badge: "Gentle Care",
              image: "https://images.unsplash.com/photo-1512290900672-1f41d9990bfb?auto=format&fit=crop&w=600&q=80",
              features: [
                "Peel-off strip-less bead wax for maximum comfort",
                "Trained senior intimate hygiene aesthetician",
                "100% private, sanitized disposable kit"
              ]
            }
          ]
        },
        {
          id: "salon_manipedi",
          name: "Pedicure & Manicure",
          items: [
            {
              id: "pedi_rose",
              title: "Rose Petal & Sea Salt Luxe Spa Pedicure",
              rating: "4.91",
              reviews: "410K+",
              price: 649,
              originalPrice: 899,
              time: "50 mins",
              badge: "Relaxing",
              image: "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=600&q=80",
              features: [
                "Warm herbal foot soak with aromatic rose crystals",
                "Dead skin pumice buffer & heel callus softening",
                "15-minute calf and foot acupressure massage"
              ]
            }
          ]
        },
        {
          id: "salon_hairspa",
          name: "Hair Spa & Styling",
          items: [
            {
              id: "hair_spa_loreal",
              title: "L'Oreal Professional Deep Nourish Hair Spa",
              rating: "4.88",
              reviews: "320K+",
              price: 899,
              originalPrice: 1299,
              time: "60 mins",
              badge: "Silky Shine",
              image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=600&q=80",
              features: [
                "Deep moisture infusion for frizz & split end repair",
                "20-minute relaxing neck, shoulder & scalp massage",
                "Hot towel steam treatment for cuticles"
              ]
            }
          ]
        }
      ],
      // CURATED DIRECTORY OF TOP LUXURY PARLOURS / SALONS
      parlours: [
        {
          id: "lakme_luxe",
          name: "Lakmé Salon Luxe",
          brandTag: "Runway Certified",
          tagline: "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
          rating: "4.94 ★ (3,800+ reviews)",
          location: "100ft Road, Indiranagar",
          distance: "0.8 km away",
          timings: "10:00 AM - 09:00 PM",
          image: "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Lakmé Fashion Week Certified Stylists",
            "Private VIP Bridal Lounge",
            "Complimentary Gourmet Brewed Coffee"
          ],
          services: [
            {
              id: "lakme_moroccan_spa",
              title: "Moroccan Oil Hydration Hair Ritual & Blowout",
              category: "Hair Care",
              price: 1899,
              originalPrice: 2499,
              time: "60 mins",
              image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
              desc: "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
            },
            {
              id: "lakme_bridal_hd",
              title: "Runway HD Airbrush Bridal Transformation",
              category: "Bridal Studio",
              price: 8999,
              originalPrice: 12000,
              time: "3 Hours",
              image: "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
              desc: "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
            },
            {
              id: "lakme_collagen_facial",
              title: "Lakmé Youth Infinity Collagen Boost Facial",
              category: "Skin Bar",
              price: 2499,
              originalPrice: 3200,
              time: "75 mins",
              image: "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
              desc: "Infused with pure peptides and micro-current lifting probes for an instant youthful sculpting effect."
            },
            {
              id: "lakme_gel_nails",
              title: "French Ombre BIAB Gel Extensions & Nail Art",
              category: "Nail Lounge",
              price: 1599,
              originalPrice: 2100,
              time: "75 mins",
              image: "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=500&q=80",
              desc: "Builder In A Bottle (BIAB) nail hardening overlay with customized crystal rhinestones and gel gloss."
            }
          ]
        },
        {
          id: "enrich_salon",
          name: "Enrich Salon & Luxury Spa",
          brandTag: "Kerastase Paris",
          tagline: "Kerastase Scalp Diagnostics & Dermalogica Skin Bar",
          rating: "4.91 ★ (2,400+ reviews)",
          location: "4th Block, Koramangala",
          distance: "1.2 km away",
          timings: "09:30 AM - 09:30 PM",
          image: "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Kerastase Micro-Camera Scalp Diagnostic",
            "Zero Ammonia L'Oreal INOA Color Bar",
            "Aroma Steam Jacuzzi Foot Reflexology"
          ],
          services: [
            {
              id: "enrich_fusio_dose",
              title: "Kerastase Fusio-Dose Instant Hair Transformation",
              category: "Hair Care",
              price: 2299,
              originalPrice: 2999,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
              desc: "Custom blend of Kerastase concentre and booster tailored to your scalp type by certified trichologist."
            },
            {
              id: "enrich_proskin_60",
              title: "Dermalogica ProSkin 60 Customized Skin Treatment",
              category: "Skin Bar",
              price: 2899,
              originalPrice: 3800,
              time: "60 mins",
              image: "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
              desc: "Deep sonic pore cleansing, acid-free resurfacing peel, and calming colloidal masque."
            },
            {
              id: "enrich_balayage",
              title: "Sun-kissed Balayage / Global Color by Art Director",
              category: "Hair Care",
              price: 4499,
              originalPrice: 5999,
              time: "2.5 Hours",
              image: "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=500&q=80",
              desc: "Freehand dimensional French balayage with Olaplex bond multiplier protection included."
            }
          ]
        },
        {
          id: "bblunt_studio",
          name: "BBlunt Premium Studio",
          brandTag: "Celebrity Favorite",
          tagline: "Bollywood Celebrity Haircuts, Olaplex & Balayage Bar",
          rating: "4.89 ★ (1,900+ reviews)",
          location: "Lavelle Road, Central Bengaluru",
          distance: "2.1 km away",
          timings: "10:00 AM - 08:30 PM",
          image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Celebrity Master Stylists on Floor",
            "Olaplex Molecular Bond Multiplier Lab",
            "Complimentary Face Shape & Hair Consultation"
          ],
          services: [
            {
              id: "bblunt_signature_cut",
              title: "BBlunt Signature Precision Restyle by Art Director",
              category: "Hair Care",
              price: 1499,
              originalPrice: 1999,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
              desc: "Bespoke cut customized to your bone structure, followed by blowout and texturizing."
            },
            {
              id: "bblunt_olaplex_repair",
              title: "Olaplex No. 1 & 2 Molecular Damage Reversal",
              category: "Hair Care",
              price: 2999,
              originalPrice: 3999,
              time: "60 mins",
              image: "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
              desc: "Rebuilds broken disulfide bonds in chemically treated or bleached hair."
            }
          ]
        },
        {
          id: "toni_guy",
          name: "Toni & Guy Essensuals",
          brandTag: "British Heritage",
          tagline: "London Precision Cuts, Scalp Rituals & Brazilian Cysteine",
          rating: "4.88 ★ (1,600+ reviews)",
          location: "Whitefield Main Road",
          distance: "1.5 km away",
          timings: "09:00 AM - 09:00 PM",
          image: "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Toni & Guy London Academy Certified Stylists",
            "Organic Strip-less Brazilian Wax Bar",
            "Private Soundproof Spa Suites"
          ],
          services: [
            {
              id: "tg_cysteine_smooth",
              title: "Formaldehyde-Free Brazilian Cysteine Hair Smoothing",
              category: "Hair Care",
              price: 6499,
              originalPrice: 8500,
              time: "3 Hours",
              image: "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=500&q=80",
              desc: "100% safe non-toxic amino acid protein infusion for frizz-free glass hair lasting 4-6 months."
            },
            {
              id: "tg_sothys_facial",
              title: "Sothys Paris Illuminating Glow Caviar Facial",
              category: "Skin Bar",
              price: 3199,
              originalPrice: 4200,
              time: "75 mins",
              image: "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
              desc: "French luxury marine algae and caviar extract to intensely hydrate and plump skin."
            }
          ]
        },
        {
          id: "naturals_sig",
          name: "Naturals Signature & Ayur Spa",
          brandTag: "Ayurvedic & Herbal",
          tagline: "24K Gold Facials, Herbal Scalp Therapy & Henna Studio",
          rating: "4.83 ★ (4,100+ reviews)",
          location: "Sector 2, HSR Layout",
          distance: "0.6 km away",
          timings: "09:00 AM - 09:30 PM",
          image: "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "100% Chemical-free Organic Formulations",
            "Fast 30-min Service Window",
            "Most Affordable Luxury Chain in India"
          ],
          services: [
            {
              id: "naturals_gold_facial",
              title: "24K Pure Gold Leaf Radiance Facial",
              category: "Skin Bar",
              price: 1599,
              originalPrice: 2200,
              time: "60 mins",
              image: "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=500&q=80",
              desc: "Gold foil infusion to boost blood circulation and produce an authentic golden glow."
            },
            {
              id: "naturals_ayur_headspa",
              title: "Ayurvedic Kesh Kanti Warm Herb Oil Therapy",
              category: "Hair Care",
              price: 999,
              originalPrice: 1499,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=500&q=80",
              desc: "Warm bhringraj and brahmi oils massaged into marma points to relieve stress and stop hair fall."
            }
          ]
        }
      ]
    },

    {
      id: "mens_salon_massage",
      name: "Men's Salon & Massage",
      iconFile: "mens_salon_massage.png",
      tagline: "At-Home Grooming or Book Top Luxury Barbershops",
      rating: "4.87 (2.4M Reviews)",
      startingPrice: "₹249",
      subcategories: [
        {
          id: "mens_groom",
          name: "Hair & Beard Styling",
          items: [
            {
              id: "mens_cut_beard",
              title: "Precision Haircut + Beard Grooming + Scalp Massage",
              rating: "4.88",
              reviews: "540K+",
              price: 399,
              originalPrice: 599,
              time: "45 mins",
              badge: "Gentlemen's Pick",
              image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=600&q=80",
              features: [
                "Sterilized tools & freshly laundered disposable cape",
                "Fade styling & razor-sharp beard edging",
                "10-min cooling herbal oil head massage",
                "Post-cut hot towel wipe"
              ]
            },
            {
              id: "mens_beard_color",
              title: "Beard Sharp Shaping + Ammonia-Free Color",
              rating: "4.84",
              reviews: "180K+",
              price: 299,
              originalPrice: 449,
              time: "30 mins",
              badge: "Grey Coverage",
              image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=600&q=80",
              features: [
                "Natural black or dark brown tint application",
                "Beard line trimming with single-use sterile blade",
                "Skin-stain free barrier gel"
              ]
            }
          ]
        },
        {
          id: "mens_skin",
          name: "Face Care & Detan",
          items: [
            {
              id: "mens_charcoal_facial",
              title: "Activated Charcoal Deep Pore Detan Facial",
              rating: "4.90",
              reviews: "220K+",
              price: 799,
              originalPrice: 1199,
              time: "45 mins",
              badge: "Pollution Defense",
              image: "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=600&q=80",
              features: [
                "Removes pollution dirt, excess sebum & dead skin",
                "Blackhead & whitehead nose extraction",
                "Peel-off volcanic clay mask"
              ]
            }
          ]
        },
        {
          id: "mens_massage_sub",
          name: "Therapeutic Massages",
          items: [
            {
              id: "mens_massage",
              title: "60-Min Deep Tissue Stress Buster Massage",
              rating: "4.92",
              reviews: "210K+",
              price: 1199,
              originalPrice: 1699,
              time: "60 mins",
              badge: "Therapeutic",
              image: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=600&q=80",
              features: [
                "Certified physiotherapist-trained masseur",
                "Warm sesame or aromatic almond oil blend",
                "Targets shoulder stiffness, lower back tension & fatigue",
                "Disposable massage table setup"
              ]
            }
          ]
        }
      ],
      // CURATED DIRECTORY OF TOP LUXURY MEN'S BARBERSHOPS & LOUNGES
      parlours: [
        {
          id: "truefitt_hill",
          name: "Truefitt & Hill Luxury Barbershop",
          brandTag: "Royal Warrant (London 1805)",
          tagline: "The World's Oldest Luxury Barbershop • Indulgent Grooming",
          rating: "4.97 ★ (2,400+ reviews)",
          location: "Lavelle Road, Central Bengaluru",
          distance: "1.1 km away",
          timings: "08:30 AM - 09:00 PM",
          image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Royal Shave with Hot Towels & Badger Brush",
            "Private Gentleman's Grooming Suite",
            "Complimentary Espresso & Single Malt Bar"
          ],
          services: [
            {
              id: "th_royal_shave",
              title: "The Royal Shave & Pre-Shave Essential Oil Ritual",
              category: "Royal Shave",
              price: 2499,
              originalPrice: 3200,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
              desc: "Traditional hot towel wrap, badger hair brush lathering, straight razor precision shave, and aftershave balm."
            },
            {
              id: "th_royal_cut",
              title: "Signature Royal Haircut & Scalp Massage by Master Barber",
              category: "Hair Styling",
              price: 2199,
              originalPrice: 2800,
              time: "50 mins",
              image: "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=500&q=80",
              desc: "Consultation, precision shear cut tailored to face shape, revitalizing scalp shampoo, and friction lotion massage."
            },
            {
              id: "th_exec_manipedi",
              title: "Executive Hand & Foot Grooming Lounge",
              category: "Hands & Feet",
              price: 1899,
              originalPrice: 2400,
              time: "60 mins",
              image: "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=500&q=80",
              desc: "Nail detailing, cuticle overhaul, dead skin exfoliation, and deep pressure acupressure hand/foot massage."
            },
            {
              id: "th_scalp_detox",
              title: "Rosemary & Mint Invigorating Scalp Therapy",
              category: "Scalp Care",
              price: 1499,
              originalPrice: 1999,
              time: "40 mins",
              image: "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=500&q=80",
              desc: "Essential oil stimulation to promote hair root density, ease migraine fatigue, and detoxify follicles."
            }
          ]
        },
        {
          id: "bounce_men",
          name: "Bounce Style Lounge for Men",
          brandTag: "Celebrity Barbers",
          tagline: "Laser Fade Artistry, Beard Sculpting & Kerastase Homme",
          rating: "4.92 ★ (1,850+ reviews)",
          location: "5th Block, Koramangala",
          distance: "0.9 km away",
          timings: "09:00 AM - 09:30 PM",
          image: "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Laser-Aligned Razor Edging & Fade Bar",
            "Kerastase Homme Diagnostic Micro-Camera",
            "Complimentary Cold Brew Coffee"
          ],
          services: [
            {
              id: "bounce_fade_beard",
              title: "Precision Skin Fade + Razor Sharp Beard Architecture",
              category: "Hair & Beard",
              price: 999,
              originalPrice: 1499,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
              desc: "Seamless taper fade with straight razor lineup, hot foam edging, and beard conditioning oil."
            },
            {
              id: "bounce_kerastase_homme",
              title: "Kerastase Homme Anti-Hair Fall Scalp Booster",
              category: "Scalp Care",
              price: 1799,
              originalPrice: 2400,
              time: "45 mins",
              image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
              desc: "Aminexil & arginine infusion to strengthen hair fiber roots and stimulate micro-circulation."
            },
            {
              id: "bounce_charcoal_peel",
              title: "Charcoal Black Peel Deep Detox Facial",
              category: "Face Care",
              price: 1299,
              originalPrice: 1800,
              time: "50 mins",
              image: "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=500&q=80",
              desc: "Bamboo charcoal suction mask to purge blackheads, tan, and city grime."
            }
          ]
        },
        {
          id: "toni_guy_men",
          name: "Toni & Guy Men's Barbershop",
          brandTag: "London Barbershop",
          tagline: "London Precision Fades & Hot Towel Beard Architecture",
          rating: "4.89 ★ (1,400+ reviews)",
          location: "100ft Road, Indiranagar",
          distance: "0.7 km away",
          timings: "09:00 AM - 09:00 PM",
          image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Toni & Guy London Academy Trained Barbers",
            "Beard Architecture with Steam Infusion",
            "Express 30-min Executive Turnaround"
          ],
          services: [
            {
              id: "tg_men_cut",
              title: "London Precision Restyle & Texture Cut",
              category: "Hair Styling",
              price: 1299,
              originalPrice: 1700,
              time: "40 mins",
              image: "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=500&q=80",
              desc: "Contemporary scissor-over-comb texturizing with London Label.m grooming clay finish."
            },
            {
              id: "tg_beard_arch",
              title: "Beard Architecture & Hot Oil Steam Treatment",
              category: "Beard Care",
              price: 899,
              originalPrice: 1200,
              time: "35 mins",
              image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
              desc: "Warm steam opening of pores, hot jojoba oil massage into beard roots, and razor sharp symmetry."
            }
          ]
        },
        {
          id: "man_company_lounge",
          name: "The Man Company Grooming Lounge",
          brandTag: "Organic Essentials",
          tagline: "Ayurvedic Beard Spa, Vitamin C Glow & Head Massages",
          rating: "4.86 ★ (2,600+ reviews)",
          location: "Church Street",
          distance: "1.8 km away",
          timings: "10:00 AM - 09:00 PM",
          image: "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "100% Toxin-Free Natural Essential Oils",
            "Personalized Skin Tone Analysis",
            "Deep Beard Hydration Station"
          ],
          services: [
            {
              id: "tmc_beard_spa",
              title: "Moroccan Argan Beard Spa & Softening Therapy",
              category: "Beard Care",
              price: 799,
              originalPrice: 1100,
              time: "35 mins",
              image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
              desc: "Deep cleansing of beard dandruff, argan butter wrap, and wooden comb alignment."
            },
            {
              id: "tmc_coffee_facial",
              title: "Vitamin C & Arabica Coffee Skin Polish Facial",
              category: "Face Care",
              price: 1199,
              originalPrice: 1600,
              time: "50 mins",
              image: "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=500&q=80",
              desc: "Fresh coffee bean scrub to de-tan skin and fade sun spots."
            }
          ]
        },
        {
          id: "jawed_habib_men",
          name: "Jawed Habib Men's Signature",
          brandTag: "Classic Trendsetter",
          tagline: "Speed Grooming, Ammonia-Free Beard Color & Blackhead Detox",
          rating: "4.83 ★ (3,100+ reviews)",
          location: "Sector 3, HSR Layout",
          distance: "0.5 km away",
          timings: "09:00 AM - 09:30 PM",
          image: "https://images.unsplash.com/photo-1534778356534-d3d45b6df1da?auto=format&fit=crop&w=700&q=80",
          highlights: [
            "Fast 20-min Executive Turnaround",
            "Affordable Luxury Grooming",
            "Ammonia-Free Organic Hair Colors"
          ],
          services: [
            {
              id: "jh_classic_cut",
              title: "Classic Executive Haircut + Beard Trim Combo",
              category: "Hair & Beard",
              price: 499,
              originalPrice: 699,
              time: "30 mins",
              image: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
              desc: "Fast professional haircut with hot foam neck razor cleanup and beard trim."
            },
            {
              id: "jh_beard_color",
              title: "Ammonia-Free Beard & Sideburns Grey Coverage",
              category: "Hair Color",
              price: 899,
              originalPrice: 1200,
              time: "30 mins",
              image: "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
              desc: "Gentle natural black/dark brown tint that leaves zero skin stains."
            }
          ]
        }
      ]
    },

    {
      id: "sugu_help",
      name: "Sugu Help",
      iconFile: "sugu_help.png",
      tagline: "24/7 Priority Support, Warranty Claims & Concierge",
      rating: "4.98 (99% Resolution)",
      startingPrice: "Free",
      subcategories: [
        {
          id: "help_desk",
          name: "Support & Guarantees",
          items: [
            {
              id: "concierge_booking",
              title: "Sugu VIP Concierge Booking & Assistance",
              rating: "5.0",
              reviews: "80K+",
              price: 0,
              originalPrice: 0,
              time: "Instant",
              badge: "24x7 Free",
              image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
              features: [
                "Dedicated relationship manager assigned in 60s",
                "Free schedule rescheduling or technician reassignment",
                "Full warranty claim support with 24-hr resolution",
                "Direct escalation to city operations lead"
              ]
            }
          ]
        }
      ]
    }
  ],

  // Bidding Demo Jobs & Quotes for End-User Portal
  biddingDemo: {
    activeJobs: [
      {
        id: "JOB-7821",
        title: "Complete 3BHK Wall Painting & Waterproofing Revamp",
        category: "Home Painting & Upgrade",
        icon: "painting_upgrade.png",
        postedDate: "Yesterday, 3:15 PM",
        budgetRange: "₹22,000 - ₹30,000",
        urgency: "Starts in 3 Days",
        location: "HSR Layout, Bengaluru",
        description: "Need full 3BHK interior painting (approx 1,450 sqft carpet). Wall sanding, primer coat, 2 coats of Asian Paints Royale Luxury Emulsion, plus 1 accent feature wall in master bedroom. Require waterproof coating on north-facing balcony wall.",
        photos: [
          "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=400&q=80",
          "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=400&q=80"
        ],
        status: "Receiving Bids",
        bidsCount: 3,
        bids: [
          {
            id: "BID-101",
            bidderName: "Apex Decor & Craft Coatings",
            contractor: "Vikram Sharma (Asian Paints Master Craftsman)",
            rating: "4.92",
            jobsDone: 340,
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
            bidAmount: 23500,
            timeline: "4 Working Days",
            included: "Royale Luxury paint + Dr. Fixit Damp-proof waterproof coating + free mechanized dustless sanding + 3-year warranty certificate.",
            verified: true,
            isRecommended: true
          },
          {
            id: "BID-102",
            bidderName: "Royal Brush Home Solutions",
            contractor: "Arun Das",
            rating: "4.81",
            jobsDone: 195,
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80",
            bidAmount: 21800,
            timeline: "5 Working Days",
            included: "Full 2 coats Royale paint + putty touchups + floor masking & deep cleaning upon handover.",
            verified: true,
            isRecommended: false
          },
          {
            id: "BID-103",
            bidderName: "Shree Colors & Interior Works",
            contractor: "K. R. Murthy",
            rating: "4.78",
            jobsDone: 112,
            avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80",
            bidAmount: 25000,
            timeline: "3 Working Days",
            included: "Express 5-painter crew with mechanized rollers + Berger Luxury PU finish + 2 accent designs.",
            verified: true,
            isRecommended: false
          }
        ]
      },
      {
        id: "JOB-7835",
        title: "Modular Wardrobe & Storage Loft Custom Carpentry",
        category: "Carpentry",
        icon: "carpentry.png",
        postedDate: "2 days ago",
        budgetRange: "₹35,000 - ₹50,000",
        urgency: "Flexible (within 2 weeks)",
        location: "Koramangala, Bengaluru",
        description: "Custom floor-to-ceiling 3-door sliding wardrobe (8ft x 7ft) with internal organizers, soft-close drawers, and high-gloss laminate finish. Marine grade ply required.",
        photos: [
          "https://images.unsplash.com/photo-1558997519-83ea9252def8?auto=format&fit=crop&w=400&q=80"
        ],
        status: "Receiving Bids",
        bidsCount: 2,
        bids: [
          {
            id: "BID-201",
            bidderName: "TimberCraft Woodworks",
            contractor: "Suresh Mistri",
            rating: "4.94",
            jobsDone: 280,
            avatar: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80",
            bidAmount: 38500,
            timeline: "7 Days",
            included: "Century 710 BWP plywood + Hettich sliding channels + 1mm Merino high-gloss laminate.",
            verified: true,
            isRecommended: true
          },
          {
            id: "BID-202",
            bidderName: "Modern Living Furniture Lab",
            contractor: "Devendra Patel",
            rating: "4.86",
            jobsDone: 140,
            avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=150&q=80",
            bidAmount: 42000,
            timeline: "6 Days",
            included: "Greenply Gold marine ply + Ebco soft-close channels + 10-year anti-termite guarantee.",
            verified: true,
            isRecommended: false
          }
        ]
      }
    ],
    popularTemplates: [
      {
        id: "TPL-PAINT",
        title: "Full 3BHK Interior Painting + Waterproofing",
        category: "Home Painting & Upgrade",
        categoryId: "painting_upgrade",
        icon: "painting_upgrade.png",
        budgetRange: "₹22,000 - ₹30,000",
        urgency: "Within 1 Week",
        avgQuotes: "4-6 Quotes in 30 mins",
        description: "Complete interior painting for 3BHK (approx 1,450 sqft). Wall sanding, primer coat, 2 coats of Asian Paints Royale Luxury Emulsion, and damp waterproofing on balcony walls."
      },
      {
        id: "TPL-WARD",
        title: "Floor-to-Ceiling Sliding Wardrobe & Lofts",
        category: "Carpentry",
        categoryId: "carpentry",
        icon: "carpentry.png",
        budgetRange: "₹35,000 - ₹50,000",
        urgency: "Flexible (within 2 weeks)",
        avgQuotes: "3-5 Quotes in 45 mins",
        description: "Custom 3-door sliding wardrobe (8ft x 7ft) with internal organizers, soft-close hydraulic drawers, and high-gloss 1mm laminate using Century 710 BWP marine plywood."
      },
      {
        id: "TPL-KITCHEN",
        title: "Complete Modular Kitchen Makeover",
        category: "Home Renovation",
        categoryId: "home_renovation",
        icon: "home_renovation.png",
        budgetRange: "₹45,000 - ₹80,000",
        urgency: "Within 2 Weeks",
        avgQuotes: "4 Quotes in 1 hour",
        description: "L-shaped modular kitchen overhaul with boiling waterproof plywood, tandem drawers, soft-close Hafele hinges, and black galaxy granite counter replacement."
      },
      {
        id: "TPL-SEPTIC",
        title: "Heavy Vacuum Septic Pumping & Desilting",
        category: "Septic Tank Cleaning",
        categoryId: "septic_tank",
        icon: "septic_tank.png",
        budgetRange: "₹3,000 - ₹4,500",
        urgency: "Immediate (24-48 Hours)",
        avgQuotes: "5 Quotes in 20 mins",
        description: "Complete 4000L septic sludge evacuation via motorized vacuum truck, high-pressure pipeline flushing, and odor neutralizing enzyme treatment."
      },
      {
        id: "TPL-WIRING",
        title: "Concealed House Rewiring & MCB Upgrade",
        category: "Electrical",
        categoryId: "electrical",
        icon: "electrical.png",
        budgetRange: "₹12,000 - ₹20,000",
        urgency: "Within 1 Week",
        avgQuotes: "3 Quotes in 30 mins",
        description: "Replacing old wiring with Polycab FR insulated fire-retardant copper wires, new 8-way MCB distribution board, and earthing pit check."
      },
      {
        id: "TPL-BATH",
        title: "Bathroom Waterproofing & Diverter Fitting",
        category: "Plumbing",
        categoryId: "plumbing",
        icon: "plumbing.png",
        budgetRange: "₹15,000 - ₹25,000",
        urgency: "Immediate (24-48 Hours)",
        avgQuotes: "4 Quotes in 30 mins",
        description: "Fixing recurring floor seepage, chemical grouting of tile joints, wall mixer to concealed diverter conversion with branded brass fittings."
      }
    ]
  }
};
