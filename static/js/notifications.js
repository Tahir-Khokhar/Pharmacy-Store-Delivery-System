/**
 * PharmaCare Notifications Interactive Handler
 */
document.addEventListener('DOMContentLoaded', () => {
  const markReadButtons = document.querySelectorAll('.mark-read-btn');
  markReadButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const notifId = this.dataset.notifId;
      fetch(`/notifications/mark-read/${notifId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN,
          'Content-Type': 'application/json'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const item = document.getElementById(`notif-item-${notifId}`);
          if (item) {
            item.classList.remove('bg-light', 'border-start', 'border-4', 'border-teal');
            btn.replaceWith(document.createRange().createContextualFragment(
              '<span class="badge bg-light text-muted small"><i class="bi bi-check2"></i> Read</span>'
            ));
          }
        }
      })
      .catch(err => console.error(err));
    });
  });
});
