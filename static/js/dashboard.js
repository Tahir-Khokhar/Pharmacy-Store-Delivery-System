/**
 * PharmaCare Management Dashboard Interactions
 */
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alerts after 5s if desired
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // Table row quick filter if search box present
  const tableSearch = document.getElementById('tableSearchInput');
  if (tableSearch) {
    tableSearch.addEventListener('input', function() {
      const q = this.value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }
});
