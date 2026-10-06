/**
 * PharmaCare Global JavaScript Engine
 */

// Toast notification helper
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const bgClass = type === 'error' ? 'bg-danger' : (type === 'warning' ? 'bg-warning text-dark' : 'bg-teal');
  const icon = type === 'error' ? 'bi-exclamation-triangle-fill' : (type === 'warning' ? 'bi-exclamation-circle-fill' : 'bi-check-circle-fill');

  const toastId = 'toast-' + Date.now();
  const html = `
    <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 shadow-lg rounded-3 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center">
          <i class="bi ${icon} me-2 fs-5"></i>
          <div>${message}</div>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', html);
  const toastEl = document.getElementById(toastId);
  const bsToast = new bootstrap.Toast(toastEl, { delay: 4000 });
  bsToast.show();
  toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

document.addEventListener('DOMContentLoaded', () => {
  const csrfToken = window.CSRF_TOKEN || '';

  // 1. Quick Add to Cart
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const qtyInput = document.getElementById('productQuantity');
      const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

      const origText = this.innerHTML;
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

      const formData = new FormData();
      formData.append('product_id', productId);
      formData.append('quantity', quantity);

      fetch(window.CART_ADD_URL || '/cart/add/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        this.disabled = false;
        this.innerHTML = origText;

        if (data.success) {
          // Update cart badges in navbar
          document.querySelectorAll('.cart-count-badge').forEach(b => b.textContent = data.total_items);
          showToast(data.message, 'success');
        } else {
          showToast(data.message || 'Could not add to cart.', 'error');
        }
      })
      .catch(err => {
        this.disabled = false;
        this.innerHTML = origText;
        console.error(err);
        showToast('Network error adding product.', 'error');
      });
    });
  });

  // 2. Wishlist Toggle
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const icon = this.querySelector('i');

      const formData = new FormData();
      formData.append('product_id', productId);

      fetch(window.WISHLIST_TOGGLE_URL || '/wishlist/toggle/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (icon) {
            if (data.is_wishlisted) {
              icon.classList.remove('bi-heart', 'text-muted');
              icon.classList.add('bi-heart-fill', 'text-danger');
            } else {
              icon.classList.remove('bi-heart-fill', 'text-danger');
              icon.classList.add('bi-heart', 'text-muted');
            }
          }
          // If on wishlist page and item removed, remove column
          const col = document.getElementById(`wishlist-col-${productId}`);
          if (col && !data.is_wishlisted) {
            col.remove();
          }

          document.querySelectorAll('.wishlist-count-badge').forEach(b => b.textContent = data.wishlist_count);
          showToast(data.message, 'success');
        } else {
          showToast(data.message || 'Please log in to manage wishlist.', 'warning');
        }
      })
      .catch(err => console.error(err));
    });
  });
});
