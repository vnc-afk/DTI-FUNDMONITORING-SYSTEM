/**
 * calculations.js
 */

// Initialize form calculations and functionality
function initializeCalculations() {
    // ===== BANK STATEMENT FORM =====
    // Handle balance calculation for bank statement forms
    const debitInput = document.querySelector('input[name="debit"]');
    const creditInput = document.querySelector('input[name="credit"]');
    const balanceInput = document.querySelector('input[name="balance"]');
    
    if (debitInput && creditInput && balanceInput) {
        // Get context variables from Django template
        const isFirstTransactionEl = document.getElementById('is_first_transaction');
        const previousBalanceEl = document.getElementById('previous_balance');
        
        const isFirstTransaction = isFirstTransactionEl ? JSON.parse(isFirstTransactionEl.dataset.value) : false;
        const previousBalance = previousBalanceEl ? parseFloat(previousBalanceEl.dataset.value) : 0;

        // Function to calculate balance
        function calculateBalance() {
            const debit = parseFloat(debitInput.value) || 0;
            const credit = parseFloat(creditInput.value) || 0;
            
            // Calculate: Previous Balance + Credit - Debit
            const newBalance = previousBalance + credit - debit;
            
            // Update balance field
            balanceInput.value = newBalance.toFixed(2);
        }

        // For subsequent transactions, add event listeners to auto-calculate
        if (!isFirstTransaction) {
            // Set initial balance to previous balance
            balanceInput.value = previousBalance.toFixed(2);
            
            // Add event listeners for real-time calculation
            debitInput.addEventListener('input', calculateBalance);
            creditInput.addEventListener('input', calculateBalance);
        }
    }

    // ===== MASTER FUND MONITORING FORM =====
    // Get form field references
    const payeeSelect = document.querySelector('[name="payee"]');
    const tinField = document.querySelector('[name="tin"]');
    const taxTypeField = document.querySelector('[name="tax_type"]');
    const purchaseTypeSelect = document.querySelector('[name="purchase_type"]');
    const paymentsInput = document.querySelector('[name="payments"]');

    // Tax field mappings
    const taxFields = {
        'vat_goods_5': 'goods_5_percent',
        'vat_services_5': 'services_5_percent',
        'vat_goods_services_3': 'goods_services_3_percent',
        'vat_goods_1': 'goods_1_percent',
        'vat_services_2': 'services_2_percent',
        'vat_rental_5': 'rental_5_percent',
        'vat_prof_fee_10': 'prof_fee_10_percent',
    };

    // Handle supplier change
    if (payeeSelect) {
        payeeSelect.addEventListener('change', function() {
            const supplierId = this.value;
            
            if (supplierId) {
                fetch(`/api/supplier/${supplierId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (tinField) tinField.value = data.tin || '';
                        if (taxTypeField) {
                            const vatStatusText = data.vat_status === 'V' ? 'VAT Registered' : 'Non-VAT';
                            taxTypeField.value = vatStatusText;
                        }
                    })
                    .catch(error => console.error('Error fetching supplier data:', error));
            } else {
                if (tinField) tinField.value = '';
                if (taxTypeField) taxTypeField.value = '';
            }
        });

        if (payeeSelect.value) {
            payeeSelect.dispatchEvent(new Event('change'));
        }
    }

    // Handle purchase type change and auto-calculate taxes
    if (purchaseTypeSelect) {
        purchaseTypeSelect.addEventListener('change', function() {
            const purchaseTypeId = this.value;
            
            if (purchaseTypeId) {
                fetch(`/api/tax_rates/${purchaseTypeId}/`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(errorData => {
                                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                            }).catch(() => {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            });
                        }
                        return response.json();
                    })
                    .then(taxRates => {
                        // Check if response contains an error
                        if (taxRates.status === 'error' || taxRates.error) {
                            console.error('✗ API Error:', taxRates.error);
                            console.warn('No tax rates available for this purchase type. Tax fields will be cleared.');
                            // Clear tax fields instead of showing alert
                            Object.values(taxFields).forEach(fieldName => {
                                const field = document.querySelector(`[name="${fieldName}"]`);
                                if (field) field.value = '';
                            });
                            return;
                        }
                        
                        // Get current payment amount
                        const paymentAmount = parseFloat(paymentsInput?.value || 0);
                        
                        console.log(`Purchase Type ID: ${purchaseTypeId}`);
                        console.log(`Payment Amount: ₱${paymentAmount.toFixed(2)}`);
                        console.log('Tax Rates Retrieved:', taxRates);
                        
                        if (paymentAmount > 0) {
                            // Calculate and populate each tax field
                            for (const [taxKey, fieldName] of Object.entries(taxFields)) {
                                const taxRate = taxRates[taxKey];
                                const taxField = document.querySelector(`[name="${fieldName}"]`);
                                
                                if (taxField && taxRate !== null && taxRate !== undefined) {
                                    // Calculate tax amount
                                    const taxAmount = (paymentAmount * taxRate).toFixed(2);
                                    taxField.value = taxAmount;
                                    console.log(`${fieldName}: ${taxAmount} (${taxKey} = ${taxRate})`);
                                } else if (taxField) {
                                    // Clear if no rate available
                                    taxField.value = '';
                                }
                            }
                            
                            console.log('[TAX] Tax rates calculated and applied');
                        } else {
                            console.log('[WARNING] Payment amount is 0 or empty - taxes not calculated');
                            // Clear all tax fields if no payment
                            Object.values(taxFields).forEach(fieldName => {
                                const field = document.querySelector(`[name="${fieldName}"]`);
                                if (field) field.value = '';
                            });
                        }
                    })
                    .catch(error => {
                        console.error('✗ Error fetching tax rates:', error);
                        // Only show alert for critical errors
                        if (error.message.includes('network') || error.message.includes('Failed to fetch')) {
                            alert('Network error while loading tax rates. Please check your connection.');
                        } else {
                            console.warn('Tax rates unavailable. Clearing tax fields.');
                        }
                        // Clear tax fields on error
                        Object.values(taxFields).forEach(fieldName => {
                            const field = document.querySelector(`[name="${fieldName}"]`);
                            if (field) field.value = '';
                        });
                    });
            } else {
                // Clear all tax fields if no purchase type selected
                console.log('No purchase type selected - clearing tax fields');
                Object.values(taxFields).forEach(fieldName => {
                    const field = document.querySelector(`[name="${fieldName}"]`);
                    if (field) field.value = '';
                });
            }
        });
    }

    // Handle payment amount change - recalculate taxes if purchase type is selected
    if (paymentsInput) {
        paymentsInput.addEventListener('change', function() {
            if (purchaseTypeSelect?.value) {
                console.log('Payment amount changed - recalculating taxes');
                purchaseTypeSelect.dispatchEvent(new Event('change'));
            }
        });
    }

    // Trigger initial load if purchase type is pre-selected
    if (purchaseTypeSelect?.value) {
        console.log('Initial load - purchase type pre-selected, calculating taxes');
        purchaseTypeSelect.dispatchEvent(new Event('change'));
    }

    // ===== TAX FORM - FORMULA EVALUATION =====
    // Get all input fields with formula wrappers
    const taxInputs = document.querySelectorAll('.formula-wrapper .form-control');
    
    taxInputs.forEach(input => {
        input.addEventListener('input', function() {
            const wrapper = this.closest('.formula-wrapper');
            const resultSpan = wrapper.querySelector('.formula-result');
            const value = this.value.trim();
            
            if (value.startsWith('=')) {
                // This is a formula
                try {
                    // Remove the = sign and evaluate the expression
                    const formula = value.substring(1);
                    
                    // Sanitize the formula to prevent code injection
                    // Only allow: numbers, operators (+, -, *, /, %), parentheses, and decimal points
                    if (!/^[0-9+\-*/%().\s]+$/.test(formula)) {
                        resultSpan.textContent = 'Invalid formula';
                        resultSpan.classList.remove('has-value');
                        return;
                    }
                    
                    // Evaluate the formula safely
                    const result = Function('"use strict"; return (' + formula + ')')();
                    
                    // Format result to 8 decimal places
                    const formattedResult = parseFloat(result).toFixed(8);
                    resultSpan.textContent = formattedResult;
                    resultSpan.classList.add('has-value');
                    
                    // Store the original formula in a data attribute
                    this.dataset.formula = value;
                } catch (e) {
                    resultSpan.textContent = 'Error';
                    resultSpan.classList.remove('has-value');
                }
            } else if (value === '') {
                // Empty field
                resultSpan.textContent = '';
                resultSpan.classList.remove('has-value');
                if (this.dataset.formula) {
                    delete this.dataset.formula;
                }
            } else {
                // Plain number
                resultSpan.textContent = value;
                resultSpan.classList.add('has-value');
                if (this.dataset.formula) {
                    delete this.dataset.formula;
                }
            }
        });
        
        // Trigger input event on page load to show any existing values
        input.dispatchEvent(new Event('input'));
    });

    // Initialize Searchable Dropdowns
    const selects = document.querySelectorAll('.form-select');
    selects.forEach(function(select) {
        new TomSelect(select, {
            create: false,
            placeholder: 'Search and select...',
            allowEmptyOption: false,
            hideSelected: true,
            maxOptions: null,
            plugins: {
                remove_button: {
                    title: 'Remove'
                }
            },
            render: {
                option: function(data, escape) {
                    // Filter out empty or divider options
                    if (!data.text || data.text.match(/^-+$/)) {
                        return '';
                    }
                    return '<div>' + escape(data.text) + '</div>';
                },
                item: function(data, escape) {
                    return '<div>' + escape(data.text) + '</div>';
                }
            }
        });
    });

    // Determine color class based on purchase type name
    function getColorClass(purchaseTypeName) {
        const name = purchaseTypeName.trim();
        
        if (name.startsWith('NV')) {
            return 'cell-nvat'; // Blue for Non-VAT
        } else if (name.toLowerCase().includes('premium')) {
            return 'cell-premium'; // Yellow for Premium
        } else if (name.startsWith('V')) {
            return 'cell-vat'; // Green for VAT
        }
        return ''; // No color coding for others
    }

    // Color code the data cells based on purchase type
    const tableBody = document.querySelector('#tableBody');
    if (tableBody) {
        const rows = tableBody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell && firstCell.textContent.trim() !== '') {
                const purchaseTypeName = firstCell.textContent.trim();
                const colorClass = getColorClass(purchaseTypeName);

                if (colorClass) {
                    // Apply color class to all data cells (excluding first and last)
                    const dataCells = row.querySelectorAll('td:not(:first-child):not(:last-child)');
                    dataCells.forEach(cell => {
                        cell.classList.add(colorClass);
                    });
                }
            }
        });

        // Process formula values in table cells
        const cells = tableBody.querySelectorAll('td:not(:first-child):not(:last-child)');
        
        cells.forEach(cell => {
            const value = cell.textContent.trim();
            
            // Check if the value is a formula (starts with =)
            if (value.startsWith('=')) {
                try {
                    // Remove the = sign and evaluate the expression
                    const formula = value.substring(1);
                    
                    // Sanitize the formula to prevent code injection
                    // Only allow: numbers, operators (+, -, *, /, %), parentheses, and decimal points
                    if (!/^[0-9+\-*/%().\s]+$/.test(formula)) {
                        cell.textContent = 'Invalid';
                        cell.style.color = '#d32f2f';
                        return;
                    }
                    
                    // Evaluate the formula safely
                    const result = Function('"use strict"; return (' + formula + ')')();
                    
                    // Format result to 3 decimal places
                    const formattedResult = parseFloat(result).toFixed(3).replace(/\.?0+$/, '');
                    cell.textContent = formattedResult;
                    cell.style.fontWeight = 'bold';
                } catch (e) {
                    cell.textContent = 'Error';
                    cell.style.color = '#d32f2f';
                }
            }
        });
    }

}

// Initialize on page load and when AJAX loads new content
document.addEventListener('DOMContentLoaded', initializeCalculations);
