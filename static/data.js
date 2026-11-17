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
        title: "Milestone Protection & Completion",
        desc: "Funds are safely protected with Sugu. Payment is released stage-by-stage only when you sign off on milestones.",
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
      quote: "We got 4 contractor quotes in 2 hours and saved ₹42,000 on our interior revamp! Milestone payment protection gave us total peace of mind.",
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
      id: "37",
      dbId: "37",
      name: "Beauty",
      iconFile: "womens_salon_spa.png",
      tagline: "Salon at Home or Book Top Luxury Parlours",
      rating: "4.91 (4.2M Reviews)",
      startingPrice: "₹249",
      isBeautyHub: true,
      subcategories: []
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

window.SUGU_DATA = SUGU_DATA;
