/**
 * Universal Action Confirmation Handler
 * Handles delete, edit, mark, approve, and any other action type
 * Uses the same Promise-based confirmation dialog pattern as user-accounts.js
 */

/**
 * Action configuration templates with default messages and styles
 */
const ACTION_CONFIGS = {
  delete: {
    title: (name) => `Delete ${name}?`,
    message: (label) => `You are about to permanently delete: "${label}"`,
    confirmText: 'Delete',
    type: 'danger'
  },
  edit: {
    title: (name) => `Edit ${name}?`,
    message: (label) => `You're about to edit "${label}". Continue?`,
    confirmText: 'Edit',
    type: 'warning'
  },
  'mark-approved': {
    title: () => 'Mark as Approved?',
    message: (label) => `Mark "${label}" as approved?`,
    confirmText: 'Approve',
    type: 'success'
  },
  'mark-rejected': {
    title: () => 'Mark as Rejected?',
    message: (label) => `Mark "${label}" as rejected?`,
    confirmText: 'Reject',
    type: 'danger'
  },
  archive: {
    title: (name) => `Archive ${name}?`,
    message: (label) => `Archive "${label}"? You can restore it later.`,
    confirmText: 'Archive',
    type: 'warning'
  },
  restore: {
    title: (name) => `Restore ${name}?`,
    message: (label) => `Restore "${label}" to active status?`,
    confirmText: 'Restore',
    type: 'success'  },
  'mark-cleared': {
    title: () => 'Mark as Cleared?',
    message: (label) => `Mark "${label}" as cleared?`,
    confirmText: 'Mark Cleared',
    type: 'success'  }
};

/**
 * Show action confirmation and perform the action
 * @param {Object} options - Configuration options
 * @param {string} options.actionUrl - URL to POST the request to
 * @param {string} options.actionType - Type of action (delete, edit, mark-approved, etc.)
 * @param {string} options.actionName - Name of the entity being acted upon (e.g., 'Supplier')
 * @param {string} options.actionLabel - Label/name of the specific item (e.g., 'ABC Corporation')
 * @param {string} options.redirectUrl - URL to redirect to after successful action
 * @param {Object} options.customConfig - Optional custom configuration to override defaults
 * @param {Object} options.customBody - Optional custom request body (defaults to {})
 * @param {Function} options.onSuccess - Optional callback function after successful action
 * @returns {Promise<boolean>} - Resolves true if action completed, false if cancelled
 */
window.showActionConfirmation = async function(options = {}) {
  const {
    actionUrl,
    actionType = 'delete',
    actionName = 'Item',
    actionLabel = 'this item',
    redirectUrl = null,
    customConfig = {},
    customBody = {},
    onSuccess = null
  } = options;

  if (!actionUrl) {
    console.error('Action URL is required');
    alert('Action configuration error');
    return false;
  }

  // Get configuration for this action type
  let config = ACTION_CONFIGS[actionType] || ACTION_CONFIGS.delete;
  config = { ...config, ...customConfig };

  // Generate messages (handle both function and string formats)
  const title = typeof config.title === 'function' ? config.title(actionName) : config.title;
  const message = typeof config.message === 'function' ? config.message(actionLabel) : config.message;
  const confirmText = config.confirmText || 'Confirm';
  const type = config.type || 'warning';

  // Show confirmation dialog
  const confirmed = await window.showConfirmation(
    title,
    message,
    confirmText,
    'Cancel',
    type
  );

  if (!confirmed) return false;

  // Perform the action
  return performAction(actionUrl, actionType, redirectUrl, customBody, onSuccess);
};

/**
 * Perform the actual action request
 */
async function performAction(actionUrl, actionType, redirectUrl, customBody = {}, onSuccess = null) {
  try {
    const csrfToken = getCookie('csrftoken');

    const response = await fetch(actionUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(customBody || {}),
      redirect: 'follow'
    });

    // Handle various response types
    if (response.status === 204) {
      // No content - successful action
      const successMessage = getActionSuccessMessage(actionType);
      showActionAlert(successMessage, 'success');
      
      // Call custom callback if provided
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess({});
      }
      
      setTimeout(() => {
        if (redirectUrl) {
          window.location.href = redirectUrl;
        } else {
          location.reload();
        }
      }, 1200);
      return true;
    }

    if (response.ok) {
      const contentType = response.headers.get('content-type');
      let data = { success: true };

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      }

      if (data.success !== false) {
        const successMessage = getActionSuccessMessage(actionType);
        showActionAlert(successMessage, 'success');
        
        // Call custom callback if provided (for DOM updates like removing buttons)
        if (onSuccess && typeof onSuccess === 'function') {
          onSuccess(data);
        }
        
        // Redirect or reload after delay
        setTimeout(() => {
          if (redirectUrl) {
            window.location.href = redirectUrl;
          } else {
            location.reload();
          }
        }, 1200);
        return true;
      }
    }

    // Error response
    const errorMsg = response.statusText || 'Action failed';
    showActionAlert(errorMsg, 'error');
    return false;
  } catch (error) {
    console.error('Action request failed:', error);
    showActionAlert('Network error. Please try again.', 'error');
    return false;
  }
}

