/**
 * Form Submission Handler with Modern Modal
 * Provides theme-aware form submission with confirmation dialogs, loading states, and toast notifications
 */

class FormSubmissionHandler {
  constructor(options = {}) {
    this.form = options.form || null;
    this.title = options.title || 'Confirm Action';
    this.message = options.message || 'Are you sure you want to proceed?';
    this.confirmText = options.confirmText || 'Submit';
    this.cancelText = options.cancelText || 'Cancel';
    this.confirmationType = options.confirmationType || 'info'; // 'info', 'success'
    this.details = options.details || {};
    this.detailFields = options.detailFields || []; // Array of field names to show as details
    this.onSubmit = options.onSubmit || null;
    this.suppressConfirmation = options.suppressConfirmation || false;
    this.enableLivePreview = options.enableLivePreview !== false; // Enabled by default
    this.setupLivePreview();
  }

  /**
   * Setup real-time preview updates as user types
   */
  setupLivePreview() {
    if (!this.form || !this.detailFields || this.detailFields.length === 0 || !this.enableLivePreview) {
      return;
    }

    // Listen to all input changes on specified fields
    this.detailFields.forEach(fieldName => {
      // Try to find the field
      let field = this.form.elements[fieldName];
      
      // If it's a RadioNodeList (for radio buttons), get the first element
      if (field && field.length !== undefined && typeof field[0] !== 'undefined') {
        field = field[0];
      }
      
      if (!field) {
        field = this.form.querySelector(
          `input[name="${fieldName}"], ` +
          `select[name="${fieldName}"], ` +
          `textarea[name="${fieldName}"]`
        );
      }
      
      // Validate field is a proper element
      if (!field || typeof field.addEventListener !== 'function') {
        console.warn(`⚠️  Field "${fieldName}" found but is not a valid element or doesn't support addEventListener`);
        return;
      }

      // Handle different input types
      try {
        if (field.type === 'checkbox') {
          field.addEventListener('change', () => this.updateLivePreview());
        } else if (field.type === 'radio') {
          // For radio buttons, listen to all with same name
          const radios = this.form.querySelectorAll(`input[name="${fieldName}"]`);
          radios.forEach(radio => {
            if (radio && typeof radio.addEventListener === 'function') {
              radio.addEventListener('change', () => this.updateLivePreview());
            }
          });
        } else if (field.tagName === 'SELECT') {
          field.addEventListener('change', () => this.updateLivePreview());
        } else {
          // Text, number, date, textarea
          field.addEventListener('input', () => this.updateLivePreview());
          field.addEventListener('change', () => this.updateLivePreview());
        }
      } catch (e) {
        console.error(`❌ Error attaching listeners to field "${fieldName}":`, e);
      }
    });
  }

  /**
   * Update live preview of details
   */
  updateLivePreview() {
    if (!this.detailFields || this.detailFields.length === 0) return;

    // Capture current values
    this.details = this.captureFormDetails(this.detailFields);

    // Update the details display in the modal if it's open
    const detailsContainer = document.querySelector('.form-submission-dialog-details');
    if (detailsContainer) {
      this.updateDetailsDisplay(detailsContainer);
    }
  }

  /**
   * Update the details display in the modal
   */
  updateDetailsDisplay(container) {
    let html = '<div class="form-submission-dialog-details-title">Details</div>';
    
    for (const [key, value] of Object.entries(this.details)) {
      html += `
        <div class="form-submission-dialog-details-item">
          <span class="form-submission-dialog-details-label">${key}:</span>
          <span class="form-submission-dialog-details-value">${value}</span>
        </div>
      `;
    }

    container.innerHTML = html;
  }

