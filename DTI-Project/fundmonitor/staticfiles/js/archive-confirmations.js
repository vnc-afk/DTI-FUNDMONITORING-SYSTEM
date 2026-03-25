/**
 * Archive Confirmations - Modal dialogs for archive operations
 * Reuses the custom confirmation modal from user-accounts.js
 */

// Show custom confirmation modal (same as user-accounts.js)
window.showConfirmation = function(title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'warning') {
  return new Promise((resolve) => {
    const backdrop = document.createElement('div');
    backdrop.className = 'confirmation-modal-backdrop';

    const modal = document.createElement('div');
    modal.className = 'confirmation-modal';

    const header = document.createElement('div');
    header.className = 'confirmation-modal-header';
    
    const icon = document.createElement('div');
    icon.className = `confirmation-modal-icon ${type}`;
    icon.innerHTML = getIconHTML(type);
    
    const titleElement = document.createElement('h3');
    titleElement.className = 'confirmation-modal-title';
    titleElement.textContent = title;
    
    header.appendChild(icon);
    header.appendChild(titleElement);

    const body = document.createElement('div');
    body.className = 'confirmation-modal-body';
    body.textContent = message;

    const footer = document.createElement('div');
    footer.className = 'confirmation-modal-footer';

    const cancelBtn = document.createElement('button');
    cancelBtn.type = 'button';
    cancelBtn.className = 'confirmation-modal-button cancel';
    cancelBtn.innerHTML = `<i class="bi bi-x-lg"></i> ${cancelText}`;
    cancelBtn.addEventListener('click', () => closeModal(false));

    const confirmBtn = document.createElement('button');
    confirmBtn.type = 'button';
    confirmBtn.className = `confirmation-modal-button confirm ${type === 'danger' ? 'danger' : ''}`;
    confirmBtn.innerHTML = `<i class="bi ${getButtonIcon(type)}"></i> ${confirmText}`;
    confirmBtn.addEventListener('click', () => closeModal(true));

    // Only add cancel button if cancelText is provided and not empty
    if (cancelText && cancelText.trim() !== '') {
      footer.appendChild(cancelBtn);
    }
    footer.appendChild(confirmBtn);

    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    backdrop.appendChild(modal);

    document.body.appendChild(backdrop);
    confirmBtn.focus();

    const handleKeyDown = (e) => {
      // Only allow Escape to close if there's a cancel button
      if (e.key === 'Escape' && cancelText && cancelText.trim() !== '') {
        closeModal(false);
      } else if (e.key === 'Enter') {
        closeModal(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    function closeModal(confirmed) {
      backdrop.removeEventListener('click', backdropClick);
      document.removeEventListener('keydown', handleKeyDown);
      backdrop.remove();
      resolve(confirmed);
    }

    const backdropClick = (e) => {
      // Only allow backdrop click to close if there's a cancel button
      if (e.target === backdrop && cancelText && cancelText.trim() !== '') {
        closeModal(false);
      }
    };
    backdrop.addEventListener('click', backdropClick);
  });
};

function getIconHTML(type) {
  const icons = {
    'warning': '<i class="bi bi-exclamation-triangle-fill"></i>',
    'danger': '<i class="bi bi-exclamation-circle-fill"></i>',
    'info': '<i class="bi bi-info-circle-fill"></i>',
    'success': '<i class="bi bi-check-circle-fill"></i>'
  };
  return icons[type] || icons['warning'];
}

function getButtonIcon(type) {
  const icons = {
    'warning': 'bi-check-lg',
    'danger': 'bi-check-lg',
    'info': 'bi-check-lg',
    'success': 'bi-check-lg'
  };
  return icons[type] || 'bi-check-lg';
}

// ════════════════════════════════════════════════════════════════════════════
// Archive-Specific Event Handlers
// ════════════════════════════════════════════════════════════════════════════

// Wait for DOM to be ready
function initRestoreHandlers() {
  // Handle restore button clicks with event delegation
  document.addEventListener('click', async function(e) {
    const button = e.target.closest('.archived-act-restore');
    
    if (!button) return;
    
    const form = button.closest('form');
    if (!form) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    // Determine message based on page context
    const pageTitle = document.querySelector('h1')?.textContent || 'Archive';
    const isStatements = pageTitle.includes('Statements');
    
    const title = isStatements ? 'Restore Bank Statement' : 'Restore Transaction';
    const message = isStatements 
      ? 'Are you sure you want to restore this bank statement to your main dashboard?'
      : 'Are you sure you want to restore this transaction to your main dashboard?';
    
    const confirmed = await showConfirmation(
      title,
      message,
      'Restore',
      'Cancel',
      'warning'
    );
    
    if (confirmed) {
      form.submit();
    }
  }, true); // Use capture phase to ensure we catch the click before stopPropagation
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initRestoreHandlers);
} else {
  initRestoreHandlers();
}
