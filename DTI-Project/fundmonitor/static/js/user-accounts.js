/**
 * User Accounts Management JavaScript
 * Consolidates all functionality for user account creation, editing, and management
 * With custom styled confirmation modals for dark/light theme
 */

// ════════════════════════════════════════════════════════════════════════════
// Configuration
// ════════════════════════════════════════════════════════════════════════════

window.userAccountManager = {
  deleteButtonClass: 'delete-user-btn',
  toggleStatusClass: 'toggle-status-btn',
  modalOpen: false, // Prevent multiple modals from opening simultaneously
};

// ════════════════════════════════════════════════════════════════════════════
// Custom Confirmation Modal
// ════════════════════════════════════════════════════════════════════════════

/**
 * Show a custom styled confirmation dialog
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message/body
 * @param {string} confirmText - Confirm button text (default: "Confirm")
 * @param {string} cancelText - Cancel button text (default: "Cancel")
 * @param {string} type - Icon type: 'warning', 'danger', 'info', 'success' (default: 'warning')
 * @returns {Promise<boolean>} - Resolves true if confirmed, false if cancelled
 */
window.showConfirmation = function(title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'warning') {
  return new Promise((resolve) => {
    // Prevent multiple modals from opening at the same time
    if (window.userAccountManager.modalOpen) {
      resolve(false);
      return;
    }
    
    window.userAccountManager.modalOpen = true;

    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'confirmation-modal-backdrop';

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'confirmation-modal';

    // Create header with icon
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

    // Create body
    const body = document.createElement('div');
    body.className = 'confirmation-modal-body';
    body.textContent = message;

    // Create footer with buttons
    const footer = document.createElement('div');
    footer.className = 'confirmation-modal-footer';

    // Cancel button
    const cancelBtn = document.createElement('button');
    cancelBtn.type = 'button';
    cancelBtn.className = 'confirmation-modal-button cancel';
    cancelBtn.innerHTML = `<i class="bi bi-x-lg"></i> ${cancelText}`;
    cancelBtn.addEventListener('click', () => closeModal(false));

    // Confirm button
    const confirmBtn = document.createElement('button');
    confirmBtn.type = 'button';
    confirmBtn.className = `confirmation-modal-button confirm ${type === 'danger' ? 'danger' : ''}`;
    confirmBtn.innerHTML = `<i class="bi ${getButtonIcon(type)}"></i> ${confirmText}`;
    confirmBtn.addEventListener('click', () => closeModal(true));

    footer.appendChild(cancelBtn);
    footer.appendChild(confirmBtn);

    // Assemble modal
    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    backdrop.appendChild(modal);

    // Add to DOM
    document.body.appendChild(backdrop);

    // Set focus to confirm button
    confirmBtn.focus();

    // Handle keyboard
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        closeModal(false);
      } else if (e.key === 'Enter') {
        closeModal(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    // Close modal function
    function closeModal(confirmed) {
      backdrop.removeEventListener('click', backdropClick);
      document.removeEventListener('keydown', handleKeyDown);
      backdrop.remove();
      window.userAccountManager.modalOpen = false;
      resolve(confirmed);
    }

    // Close on backdrop click
    const backdropClick = (e) => {
      if (e.target === backdrop) {
        closeModal(false);
      }
    };
    backdrop.addEventListener('click', backdropClick);
  });
};

/**
 * Get icon HTML for confirmation type
 */
function getIconHTML(type) {
  const icons = {
    'warning': '<i class="bi bi-exclamation-triangle-fill"></i>',
    'danger': '<i class="bi bi-exclamation-circle-fill"></i>',
    'info': '<i class="bi bi-info-circle-fill"></i>',
    'success': '<i class="bi bi-check-circle-fill"></i>'
  };
  return icons[type] || icons['warning'];
}

/**
 * Get button icon for confirmation type
 */
function getButtonIcon(type) {
  const icons = {
    'warning': 'bi-check-lg',
    'danger': 'bi-trash',
    'info': 'bi-check-lg',
    'success': 'bi-check-lg'
  };
  return icons[type] || 'bi-check-lg';
}

// ════════════════════════════════════════════════════════════════════════════
// Event Handlers
// ════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
  // Handle permission level radio buttons
  const permissionRadios = document.querySelectorAll('input[name="permission-level"]');
  const isStaffCheckbox = document.getElementById('id_is_staff');
  const isSuperuserCheckbox = document.getElementById('id_is_superuser');

  // Only initialize if permission radios exist (on create/edit forms)
  if (permissionRadios.length > 0 && isStaffCheckbox && isSuperuserCheckbox) {
    // Set initial state
    updatePermissionCheckboxes();

    // Update on radio change
    permissionRadios.forEach(radio => {
      radio.addEventListener('change', updatePermissionCheckboxes);
    });

    function updatePermissionCheckboxes() {
      const selected = document.querySelector('input[name="permission-level"]:checked')?.value;
      
      if (selected === 'regular') {
        isStaffCheckbox.checked = false;
        isSuperuserCheckbox.checked = false;
      } else if (selected === 'staff') {
        isStaffCheckbox.checked = true;
        isSuperuserCheckbox.checked = false;
      } else if (selected === 'superuser') {
        isStaffCheckbox.checked = true;
        isSuperuserCheckbox.checked = true;
      }
    }
  }
});

