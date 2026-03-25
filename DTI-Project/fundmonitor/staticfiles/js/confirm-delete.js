/**
 * Single Item Delete Confirmation
 * Modern modal-based confirmation dialog for deleting individual items
 */

class ConfirmDeleteDialog {
  constructor(options = {}) {
    this.itemName = options.itemName || 'item';
    this.itemLabel = options.itemLabel || '';
    this.deleteUrl = options.deleteUrl;
    this.csrfToken = this.getCookie('csrftoken');
    this.details = options.details || {};
    this.onSuccess = options.onSuccess || (() => location.reload());
    this.redirectUrl = options.redirectUrl;
  }

  show() {
    this.showConfirmationDialog();
  }

  showConfirmationDialog() {
    // Remove existing dialog if any
    const existingDialog = document.getElementById('confirmDeleteDialog');
    if (existingDialog) existingDialog.remove();

    // Add animation styles if not already present
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      @keyframes fadeIn {
        from {
          opacity: 0;
        }
        to {
          opacity: 1;
        }
      }
      .confirm-delete-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(2px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.2s ease-out;
      }
      .confirm-delete-dialog {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius, 12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        max-width: 500px;
        width: 90%;
        overflow: hidden;
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .confirm-delete-dialog-header {
        padding: 20px 24px;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.04));
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: flex-start;
        gap: 14px;
      }
      .confirm-delete-dialog-header-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.12);
        color: var(--danger, #ef4444);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1.3rem;
      }
      .confirm-delete-dialog-header-text h5 {
        margin: 0 0 6px 0;
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: -0.01em;
      }
      .confirm-delete-dialog-header-text p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-weight: 500;
      }
      .confirm-delete-dialog-body {
        padding: 24px;
        background: var(--bg-card);
        color: var(--text-primary);
      }
      .confirm-delete-dialog-body p {
        margin: 0 0 16px 0;
        font-size: 0.9rem;
        line-height: 1.6;
        color: var(--text-primary);
      }
      .confirm-delete-dialog-body strong {
        font-weight: 600;
        color: var(--danger, #ef4444);
      }
      .confirm-delete-warning {
        padding: 12px 14px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.15);
        border-left: 3px solid var(--danger, #ef4444);
        border-radius: var(--radius-sm, 8px);
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
      }
      .confirm-delete-warning-icon {
        color: var(--danger, #ef4444);
        font-size: 1.1rem;
        flex-shrink: 0;
      }
      .confirm-delete-warning-text {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
      }
      .confirm-delete-details {
        padding: 14px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm, 8px);
        margin-bottom: 16px;
      }
      .confirm-delete-details-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      .confirm-delete-details-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        padding: 6px 0;
        border-bottom: 1px solid var(--border);
      }
      .confirm-delete-details-item:last-child {
        border-bottom: none;
      }
      .confirm-delete-details-label {
        color: var(--text-secondary);
        font-weight: 500;
      }
      .confirm-delete-details-value {
        color: var(--text-primary);
        font-weight: 600;
        word-break: break-word;
        max-width: 60%;
        text-align: right;
      }
      .confirm-delete-dialog-footer {
        padding: 16px 24px;
        background: var(--bg-surface);
        border-top: 1px solid var(--border);
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }
      .confirm-delete-btn {
        padding: 9px 18px;
        border-radius: var(--radius-sm, 8px);
        border: none;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: var(--font-body, -apple-system, BlinkMacSystemFont, sans-serif);
      }
      .confirm-delete-btn-cancel {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-strong);
      }
      .confirm-delete-btn-cancel:hover {
        background: var(--bg-card);
        border-color: var(--accent);
        color: var(--accent);
      }
      .confirm-delete-btn-cancel:active {
        transform: scale(0.98);
      }
      .confirm-delete-btn-delete {
        background: var(--danger, #ef4444);
        color: white;
        border: 2px solid var(--danger, #ef4444);
      }
      .confirm-delete-btn-delete:hover {
        background: #f87171;
        border-color: #f87171;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
        transform: translateY(-1px);
      }
      .confirm-delete-btn-delete:active {
        transform: translateY(0);
      }
      .confirm-delete-btn-delete:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none !important;
      }
    `;
    if (!document.querySelector('style[data-confirm-delete-dialog]')) {
      style.setAttribute('data-confirm-delete-dialog', 'true');
      document.head.appendChild(style);
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'confirmDeleteDialog';
    overlay.className = 'confirm-delete-overlay';

    // Create dialog card
    const card = document.createElement('div');
    card.className = 'confirm-delete-dialog';

    // Header
    const header = document.createElement('div');
    header.className = 'confirm-delete-dialog-header';

    const icon = document.createElement('div');
    icon.className = 'confirm-delete-dialog-header-icon';
    icon.innerHTML = `
      <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
    `;

    const headerContent = document.createElement('div');
    headerContent.className = 'confirm-delete-dialog-header-text';
    headerContent.style.flex = '1';
    headerContent.innerHTML = `
      <h5>Confirm Deletion</h5>
      <p>This action cannot be undone</p>
    `;

    header.appendChild(icon);
    header.appendChild(headerContent);

    // Body
    const body = document.createElement('div');
    body.className = 'confirm-delete-dialog-body';

    let bodyHTML = `<p>You are about to delete:</p>`;

    if (this.itemLabel) {
      bodyHTML += `<p style="margin: 0 0 16px 0;"><strong>${this.itemLabel}</strong></p>`;
    }

    // Add details if provided
    if (Object.keys(this.details).length > 0) {
      bodyHTML += `
        <div class="confirm-delete-details">
          <div class="confirm-delete-details-title">Details</div>
      `;
      for (const [key, value] of Object.entries(this.details)) {
        bodyHTML += `
          <div class="confirm-delete-details-item">
            <span class="confirm-delete-details-label">${key}:</span>
            <span class="confirm-delete-details-value">${value}</span>
          </div>
        `;
      }
      bodyHTML += `</div>`;
    }

    bodyHTML += `
      <div class="confirm-delete-warning">
        <span class="confirm-delete-warning-icon"><i class="fa-solid fa-triangle-exclamation"></i></span>
        <span class="confirm-delete-warning-text">This action is permanent and cannot be reversed.</span>
      </div>
    `;

    body.innerHTML = bodyHTML;

    // Footer
    const footer = document.createElement('div');
    footer.className = 'confirm-delete-dialog-footer';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'confirm-delete-btn confirm-delete-btn-cancel';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.addEventListener('click', () => overlay.remove());

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'confirm-delete-btn confirm-delete-btn-delete';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', () => this.performDelete(deleteBtn, overlay));

    footer.appendChild(cancelBtn);
    footer.appendChild(deleteBtn);

    // Assemble card
    card.appendChild(header);
    card.appendChild(body);
    card.appendChild(footer);

    // Assemble dialog
    overlay.appendChild(card);

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.remove();
    });

    // Close on ESC key
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        overlay.remove();
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);

    document.body.appendChild(overlay);

    // Focus the delete button for accessibility
    deleteBtn.focus();
  }

  performDelete(deleteBtn, overlay) {
    // Disable button during request
    deleteBtn.disabled = true;
    deleteBtn.textContent = 'Deleting...';

    if (!this.deleteUrl) {
      deleteBtn.disabled = false;
      deleteBtn.textContent = 'Delete';
      this.showAlert('Delete URL is not configured', 'error');
      console.error('ConfirmDeleteDialog: deleteUrl is not set');
      return;
    }

    fetch(this.deleteUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': this.csrfToken,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({}),
      redirect: 'follow'  // Important: Follow redirects
    })
      .then(r => {
        console.log('Delete response status:', r.status, r.statusText);
        console.log('Delete response URL:', r.url);
        
        // Success cases:
        // - 302/301 redirect: Traditional Django form submission (fetch follows automatically)
        // - 200 with JSON: API returning success JSON
        // - 204: No Content (successful deletion)
        
        if (r.status === 204) {
          // No content response - successful deletion
          return { success: true };
        }
        
        // For success statuses, check if it's JSON
        if (r.status === 200 || r.status === 201) {
          const contentType = r.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            return r.json().then(data => ({ ...data }));
          } else {
            // Successful response but not JSON - assume success
            console.log('Non-JSON success response, assuming deletion was successful');
            return { success: true };
          }
        }
        
        // Fetch automatically follows redirects, so if we get here with 200,
        // it means the redirect succeeded
        if (r.ok) {
          console.log('Successful response (followed redirect or direct success)');
          return { success: true };
        }
        
        // Error response
        const contentType = r.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return r.json().then(data => ({ ...data }));
        } else {
          return { 
            success: false, 
            message: 'Server error: ' + r.status + ' ' + r.statusText
          };
        }
      })
      .then(data => {
        console.log('Parsed delete response:', data);
        
        if (data.success) {
          overlay.remove();
          this.showAlert('Item deleted successfully', 'success');
          setTimeout(() => {
            if (this.redirectUrl) {
              window.location.href = this.redirectUrl;
            } else {
              this.onSuccess();
            }
          }, 1500);
        } else {
          deleteBtn.disabled = false;
          deleteBtn.textContent = 'Delete';
          const errorMsg = data.message || data.error || 'Failed to delete item';
          this.showAlert(errorMsg, 'error');
          console.error('Delete failed:', data);
        }
      })
      .catch(e => {
        console.error('Delete request error:', e);
        deleteBtn.disabled = false;
        deleteBtn.textContent = 'Delete';
        this.showAlert('Network error: ' + (e.message || 'Failed to delete item. Please try again.'), 'error');
      });
  }

  showAlert(message, type = 'info') {
    // Remove existing alert if any
    const existingAlert = document.getElementById('confirmDeleteAlert');
    if (existingAlert) existingAlert.remove();

    // Add alert styles if not already present
    const style = document.createElement('style');
    style.textContent = `
      .confirm-delete-alert {
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        padding: 14px 16px;
        border-radius: var(--radius-sm, 8px);
        border: 1px solid;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 999;
        animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      @keyframes slideInRight {
        from {
          opacity: 0;
          transform: translateX(100%);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      .confirm-delete-alert-info {
        background: rgba(56, 189, 248, 0.08);
        border-color: rgba(56, 189, 248, 0.2);
        color: var(--text-primary);
      }
      .confirm-delete-alert-warning {
        background: rgba(245, 158, 11, 0.08);
        border-color: rgba(245, 158, 11, 0.2);
        color: var(--text-primary);
      }
      .confirm-delete-alert-success {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.2);
        color: var(--text-primary);
      }
      .confirm-delete-alert-error {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.2);
        color: var(--text-primary);
      }
      .confirm-delete-alert-icon {
        flex-shrink: 0;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .confirm-delete-alert-content {
        flex: 1;
        font-size: 0.9rem;
        font-weight: 500;
      }
      .confirm-delete-alert-close {
        flex-shrink: 0;
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 1.2rem;
        padding: 0;
        transition: color 0.2s ease;
      }
      .confirm-delete-alert-close:hover {
        color: var(--text-primary);
      }
    `;
    if (!document.querySelector('style[data-confirm-delete-alert]')) {
      style.setAttribute('data-confirm-delete-alert', 'true');
      document.head.appendChild(style);
    }

    const alert = document.createElement('div');
    alert.id = 'confirmDeleteAlert';
    alert.className = `confirm-delete-alert confirm-delete-alert-${type}`;

    const iconMap = {
      info: '<i class="fa-solid fa-circle-info"></i>',
      warning: '<i class="fa-solid fa-triangle-exclamation"></i>',
      success: '<i class="fa-solid fa-circle-check"></i>',
      error: '<i class="fa-solid fa-circle-xmark"></i>'
    };

    const icon = document.createElement('span');
    icon.className = 'confirm-delete-alert-icon';
    icon.innerHTML = iconMap[type] || '<i class="fa-solid fa-circle"></i>';

    const content = document.createElement('span');
    content.className = 'confirm-delete-alert-content';
    content.textContent = message;

    const closeBtn = document.createElement('button');
    closeBtn.className = 'confirm-delete-alert-close';
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

  getCookie(name) {
    let v = null;
    if (document.cookie) {
      document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) {
          v = decodeURIComponent(c.substring(name.length + 1));
        }
      });
    }
    return v;
  }
}

// Helper function to initialize delete dialogs from delete buttons
function initializeDeleteButton(button, options = {}) {
  button.addEventListener('click', (e) => {
    e.preventDefault();
    
    // Validate delete URL
    const deleteUrl = options.deleteUrl || button.dataset.deleteUrl;
    if (!deleteUrl) {
      console.error('Error: No delete URL provided. Set data-delete-url or pass deleteUrl in options.');
      alert('Delete URL is not configured. Please try again.');
      return;
    }
    
    const dialog = new ConfirmDeleteDialog({
      itemName: options.itemName || 'item',
      itemLabel: button.dataset.itemLabel || options.itemLabel,
      deleteUrl: deleteUrl,
      redirectUrl: button.dataset.redirectUrl || options.redirectUrl,
      details: options.details || {}
    });
    dialog.show();
  });
}

// Initialize all delete buttons with data-confirm-delete attribute
window.addEventListener('load', () => {
  document.querySelectorAll('[data-confirm-delete]').forEach(button => {
    const options = {
      itemName: button.dataset.itemName || 'item',
      itemLabel: button.dataset.itemLabel || '',
      deleteUrl: button.dataset.deleteUrl || button.form?.action,
      redirectUrl: button.dataset.redirectUrl || '',
      details: {}
    };

    // Parse details from data attributes
    if (button.dataset.details) {
      try {
        options.details = JSON.parse(button.dataset.details);
      } catch (e) {
        console.error('Failed to parse details:', e);
      }
    }

    // Log configuration for debugging
    if (!options.deleteUrl) {
      console.warn('Warning: Delete button missing data-delete-url attribute', button);
    }

    initializeDeleteButton(button, options);
  });
});