  /**
   * Auto-capture form field values for detail display
   * @param {string[]} fieldNames - Array of form field names to capture
   * @returns {object} Key-value pairs of field labels and values
   */
  captureFormDetails(fieldNames) {
    const details = {};
    
    if (!this.form || !fieldNames || fieldNames.length === 0) {
      return details;
    }

    const foundFields = [];
    const notFoundFields = [];

    fieldNames.forEach(fieldName => {
      // Try to find the field using multiple methods
      let field = this.form.elements[fieldName];
      
      // If it's a RadioNodeList (for radio buttons), get the first element
      if (field && field.length !== undefined && typeof field[0] !== 'undefined') {
        field = field[0];
      }
      
      // If not found in form.elements, try querySelector
      if (!field) {
        field = this.form.querySelector(
          `input[name="${fieldName}"], ` +
          `select[name="${fieldName}"], ` +
          `textarea[name="${fieldName}"]`
        );
      }
      
      // Validate field is a proper element
      if (!field || !field.tagName) {
        notFoundFields.push(fieldName);
        console.warn(`⚠️  Form field not found or invalid: "${fieldName}"`);
        return;
      }

      foundFields.push(fieldName);

      // Get the label text - but for radio buttons, use field name instead
      let label = '';
      let value = '';

      // Determine label and value based on field type
      if (field.type === 'radio') {
        // For radio buttons, use field name as label
        label = fieldName.charAt(0).toUpperCase() + fieldName.slice(1).replace(/_/g, ' ');
        
        try {
          const checkedRadio = this.form.querySelector(`input[name="${fieldName}"]:checked`);
          value = checkedRadio ? checkedRadio.value : 'Not selected';
        } catch (e) {
          console.warn(`⚠️  Error reading radio button "${fieldName}":`, e);
          value = '(Error reading value)';
        }
      } else {
        // For other field types, extract label from associated label element
        label = this.form.querySelector(`label[for="${field.id}"]`)?.textContent?.trim()
          || this.form.querySelector(`label[for="${field.id}"]`)?.innerText?.trim()
          || fieldName.charAt(0).toUpperCase() + fieldName.slice(1).replace(/_/g, ' ');

        try {
          if (field.type === 'checkbox') {
            value = field.checked ? 'Yes' : 'No';
          } else if (field.tagName === 'SELECT') {
            // For SELECT elements (including Tom Select), read the value directly
            // Tom Select wraps selects, so we read the value which is set by Tom Select
            if (field.value) {
              // Get the text of the selected option
              const selectedOption = Array.from(field.options).find(opt => opt.value === field.value);
              if (selectedOption) {
                value = (selectedOption.textContent || selectedOption.text || selectedOption.value || '').trim();
              } else {
                value = field.value;
              }
            }
            
            if (!value) {
              value = '(Empty)';
            }
          } else if (field.tagName === 'TEXTAREA') {
            value = field.value || '(Empty)';
          } else {
            value = field.value || '(Empty)';
          }
        } catch (e) {
          console.warn(`⚠️  Error reading value from field "${fieldName}":`, e);
          value = '(Error reading value)';
        }
      }

      // Remove required asterisk if present
      const cleanLabel = label.replace(/\s*\*\s*$/, '').trim();

      // Format the value
      if (value && typeof value === 'string') {
        try {
          // Format currency fields
          if (fieldName.toLowerCase().includes('debit') || 
              fieldName.toLowerCase().includes('credit') ||
              fieldName.toLowerCase().includes('balance') ||
              fieldName.toLowerCase().includes('payment') ||
              fieldName.toLowerCase().includes('amount')) {
            if (!isNaN(value) && value !== '') {
              value = `₱ ${parseFloat(value).toLocaleString('en-PH', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            }
          }

          // Format date fields
          if (fieldName.toLowerCase().includes('date') && value !== '(Empty)') {
            try {
              const date = new Date(value);
              if (!isNaN(date)) {
                value = date.toLocaleDateString('en-PH', {year: 'numeric', month: 'short', day: 'numeric'});
              }
            } catch (e) {
              // Keep original value if date parsing fails
            }
          }
        } catch (e) {
          console.warn(`⚠️  Error formatting value for field "${fieldName}":`, e);
        }
      }

      details[cleanLabel] = value;
    });

    if (notFoundFields.length > 0) {
      console.warn(`⚠️  Could not find ${notFoundFields.length} fields: ${notFoundFields.join(', ')}`);
    }
    if (foundFields.length > 0) {
      console.log(`✅ Found ${foundFields.length} fields: ${foundFields.join(', ')}`);
    }

    return details;
  }

  submit(event) {
    if (event && event.preventDefault) {
      event.preventDefault();
    }

    // If detail fields are specified, auto-capture them
    if (this.detailFields && this.detailFields.length > 0 && Object.keys(this.details).length === 0) {
      this.details = this.captureFormDetails(this.detailFields);
    }

    if (this.suppressConfirmation) {
      this.performSubmit();
    } else {
      this.showConfirmationDialog();
    }
  }

  showConfirmationDialog() {
    // Remove existing dialog if any
    const existingDialog = document.getElementById('formSubmissionDialog');
    if (existingDialog) existingDialog.remove();

    // Capture details if not already done
    if (this.detailFields && this.detailFields.length > 0 && Object.keys(this.details).length === 0) {
      this.details = this.captureFormDetails(this.detailFields);
    }

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
      .form-submission-overlay {
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
      .form-submission-dialog {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius, 12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        max-width: 500px;
        width: 90%;
        overflow: hidden;
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .form-submission-dialog-header {
        padding: 20px 24px;
        background: var(--bg-surface);
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: flex-start;
        gap: 14px;
      }
      .form-submission-dialog-header.success {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.04));
      }
      .form-submission-dialog-header.info {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(56, 189, 248, 0.04));
      }
      .form-submission-dialog-header-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1.3rem;
      }
      .form-submission-dialog-header.success .form-submission-dialog-header-icon {
        background: rgba(59, 130, 246, 0.12);
        color: var(--accent, #3b82f6);
      }
      .form-submission-dialog-header.info .form-submission-dialog-header-icon {
        background: rgba(56, 189, 248, 0.12);
        color: var(--accent, #60a5fa);
      }
      .form-submission-dialog-header-text h5 {
        margin: 0 0 6px 0;
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: -0.01em;
      }
      .form-submission-dialog-header-text p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
        font-weight: 500;
      }
      .form-submission-dialog-body {
        padding: 24px;
        background: var(--bg-card);
      }
        padding: 14px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm, 8px);
        margin-bottom: 16px;
      }
      .form-submission-dialog-details-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .form-submission-dialog-details-title::after {
        content: '🔄';
        font-size: 0.9rem;
        opacity: 0.6;
      }
      .form-submission-dialog-details-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        padding: 6px 0;
        border-bottom: 1px solid var(--border);
        animation: highlightUpdate 0.3s ease-out;
      }
      @keyframes highlightUpdate {
        0% {
          background-color: rgba(59, 130, 246, 0.2);
          padding: 6px 4px;
        }
        100% {
          background-color: transparent;
          padding: 6px 0;
        }
      }
      .form-submission-dialog-details-item:last-child {
        border-bottom: none;
      }
      .form-submission-dialog-details-label {
        color: var(--text-secondary);
        font-weight: 500;
      }
      .form-submission-dialog-details-value {
        color: var(--text-primary);
        font-weight: 600;
        word-break: break-word;
        max-width: 60%;
        text-align: right;
      }
      .form-submission-dialog-footer {
        padding: 16px 24px;
        background: var(--bg-surface);
        border-top: 1px solid var(--border);
        display: flex;
        gap: 12px;
        justify-content: flex-end;
      }
      .form-submission-btn {
        padding: 9px 18px;
        border-radius: var(--radius-sm, 8px);
        border: none;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: var(--font-body, -apple-system, BlinkMacSystemFont, sans-serif);
        display: inline-flex;
        align-items: center;
        gap: 6px;
      }
      .form-submission-btn-cancel {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-strong);
      }
      .form-submission-btn-cancel:hover {
        background: var(--bg-card);
        border-color: var(--accent);
        color: var(--accent);
      }
      .form-submission-btn-cancel:active {
        transform: scale(0.98);
      }
      .form-submission-btn-submit {
        background: var(--accent);
        color: white;
        border: 2px solid var(--accent);
      }
      .form-submission-btn-submit:hover {
        background: #60a5fa;
        border-color: #60a5fa;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
      }
      .form-submission-btn-submit:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none !important;
      }
    `;
    if (!document.querySelector('style[data-form-submission-dialog]')) {
      style.setAttribute('data-form-submission-dialog', 'true');
      document.head.appendChild(style);
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'formSubmissionDialog';
    overlay.className = 'form-submission-overlay';

    // Create dialog card
    const card = document.createElement('div');
    card.className = 'form-submission-dialog';

    // Header
    const header = document.createElement('div');
    header.className = `form-submission-dialog-header ${this.confirmationType}`;

    const icon = document.createElement('div');
    icon.className = 'form-submission-dialog-header-icon';
    
    // Use SVG icons based on confirmation type
    const iconSVGs = {
      info: `<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>`,
      success: `<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
      </svg>`
    };
    
    icon.innerHTML = iconSVGs[this.confirmationType] || iconSVGs.info;

    const headerContent = document.createElement('div');
    headerContent.className = 'form-submission-dialog-header-text';
    headerContent.style.flex = '1';
    headerContent.innerHTML = `
      <h5>${this.title}</h5>
      <p>Please review and confirm</p>
    `;

    header.appendChild(icon);
    header.appendChild(headerContent);

    // Body
    const body = document.createElement('div');
    body.className = 'form-submission-dialog-body';

    let bodyHTML = `<p>${this.message}</p>`;

    // Add details if provided
    if (Object.keys(this.details).length > 0) {
      bodyHTML += `
        <div class="form-submission-dialog-details">
          <div class="form-submission-dialog-details-title">Details</div>
      `;
      for (const [key, value] of Object.entries(this.details)) {
        bodyHTML += `
          <div class="form-submission-dialog-details-item">
            <span class="form-submission-dialog-details-label">${key}:</span>
            <span class="form-submission-dialog-details-value">${value}</span>
          </div>
        `;
      }
      bodyHTML += `</div>`;
    }

    body.innerHTML = bodyHTML;

    // Footer
    const footer = document.createElement('div');
    footer.className = 'form-submission-dialog-footer';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'form-submission-btn form-submission-btn-cancel';
    cancelBtn.textContent = this.cancelText;
    cancelBtn.addEventListener('click', () => overlay.remove());

    const submitBtn = document.createElement('button');
    submitBtn.className = 'form-submission-btn form-submission-btn-submit';
    submitBtn.textContent = this.confirmText;
    submitBtn.addEventListener('click', () => {
      overlay.remove();
      this.performSubmit(submitBtn);
    });

    footer.appendChild(cancelBtn);
    footer.appendChild(submitBtn);

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

    // Focus the submit button for accessibility
    submitBtn.focus();
  }

  performSubmit(submitBtn) {
    if (this.onSubmit) {
      // Custom submit handler
      this.onSubmit(submitBtn);
    } else if (this.form) {
      // Standard form submission
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span style="margin-right: 6px;">⏳</span> Submitting...`;
      
      // Show success toast
      const toastMessage = this.confirmText || 'Saved successfully';
      this.showAlert(toastMessage, 'success');
      
      // Delay slightly for better UX - let user see the toast
      setTimeout(() => {
        this.form.submit();
      }, 800);
    }
  }

  showAlert(message, type = 'info') {
    // Remove existing alert if any
    const existingAlert = document.getElementById('formSubmissionAlert');
    if (existingAlert) existingAlert.remove();

    // Add alert styles if not already present
    const style = document.createElement('style');
    style.textContent = `
      .form-submission-alert {
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
      .form-submission-alert-info {
        background: rgba(56, 189, 248, 0.08);
        border-color: rgba(56, 189, 248, 0.2);
        color: var(--text-primary);
      }
      .form-submission-alert-success {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.2);
        color: var(--text-primary);
      }
      .form-submission-alert-icon {
        flex-shrink: 0;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .form-submission-alert-content {
        flex: 1;
        font-size: 0.9rem;
        font-weight: 500;
      }
      .form-submission-alert-close {
        flex-shrink: 0;
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 1.2rem;
        padding: 0;
        transition: color 0.2s ease;
      }
      .form-submission-alert-close:hover {
        color: var(--text-primary);
      }
    `;
    if (!document.querySelector('style[data-form-submission-alert]')) {
      style.setAttribute('data-form-submission-alert', 'true');
      document.head.appendChild(style);
    }

    const alert = document.createElement('div');
    alert.id = 'formSubmissionAlert';
    alert.className = `form-submission-alert form-submission-alert-${type}`;

    const iconMap = {
      info: 'ℹ️',
      success: '✓'
    };

    const icon = document.createElement('span');
    icon.className = 'form-submission-alert-icon';
    icon.textContent = iconMap[type] || '•';

    const content = document.createElement('span');
    content.className = 'form-submission-alert-content';
    content.textContent = message;

    const closeBtn = document.createElement('button');
    closeBtn.className = 'form-submission-alert-close';
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
}

// Easy initialization with data attributes
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-form-submit-confirm]').forEach(form => {
    // Parse detail fields from data attribute
    const detailFieldsStr = form.dataset.detailFields || '';
    const detailFields = detailFieldsStr ? detailFieldsStr.split(',').map(f => f.trim()) : [];

    const handler = new FormSubmissionHandler({
      form: form,
      title: form.dataset.confirmTitle || 'Confirm Submission',
      message: form.dataset.confirmMessage || 'Are you sure?',
      confirmText: form.dataset.confirmText || 'Submit',
      confirmationType: form.dataset.confirmationType || 'info',
      icon: form.dataset.confirmIcon || 'ℹ️',
      detailFields: detailFields,
      suppressConfirmation: form.dataset.suppressConfirmation === 'true'
    });

    form.addEventListener('submit', (e) => handler.submit(e));
  });
});
