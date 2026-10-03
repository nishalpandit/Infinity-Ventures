// Sugu - Urban Company Reactive Cart Store
(function() {
  const STORAGE_KEY = "sugu_cart_items";
  let cart = {};
  const listeners = [];

  function loadCart() {
    try {
      const data = localStorage.getItem(STORAGE_KEY) || localStorage.getItem("suggu_cart_items");
      if (data) {
        cart = JSON.parse(data) || {};
      }
    } catch(e) {
      cart = {};
    }
  }

  function saveCart() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    } catch(e) {}
    notifyListeners();
  }

  function notifyListeners() {
    listeners.forEach(fn => {
      try { fn(cart); } catch(err) { console.error(err); }
    });
  }

  function addItem(item) {
    const key = item.uniqueKey || `svc_${item.serviceId}_${item.packageName || 'std'}`;
    if (cart[key]) {
      cart[key].quantity += 1;
    } else {
      cart[key] = {
        key: key,
        serviceId: item.serviceId,
        title: item.title,
        packageName: item.packageName || 'Standard',
        price: parseFloat(item.price) || 0,
        originalPrice: parseFloat(item.originalPrice) || (parseFloat(item.price) * 1.25),
        vendorName: item.vendorName || "Verified Partner",
        vendorId: item.vendorId || null,
        quantity: 1,
        image: item.image || ""
      };
    }
    saveCart();
    return cart[key];
  }

  function updateQuantity(key, delta) {
    if (!cart[key]) return;
    cart[key].quantity += delta;
    if (cart[key].quantity <= 0) {
      delete cart[key];
    }
    saveCart();
  }

  function setQuantity(key, qty) {
    if (qty <= 0) {
      delete cart[key];
    } else if (cart[key]) {
      cart[key].quantity = qty;
    }
    saveCart();
  }

  function clearCart() {
    cart = {};
    saveCart();
  }

  function getCart() {
    return { ...cart };
  }

  function getCartSummary() {
    let count = 0;
    let subtotal = 0;
    let originalTotal = 0;

    Object.values(cart).forEach(item => {
      count += item.quantity;
      subtotal += item.price * item.quantity;
      originalTotal += item.originalPrice * item.quantity;
    });

    const savings = Math.max(0, originalTotal - subtotal);

    return {
      count,
      subtotal: Math.round(subtotal),
      originalTotal: Math.round(originalTotal),
      savings: Math.round(savings),
      items: Object.values(cart)
    };
  }

  function getItemQuantity(key) {
    return cart[key] ? cart[key].quantity : 0;
  }

  function getServiceTotalQuantity(serviceId) {
    let count = 0;
    Object.values(cart).forEach(item => {
      if (item.serviceId == serviceId) {
        count += item.quantity;
      }
    });
    return count;
  }

  function subscribe(fn) {
    listeners.push(fn);
    fn(cart); // Initial callback
    return () => {
      const idx = listeners.indexOf(fn);
      if (idx !== -1) listeners.splice(idx, 1);
    };
  }

  loadCart();

  window.SugguCart = window.SuguCart = {
    addItem,
    updateQuantity,
    setQuantity,
    clearCart,
    getCart,
    getCartSummary,
    getItemQuantity,
    getServiceTotalQuantity,
    subscribe
  };
})();
