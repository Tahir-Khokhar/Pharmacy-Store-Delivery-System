/**
 * PharmaCare Checkout Interactions
 */
document.addEventListener('DOMContentLoaded', () => {
  // Address selection highlight
  document.querySelectorAll('input[name="shipping_address"]').forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.address-card').forEach(card => {
        card.classList.remove('border-teal', 'bg-light');
      });
      const parentLabel = radio.closest('.address-card');
      if (parentLabel) parentLabel.classList.add('border-teal', 'bg-light');
    });
  });

  // Payment method selection highlight
  document.querySelectorAll('input[name="payment_method"]').forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.payment-card').forEach(card => {
        card.classList.remove('border-teal', 'bg-light');
      });
      const parentLabel = radio.closest('.payment-card');
      if (parentLabel) parentLabel.classList.add('border-teal', 'bg-light');
    });
  });

  // Form submit prevention of double clicks
  const form = document.getElementById('checkoutForm');
  const btn = document.getElementById('placeOrderBtn');
  if (form && btn) {
    form.addEventListener('submit', () => {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing Order...';
    });
  }
});