// ────────────────────────────────────────────────────────────────────────────
// UNIFIED CLICK HANDLER FOR ALL CONFIRMATION MODALS
// ────────────────────────────────────────────────────────────────────────────

document.addEventListener('click', async function(e) {
  // Get the clicked element
  const clickedElement = e.target;
  
  // Handle Reset Password Button
  if (clickedElement.closest && clickedElement.closest('.user-accounts-action-reset')) {
    const resetBtn = clickedElement.closest('.user-accounts-action-reset');
    if (resetBtn && resetBtn.dataset.resetUrl) {
      e.preventDefault();
      e.stopPropagation();
      const confirmed = await showConfirmation(
        'Reset Password',
        'Are you sure you want to reset this user\'s password? They will receive a new temporary password (TempPass123!).',
        'Reset Password',
        'Cancel',
        'warning'
      );
      if (confirmed) {
        window.location = resetBtn.dataset.resetUrl;
      }
    }
    return;
  }
  
  // Get button and form
  const button = clickedElement.closest && clickedElement.closest('button[type="submit"]');
  if (!button) return;
  
  const form = button.closest('form');
  if (!form) return;
  
  const action = form.getAttribute('action') || '';
  
  // Handle Toggle Status Button
  if (action.includes('toggle_status') || action.includes('toggle-status')) {
    e.preventDefault();
    e.stopPropagation();
    
    const icon = button.querySelector('i');
    const isCurrentlyActive = icon && icon.classList.contains('bi-lock');
    
    const confirmed = await showConfirmation(
      isCurrentlyActive ? 'Disable Account' : 'Enable Account',
      isCurrentlyActive 
        ? 'Are you sure you want to disable this user account? They will not be able to log in.'
        : 'Are you sure you want to enable this user account?',
      isCurrentlyActive ? 'Disable Account' : 'Enable Account',
      'Cancel',
      'warning'
    );
    
    if (confirmed) {
      form.submit();
    }
    return;
  }
  
  // Handle Delete Account Button
  if (action.includes('delete') && (button.classList.contains('action-delete') || button.classList.contains('delete-user-btn'))) {
    e.preventDefault();
    e.stopPropagation();
    
    const confirmed = await showConfirmation(
      'Delete User Account',
      'Are you sure you want to permanently delete this user account? This action cannot be undone.',
      'Delete Account',
      'Cancel',
      'danger'
    );
    
    if (confirmed) {
      form.submit();
    }
    return;
  }
}, false); // Use capture phase: false (bubble phase)
