/**
 * RoyalShop — Main JavaScript
 * ============================
 * Handles:
 *  - Add to cart (AJAX)
 *  - Update cart quantity (AJAX)
 *  - Remove from cart (AJAX)
 *  - Quantity +/- buttons
 *  - Toast notifications
 *  - Cart count update in navbar
 */

'use strict';

// ── CSRF token helper ──────────────────────────────
function getCsrf() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.trim().split('=')[1] : '';
}

// ── Toast notification ─────────────────────────────
function showToast(message, type = 'success') {
  const toastEl = document.getElementById('cartToast');
  const msgEl   = document.getElementById('toastMessage');
  if (!toastEl || !msgEl) return;

  const icons = { success: 'bi-bag-check-fill', danger: 'bi-exclamation-triangle', warning: 'bi-exclamation-circle' };
  msgEl.innerHTML = `<i class="bi ${icons[type] || icons.success} me-2 gold-text"></i>${message}`;
  toastEl.classList.remove('bg-danger', 'bg-warning');
  if (type === 'danger')  toastEl.classList.add('bg-danger');
  if (type === 'warning') toastEl.classList.add('bg-warning');

  const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3000 });
  bsToast.show();
}

// ── Update cart count badge in navbar ─────────────
function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(el => {
    if (count > 0) { el.textContent = count; el.style.display = 'flex'; }
    else            { el.style.display = 'none'; }
  });
  // Add badge if it doesn't exist
  if (count > 0) {
    document.querySelectorAll('.nav-icon-btn').forEach(btn => {
      if (!btn.querySelector('.cart-badge')) {
        const badge = document.createElement('span');
        badge.className = 'cart-badge';
        badge.textContent = count;
        btn.appendChild(badge);
      }
    });
  }
}

// ── Add to Cart ────────────────────────────────────
function addToCart(productId, quantity = 1) {
  quantity = parseInt(quantity, 10);
  if (!quantity || quantity < 1) quantity = 1;

  fetch('/orders/cart/add/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body:    JSON.stringify({ product_id: productId, quantity }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(data.message || 'Added to cart!', 'success');
      updateCartBadge(data.cart_count);
      // Animate the cart icon
      document.querySelectorAll('.nav-icon-btn').forEach(btn => {
        btn.style.transform = 'scale(1.3)';
        setTimeout(() => btn.style.transform = '', 300);
      });
    } else {
      showToast(data.message || 'Could not add item.', 'danger');
    }
  })
  .catch(() => showToast('Network error. Please try again.', 'danger'));
}

// ── Update Cart Quantity (cart page) ───────────────
function updateCartQty(productId, delta) {
  const input = document.getElementById(`cartqty-${productId}`);
  if (!input) return;
  const newQty = parseInt(input.value, 10) + delta;
  if (newQty < 1) { removeFromCart(productId); return; }
  input.value = newQty;
  sendCartUpdate(productId, newQty);
}

function updateCartQtyDirect(productId, value) {
  const qty = parseInt(value, 10);
  if (!qty || qty < 1) { removeFromCart(productId); return; }
  sendCartUpdate(productId, qty);
}

function sendCartUpdate(productId, quantity) {
  fetch('/orders/cart/update/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body:    JSON.stringify({ product_id: productId, quantity }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateCartBadge(data.cart_count);
      // Update totals on cart page
      updateCartSummary(data);
      // Update line subtotal
      const sub = document.getElementById(`subtotal-${productId}`);
      if (sub && data.subtotal !== undefined) {
        // Recalculate line from updated totals (approx)
      }
    }
  })
  .catch(() => {});
}

function updateCartSummary(data) {
  const subtotalEl  = document.getElementById('summary-subtotal');
  const shippingEl  = document.getElementById('summary-shipping');
  const totalEl     = document.getElementById('summary-total');
  if (subtotalEl) subtotalEl.textContent = `₹${data.subtotal}`;
  if (shippingEl) shippingEl.innerHTML   = data.shipping === 0 ? '<span class="text-success">FREE</span>' : `₹${data.shipping}`;
  if (totalEl)    totalEl.textContent    = `₹${data.total}`;
}

// ── Remove from Cart ───────────────────────────────
function removeFromCart(productId) {
  fetch('/orders/cart/remove/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body:    JSON.stringify({ product_id: productId }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const row = document.getElementById(`cart-row-${productId}`);
      if (row) {
        row.style.transition = 'all .3s ease';
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        setTimeout(() => { row.remove(); checkEmptyCart(); }, 300);
      }
      updateCartBadge(data.cart_count);
      updateCartSummary(data);
      showToast('Item removed from cart.', 'warning');
    }
  })
  .catch(() => {});
}

function checkEmptyCart() {
  const rows = document.querySelectorAll('.cart-row');
  if (rows.length === 0) {
    // Reload to show empty state
    setTimeout(() => location.reload(), 400);
  }
}

// ── Quantity +/- Buttons (product cards) ──────────
document.addEventListener('click', function (e) {
  // + button
  if (e.target.classList.contains('qty-plus')) {
    const pid = e.target.dataset.pid;
    const max = parseInt(e.target.dataset.max || 99, 10);
    const input = document.getElementById(`qty-${pid}`);
    if (input) { const v = Math.min(parseInt(input.value,10) + 1, max); input.value = v; }
  }
  // - button
  if (e.target.classList.contains('qty-minus')) {
    const pid = e.target.dataset.pid;
    const input = document.getElementById(`qty-${pid}`);
    if (input) { const v = Math.max(parseInt(input.value,10) - 1, 1); input.value = v; }
  }
});

// ── Auto-dismiss alerts after 4s ──────────────────
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    document.querySelectorAll('.royal-alert').forEach(el => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    });
  }, 4500);

  // Smooth scroll to top button (optional)
  window.addEventListener('scroll', function () {
    const fab = document.getElementById('backToTop');
    if (fab) fab.style.display = window.scrollY > 400 ? 'flex' : 'none';
  });
});
