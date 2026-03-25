/**
 * Bulk Delete Functionality
 * Handles mass selection and deletion of table rows
 */

class BulkDeleteManager {
  constructor(options = {}) {
    this.bulkDeleteBtn = document.getElementById(options.bulkDeleteBtnId || 'bulkDeleteBtn');
    this.tableBody = document.getElementById(options.tableBodyId || 'tableBody');
    this.modelName = options.modelName || 'item';
    this.deleteUrl = options.deleteUrl;
    this.csrfToken = this.getCookie('csrftoken');
    
    this.isSelectionMode = false;
    this.selectedIds = new Set();
    
    if (this.bulkDeleteBtn && this.tableBody) {
      this.init();
    }
  }
  
  init() {
    this.bulkDeleteBtn.addEventListener('click', (e) => this.toggleSelectionMode(e));
  }
  
  toggleSelectionMode() {
    this.isSelectionMode = !this.isSelectionMode;
    
    if (this.isSelectionMode) {
      this.enterSelectionMode();
    } else {
      this.exitSelectionMode();
    }
  }
  
  enterSelectionMode() {
    this.bulkDeleteBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
      Cancel
    `;
    
    // Add styles for checkboxes if not already present
    const style = document.createElement('style');
    style.textContent = `
      .row-checkbox {
        width: 18px;
        height: 18px;
        cursor: pointer;
        accent-color: var(--accent, #3b82f6);
        appearance: none;
        -webkit-appearance: none;
        background: var(--bg-surface);
        border: 1.5px solid var(--border);
        border-radius: 4px;
        margin: 0;
        padding: 0;
        transition: all 0.2s ease;
      }
      .row-checkbox:hover {
        border-color: var(--accent, #3b82f6);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
      }
      .row-checkbox:checked {
        background: var(--accent, #3b82f6);
        border-color: var(--accent, #3b82f6);
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 90%;
      }
      .row-checkbox:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
      }
      .delete-selected-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 18px;
        border-radius: var(--radius-sm, 8px);
        border: 2px solid var(--danger, #ef4444);
        background: var(--danger, #ef4444);
        color: white;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: var(--font-body, -apple-system, BlinkMacSystemFont, sans-serif);
      }
      .delete-selected-btn:hover {
        background: #f87171;
        border-color: #f87171;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
        transform: translateY(-2px);
      }
      .delete-selected-btn:active {
        transform: translateY(0);
      }
      .delete-selected-btn svg {
        width: 18px;
        height: 18px;
        stroke-width: 2.5;
      }
    `;
    if (!document.querySelector('style[data-bulk-delete-checkboxes]')) {
      style.setAttribute('data-bulk-delete-checkboxes', 'true');
      document.head.appendChild(style);
    }
    
    // Add checkboxes to rows
    this.tableBody.querySelectorAll('tr').forEach((row, index) => {
      const firstCell = row.querySelector('td');
      if (firstCell && !firstCell.querySelector('input[type="checkbox"]')) {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'row-checkbox';
        checkbox.value = row.dataset.id;
        
        checkbox.addEventListener('change', () => this.updateSelection());
        
        firstCell.insertBefore(checkbox, firstCell.firstChild);
      }
    });
    
    // Add "Select All" checkbox to the table header
    const thead = this.tableBody.parentElement.querySelector('thead');
    if (thead) {
      const headerRow = thead.querySelector('tr');
      if (headerRow) {
        const firstHeaderCell = headerRow.querySelector('th');
        if (firstHeaderCell && !firstHeaderCell.querySelector('input[type="checkbox"]')) {
          const selectAllCheckbox = document.createElement('input');
          selectAllCheckbox.type = 'checkbox';
          selectAllCheckbox.id = 'selectAllCheckbox';
          selectAllCheckbox.className = 'row-checkbox';
          
          selectAllCheckbox.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
          
          firstHeaderCell.insertBefore(selectAllCheckbox, firstHeaderCell.firstChild);
        }
      }
    }
    
    // Add Delete Selected button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-selected-btn';
    deleteBtn.id = 'deleteSelectedBtn';
    deleteBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
        <path d="M10 11v6"/><path d="M14 11v6"/>
        <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
      </svg>
      Delete Selected
    `;
    deleteBtn.addEventListener('click', () => this.deleteSelected());
    
    this.bulkDeleteBtn.parentElement.insertBefore(deleteBtn, this.bulkDeleteBtn.nextSibling);
  }
  
  exitSelectionMode() {
    this.bulkDeleteBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
        <path d="M10 11v6"/><path d="M14 11v6"/>
        <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
      </svg>
      Delete
    `;
    
    // Remove checkboxes
    this.tableBody.querySelectorAll('input.row-checkbox').forEach(cb => {
      cb.parentElement.removeChild(cb);
    });
    
    // Remove Select All checkbox
    const thead = this.tableBody.parentElement.querySelector('thead');
    if (thead) {
      const selectAllCheckbox = thead.querySelector('input[type="checkbox"]');
      if (selectAllCheckbox) {
        selectAllCheckbox.parentElement.removeChild(selectAllCheckbox);
      }
    }
    
    // Remove Delete Selected button
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    if (deleteBtn) deleteBtn.remove();
    
    this.selectedIds.clear();
  }
  
  toggleSelectAll(checked) {
    this.tableBody.querySelectorAll('input.row-checkbox').forEach(cb => {
      cb.checked = checked;
    });
    this.updateSelection();
  }
  
  updateSelection() {
    this.selectedIds.clear();
    const allCheckboxes = this.tableBody.querySelectorAll('input.row-checkbox');
    const checkedCheckboxes = this.tableBody.querySelectorAll('input.row-checkbox:checked');
    
    checkedCheckboxes.forEach(cb => {
      this.selectedIds.add(cb.value);
    });
    
    // Update "Select All" checkbox state
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    if (selectAllCheckbox) {
      selectAllCheckbox.checked = allCheckboxes.length > 0 && allCheckboxes.length === checkedCheckboxes.length;
      selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
    }
  }
  
  deleteSelected() {
    this.updateSelection();
    
    if (this.selectedIds.size === 0) {
      this.showAlert(`Please select at least one ${this.modelName}`, 'warning');
      return;
    }
    
    const count = this.selectedIds.size;
    const msg = count === 1 ? `${this.modelName}` : `${this.modelName}s`;
    
    this.showConfirmationDialog(count, msg);
  }
  
  showAlert(message, type = 'info') {
    // Remove existing alert if any
    const existingAlert = document.getElementById('bulkDeleteAlert');
    if (existingAlert) existingAlert.remove();
    
    // Add alert styles if not already present
    const style = document.createElement('style');
    style.textContent = `
      .bulk-delete-alert {
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
      .bulk-delete-alert-info {
        background: rgba(56, 189, 248, 0.08);
        border-color: rgba(56, 189, 248, 0.2);
        color: var(--text-primary);
      }
      .bulk-delete-alert-warning {
        background: rgba(245, 158, 11, 0.08);
        border-color: rgba(245, 158, 11, 0.2);
        color: var(--text-primary);
      }
      .bulk-delete-alert-success {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.2);
        color: var(--text-primary);
      }
      .bulk-delete-alert-error {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.2);
        color: var(--text-primary);
      }
      .bulk-delete-alert-icon {
        flex-shrink: 0;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .bulk-delete-alert-content {
        flex: 1;
        font-size: 0.9rem;
        font-weight: 500;
      }
      .bulk-delete-alert-close {
        flex-shrink: 0;
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 1.2rem;
        padding: 0;
        transition: color 0.2s ease;
      }
      .bulk-delete-alert-close:hover {
        color: var(--text-primary);
      }
    `;
    if (!document.querySelector('style[data-bulk-delete-alert]')) {
      style.setAttribute('data-bulk-delete-alert', 'true');
      document.head.appendChild(style);
    }
    
    const alert = document.createElement('div');
    alert.id = 'bulkDeleteAlert';
    alert.className = `bulk-delete-alert bulk-delete-alert-${type}`;
    
    const iconMap = {
      info: '<i class="fa-solid fa-circle-info"></i>',
      warning: '<i class="fa-solid fa-triangle-exclamation"></i>',
      success: '<i class="fa-solid fa-circle-check"></i>',
      error: '<i class="fa-solid fa-circle-xmark"></i>'
    };
    
    const icon = document.createElement('span');
    icon.className = 'bulk-delete-alert-icon';
    icon.innerHTML = iconMap[type] || '<i class="fa-solid fa-circle"></i>';
    
    const content = document.createElement('span');
    content.className = 'bulk-delete-alert-content';
    content.textContent = message;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'bulk-delete-alert-close';
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
  
  showConfirmationDialog(count, itemLabel) {
    // Remove existing dialog if any
    const existingDialog = document.getElementById('bulkDeleteConfirmDialog');
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
      .bulk-delete-overlay {
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
      .bulk-delete-dialog {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius, 12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        max-width: 420px;
        width: 90%;
        overflow: hidden;
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .bulk-delete-dialog-header {
        padding: 20px 24px;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.04));
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: flex-start;
        gap: 14px;
      }
      .bulk-delete-dialog-header-icon {
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
      .bulk-delete-dialog-header-text h5 {
        margin: 0 0 6px 0;
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: -0.01em;
      }
      .bulk-delete-dialog-header-text p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-weight: 500;
      }
      .bulk-delete-dialog-body {
        padding: 24px;
        background: var(--bg-card);
        color: var(--text-primary);
      }
      .bulk-delete-dialog-body p {
        margin: 0 0 16px 0;
        font-size: 0.9rem;
        line-height: 1.6;
        color: var(--text-primary);
      }
      .bulk-delete-dialog-body strong {
        font-weight: 600;
        color: var(--danger, #ef4444);
      }
      .bulk-delete-warning {
        padding: 12px 14px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.15);
        border-left: 3px solid var(--danger, #ef4444);
        border-radius: var(--radius-sm, 8px);
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .bulk-delete-warning-icon {
        color: var(--danger, #ef4444);
        font-size: 1.1rem;
        flex-shrink: 0;
      }
      .bulk-delete-warning-text {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
      }
      .bulk-delete-dialog-footer {
        padding: 16px 24px;
        background: var(--bg-surface);
        border-top: 1px solid var(--border);
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }
      .bulk-delete-btn {
        padding: 9px 18px;
        border-radius: var(--radius-sm, 8px);
        border: none;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: var(--font-body, -apple-system, BlinkMacSystemFont, sans-serif);
      }
      .bulk-delete-btn-cancel {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-strong);
      }
      .bulk-delete-btn-cancel:hover {
        background: var(--bg-card);
        border-color: var(--accent);
        color: var(--accent);
      }
      .bulk-delete-btn-cancel:active {
        transform: scale(0.98);
      }
      .bulk-delete-btn-delete {
        background: var(--danger, #ef4444);
        color: white;
        border: 2px solid var(--danger, #ef4444);
      }
      .bulk-delete-btn-delete:hover {
        background: #f87171;
        border-color: #f87171;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
        transform: translateY(-1px);
      }
      .bulk-delete-btn-delete:active {
        transform: translateY(0);
      }
    `;
    if (!document.querySelector('style[data-bulk-delete-dialog]')) {
      style.setAttribute('data-bulk-delete-dialog', 'true');
      document.head.appendChild(style);
    }
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'bulkDeleteConfirmDialog';
    overlay.className = 'bulk-delete-overlay';
    
    // Create dialog card
    const card = document.createElement('div');
    card.className = 'bulk-delete-dialog';
    
    // Header
    const header = document.createElement('div');
    header.className = 'bulk-delete-dialog-header';
    
    const icon = document.createElement('div');
    icon.className = 'bulk-delete-dialog-header-icon';
    icon.innerHTML = `
      <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
    `;
    
    const headerContent = document.createElement('div');
    headerContent.className = 'bulk-delete-dialog-header-text';
    headerContent.style.flex = '1';
    headerContent.innerHTML = `
      <h5>Confirm Deletion</h5>
      <p>This action cannot be undone</p>
    `;
    
    header.appendChild(icon);
    header.appendChild(headerContent);
    
    // Body
    const body = document.createElement('div');
    body.className = 'bulk-delete-dialog-body';
    body.innerHTML = `
      <p>You are about to delete <strong>${count}</strong> ${itemLabel}.</p>
      <div class="bulk-delete-warning">
        <span class="bulk-delete-warning-icon"><i class="fa-solid fa-triangle-exclamation"></i></span>
        <span class="bulk-delete-warning-text">This action is permanent and cannot be reversed.</span>
      </div>
    `;
    
    // Footer
    const footer = document.createElement('div');
    footer.className = 'bulk-delete-dialog-footer';
    
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'bulk-delete-btn bulk-delete-btn-cancel';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.addEventListener('click', () => overlay.remove());
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'bulk-delete-btn bulk-delete-btn-delete';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', () => {
      overlay.remove();
      this.performDelete();
    });
    
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
  
  performDelete() {
    fetch(this.deleteUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({ ids: Array.from(this.selectedIds) })
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        this.showAlert('Items deleted successfully', 'success');
        setTimeout(() => location.reload(), 1500);
      } else {
        this.showAlert(data.message || 'Failed to delete items', 'error');
      }
    })
    .catch(e => {
      console.error(e);
      this.showAlert('An error occurred while deleting items', 'error');
    });
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

// Initialize bulk delete manager
function initializeBulkDelete() {
  const bulkManager = window.bulkDeleteManager;
  if (bulkManager) {
    new BulkDeleteManager(bulkManager);
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initializeBulkDelete();
});
