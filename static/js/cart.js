/**
 * PharmaCare Shopping Cart AJAX Interactions
 */
document.addEventListener('DOMContentLoaded', () => {
  const updateUrl = window.CART_UPDATE_URL || '/cart/update/';
  const removeUrl = window.CART_REMOVE_URL || '/cart/remove/';
  const csrfToken = window.CSRF_TOKEN || '';

  function postData(url, data) {
    const formData = new FormData();
    for (let key in data) {
      formData.append(key, data[key]);
    }
    return fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      body: formData,
    }).then(res => res.json());
  }

  function updateCartBadges(count) {
    document.querySelectorAll('.cart-count-badge').forEach(badge => {
      badge.textContent = count;
    });
  }

  function updateSummary(data) {
    const subtotalEl = document.getElementById('cartSummarySubtotal');
    const taxEl = document.getElementById('cartSummaryTax');
    const deliveryEl = document.getElementById('cartSummaryDelivery');
    const grandTotalEl = document.getElementById('cartSummaryGrandTotal');
    const rxWarning = document.getElementById('rxWarningCard');

    if (subtotalEl) subtotalEl.textContent = `$${data.subtotal}`;
    if (taxEl) taxEl.textContent = `$${data.tax_total}`;
    if (deliveryEl) {
      if (parseFloat(data.delivery_fee) === 0) {
        deliveryEl.innerHTML = '<span class="text-success fw-bold">FREE</span>';
      } else {
        deliveryEl.textContent = `$${data.delivery_fee}`;
      }
    }
    if (grandTotalEl) grandTotalEl.textContent = `$${data.grand_total}`;
    if (rxWarning) {
      if (data.has_prescription) {
        rxWarning.classList.remove('d-none');
      } else {
        rxWarning.classList.add('d-none');
      }
    }
    updateCartBadges(data.total_items);
  }

  // Stepper Buttons
  document.querySelectorAll('.cart-qty-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const row = this.closest('.cart-item-row');
      const itemId = row.dataset.itemId;
      const input = row.querySelector('.cart-qty-input');
      let currentVal = parseInt(input.value) || 1;
      const maxVal = parseInt(input.getAttribute('max')) || 99;
      const action = this.dataset.action;

      if (action === 'increase' && currentVal < maxVal) {
        currentVal += 1;
      } else if (action === 'decrease' && currentVal > 1) {
        currentVal -= 1;
      } else {
        return;
      }

      input.value = currentVal;
      sendQuantityUpdate(itemId, currentVal, row);
    });
  });

  // Direct Input Change
  document.querySelectorAll('.cart-qty-input').forEach(input => {
    input.addEventListener('change', function() {
      const row = this.closest('.cart-item-row');
      const itemId = row.dataset.itemId;
      let val = parseInt(this.value) || 1;
      const maxVal = parseInt(this.getAttribute('max')) || 99;
      if (val > maxVal) val = maxVal;
      if (val < 1) val = 1;
      this.value = val;
      sendQuantityUpdate(itemId, val, row);
    });
  });

  function sendQuantityUpdate(itemId, quantity, row) {
    postData(updateUrl, { item_id: itemId, quantity: quantity })
      .then(res => {
        if (res.success) {
          const subtotalEl = row.querySelector('.item-subtotal-display');
          if (subtotalEl) subtotalEl.textContent = `$${res.item_subtotal}`;
          updateSummary(res);
        } else {
          alert(res.message || 'Error updating item quantity');
        }
      })
      .catch(err => console.error(err));
  }

  // Remove Item
  document.querySelectorAll('.cart-remove-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const row = this.closest('.cart-item-row');
      const itemId = row.dataset.itemId;

      postData(removeUrl, { item_id: itemId })
        .then(res => {
          if (res.success) {
            row.style.opacity = '0';
            setTimeout(() => {
              row.remove();
              updateSummary(res);
              if (parseInt(res.total_items) === 0) {
                location.reload();
              }
            }, 300);
          } else {
            alert(res.message || 'Error removing item');
          }
        })
        .catch(err => console.error(err));
    });
  });
});
