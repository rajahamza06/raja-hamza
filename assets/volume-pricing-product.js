// Optional separate JS if your theme concatenates assets; section also includes inline JS.
(function() {
  var containers = document.querySelectorAll('[id^="vp-"][data-tiers]');
  containers.forEach(function(container){
    // Skip if inline script already initialized by checking a flag
    if (container.__vpInit) return;
    container.__vpInit = true;

    function parseJSONAttribute(el, attr) {
      try { return JSON.parse(el.getAttribute(attr)); } catch(e) { return []; }
    }

    function formatMoney(cents) {
      var symbol = container.getAttribute('data-currency-symbol') || '$';
      var value = (cents / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      return symbol + value;
    }

    var tiers = parseJSONAttribute(container, 'data-tiers');
    var maxQty = parseInt(container.getAttribute('data-max-qty'), 10) || 5;
    var basePriceCents = parseInt(container.getAttribute('data-base-price-cents'), 10) || 0;
    var discountPriceEl = container.querySelector('[data-vp-discount-price]');
    var progressBarEl = container.querySelector('.vp-progress__bar');
    var qtyInput = container.querySelector('.vp-qty__input');
    var decBtn = container.querySelector('[data-action="decrement"]');
    var incBtn = container.querySelector('[data-action="increment"]');
    var atcBtn = container.querySelector('[data-vp-atc]');

    function getTierPriceCents(quantity) {
      var price = null;
      for (var i = 0; i < tiers.length; i++) {
        if (tiers[i].qty === quantity) { price = tiers[i].price_cents; break; }
      }
      if (price === null) {
        var highest = tiers[tiers.length - 1];
        price = highest ? highest.price_cents : basePriceCents;
      }
      return price || basePriceCents;
    }

    function clamp(min, val, max) { return Math.max(min, Math.min(val, max)); }

    function updateUI() {
      var q = parseInt(qtyInput.value, 10) || 1;
      q = clamp(1, q, 9999);
      qtyInput.value = q;

      var unitPriceCents = getTierPriceCents(q);
      if (discountPriceEl) {
        discountPriceEl.textContent = formatMoney(unitPriceCents) + '/each';
      }

      if (progressBarEl) {
        var pct = Math.max(0, Math.min(100, (q / maxQty) * 100));
        progressBarEl.style.width = pct + '%';
      }

      if (atcBtn) {
        atcBtn.textContent = 'Add to cart';
      }
    }

    if (decBtn) decBtn.addEventListener('click', function(){ qtyInput.value = Math.max(1, (parseInt(qtyInput.value,10)||1) - 1); updateUI(); });
    if (incBtn) incBtn.addEventListener('click', function(){ qtyInput.value = (parseInt(qtyInput.value,10)||1) + 1; updateUI(); });
    qtyInput.addEventListener('change', updateUI);

    updateUI();
  });
})();