/**
 * Get success message for action type
 */
function getActionSuccessMessage(actionType) {
  const messages = {
    delete: 'Item deleted successfully',
    edit: 'Item updated successfully',
    'mark-approved': 'Item marked as approved',
    'mark-rejected': 'Item marked as rejected',
    'mark-cleared': 'Transaction marked as cleared',
    archive: 'Item archived successfully',
    restore: 'Item restored successfully'
  };
  return messages[actionType] || 'Action completed successfully';
}

/**
 * Show alert notification for action results
 * Uses confirmation-modal.css classes for styling
 */
function showActionAlert(message, type = 'info') {
  const iconMap = {
    'info': '<i class="bi bi-info-circle-fill"></i>',
    'success': '<i class="bi bi-check-circle-fill"></i>',
    'error': '<i class="bi bi-exclamation-circle-fill"></i>',
    'warning': '<i class="bi bi-exclamation-triangle-fill"></i>'
  };

  const alert = document.createElement('div');
  alert.className = `confirmation-modal-alert confirmation-modal-alert-${type}`;

  const icon = document.createElement('span');
  icon.className = 'confirmation-modal-alert-icon';
  icon.innerHTML = iconMap[type] || iconMap['info'];

  const content = document.createElement('span');
  content.className = 'confirmation-modal-alert-content';
  content.textContent = message;

  const closeBtn = document.createElement('button');
  closeBtn.className = 'confirmation-modal-alert-close';
  closeBtn.type = 'button';
  closeBtn.textContent = '×';
  closeBtn.addEventListener('click', () => alert.remove());

  alert.appendChild(icon);
  alert.appendChild(content);
  alert.appendChild(closeBtn);
  document.body.appendChild(alert);

  // Auto-remove after 4 seconds
  setTimeout(() => {
    if (alert.parentElement) alert.remove();
  }, 4000);
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
  let value = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) {
        value = decodeURIComponent(c.substring(name.length + 1));
      }
    });
  }
  return value;
}

/**
 * Initialize a single delegated click listener for action buttons.
 * This supports dynamic/AJAX-rendered content without rebinding listeners.
 */
function initializeConfirmActionDelegation() {
  if (window.__confirmActionDelegatedBound) return;

  document.addEventListener('click', async function(e) {
    const button = e.target.closest && e.target.closest('[data-confirm-action]');
    if (!button) return;

    e.preventDefault();

    const actionType = button.dataset.actionType || button.dataset.confirmAction;
    const actionUrl = button.dataset.actionUrl || button.form?.action;

    if (!actionUrl) {
      console.error('Action button missing data-action-url attribute', button);
      alert('Action URL is not configured.');
      return;
    }

    const customConfig = button.dataset.customConfig ? tryParseJSON(button.dataset.customConfig) : {};
    const customBody = button.dataset.customBody ? tryParseJSON(button.dataset.customBody) : {};

    // Support referencing a callback function by name
    let onSuccess = null;
    if (button.dataset.onSuccess && typeof window[button.dataset.onSuccess] === 'function') {
      onSuccess = function(data) {
        window[button.dataset.onSuccess](data, button);
      };
    }

    await window.showActionConfirmation({
      actionUrl: actionUrl,
      actionType: actionType || 'delete',
      actionName: button.dataset.actionName || 'Item',
      actionLabel: button.dataset.actionLabel || 'this item',
      redirectUrl: button.dataset.redirectUrl || null,
      customConfig: customConfig,
      customBody: customBody,
      onSuccess: onSuccess
    });
  });

  window.__confirmActionDelegatedBound = true;
}

initializeConfirmActionDelegation();

/**
 * Helper to safely parse JSON from data attributes
 */
function tryParseJSON(jsonString) {
  try {
    return JSON.parse(jsonString);
  } catch (e) {
    console.warn('Failed to parse JSON:', jsonString, e);
    return {};
  }
}
