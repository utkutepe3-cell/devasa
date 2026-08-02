document.addEventListener('DOMContentLoaded', function () {

    // User Info
    const currentUser = { name: 'Merchant Admin' };
    const userInfoEl = document.getElementById('userInfo');
    if (userInfoEl) {
        userInfoEl.textContent = currentUser.name;
    }
    document.getElementById('logoutBtn').addEventListener('click', function() {
        if (confirm('Çıkış yapmak istediğinizden emin misiniz?')) {
            window.location.href = 'login.html';
        }
    });

    // Navigation
    const navSubitems = document.querySelectorAll('.nav-subitem');
    const navGroupToggles = document.querySelectorAll('.nav-group-toggle');
    const pages = document.querySelectorAll('.page');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');

    // Page navigation
    navSubitems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const pageId = this.dataset.page;
            navigateToPage(pageId);
        });
    });

    // Dashboard nav item
    document.querySelector('[data-page="dashboard"]').addEventListener('click', function (e) {
        e.preventDefault();
        navigateToPage('dashboard');
    });

    function navigateToPage(pageId) {
        navSubitems.forEach(i => i.classList.remove('active'));
        const activeNav = document.querySelector(`[data-page="${pageId}"]`);
        if (activeNav) activeNav.classList.add('active');

        pages.forEach(p => p.classList.remove('active'));
        const targetPage = document.getElementById(`page-${pageId}`);
        if (targetPage) targetPage.classList.add('active');

        if (window.innerWidth <= 768) {
            sidebar.classList.remove('mobile-open');
        }
    }

    // Sidebar group toggles
    navGroupToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            const group = this.closest('.nav-group');
            const submenu = group.querySelector('.nav-submenu');
            const icon = this.querySelector('.toggle-icon');

            if (group.classList.contains('expanded')) {
                group.classList.remove('expanded');
                submenu.classList.add('collapsed');
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-right');
            } else {
                group.classList.add('expanded');
                submenu.classList.remove('collapsed');
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-down');
            }
        });
    });

    // Sidebar toggle (mobile)
    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('mobile-open');
    });

    // Modal
    const modalOverlay = document.getElementById('modalOverlay');
    const modalClose = document.getElementById('modalClose');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    function showModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = content;
        modalOverlay.classList.add('active');
    }

    function hideModal() {
        modalOverlay.classList.remove('active');
    }

    modalClose.addEventListener('click', hideModal);
    modalCloseBtn.addEventListener('click', hideModal);
    modalOverlay.addEventListener('click', function (e) {
        if (e.target === modalOverlay) hideModal();
    });

    document.getElementById('printReceipt').addEventListener('click', function() {
        const content = document.getElementById('modalBody').innerHTML;
        const title = document.getElementById('modalTitle').textContent;
        const printWindow = window.open('', '_blank', 'width=400,height=600');
        printWindow.document.write(`
            <html><head><title>Makbuz - ${title}</title>
            <style>
                body { font-family: monospace; padding: 20px; font-size: 12px; }
                h2 { text-align: center; border-bottom: 2px dashed #000; padding-bottom: 10px; }
                .result-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dotted #ccc; }
                .result-label { font-weight: bold; }
                .header { text-align: center; margin-bottom: 20px; }
                .footer { text-align: center; margin-top: 20px; border-top: 2px dashed #000; padding-top: 10px; font-size: 10px; }
            </style></head><body>
            <div class="header">
                <h2>VIRTUAL TERMINAL</h2>
                <p>Payment Gateway Receipt</p>
            </div>
            <h3>${title}</h3>
            ${content}
            <div class="footer">
                <p>Transaction Date: ${new Date().toLocaleString()}</p>
                <p>Merchant: ${currentUser.name || 'N/A'}</p>
                <p>--- Thank You ---</p>
            </div>
            </body></html>
        `);
        printWindow.document.close();
        printWindow.print();
    });

    // Transaction storage
    let transactions = JSON.parse(localStorage.getItem('vt_transactions') || '[]');

    function saveTransactions() {
        localStorage.setItem('vt_transactions', JSON.stringify(transactions));
    }

    function generateTransactionId() {
        return 'TXN' + Date.now().toString(36).toUpperCase() + Math.random().toString(36).substr(2, 4).toUpperCase();
    }

    function formatCardNumber(number) {
        return '****' + number.slice(-4);
    }

    function formatCurrency(amount) {
        return '$' + parseFloat(amount).toFixed(2);
    }

    function simulateTransaction() {
        const rand = Math.random();
        if (rand < 0.85) return { status: 'approved', code: '00', message: 'Transaction Approved' };
        if (rand < 0.92) return { status: 'declined', code: '05', message: 'Do Not Honor' };
        if (rand < 0.96) return { status: 'declined', code: '51', message: 'Insufficient Funds' };
        return { status: 'declined', code: '14', message: 'Invalid Card Number' };
    }

    // Key Enter Card - Process Transaction
    document.getElementById('processTransaction').addEventListener('click', function () {
        const amount = document.getElementById('amount').value.trim();
        const cardNumber = document.getElementById('cardNumber').value.trim().replace(/\s/g, '');
        const expMonth = document.getElementById('expMonth').value.trim();
        const expYear = document.getElementById('expYear').value.trim();
        const transType = document.getElementById('transactionType').value;

        if (!amount || !cardNumber || !expMonth || !expYear) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please fill in all required fields (Amount, Card Number, Expiration Date).</p>');
            return;
        }

        if (isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a valid amount.</p>');
            return;
        }

        if (cardNumber.length < 13 || cardNumber.length > 19) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a valid card number.</p>');
            return;
        }

        const result = simulateTransaction();
        const txn = {
            id: generateTransactionId(),
            date: new Date().toISOString(),
            type: transType,
            amount: parseFloat(amount),
            cardLast4: cardNumber.slice(-4),
            status: result.status,
            responseCode: result.code,
            responseMessage: result.message,
            billingName: document.getElementById('billingName').value,
            invoiceNumber: document.getElementById('invoiceNumber').value
        };

        transactions.unshift(txn);
        saveTransactions();

        const statusClass = result.status === 'approved' ? 'result-success' : 'result-error';
        const statusIcon = result.status === 'approved' ? 'fa-check-circle' : 'fa-times-circle';

        showModal('Transaction Result', `
            <p class="${statusClass}" style="font-size:16px;margin-bottom:16px;">
                <i class="fas ${statusIcon}"></i> ${result.message}
            </p>
            <div class="result-item"><span class="result-label">Transaction ID</span><span class="result-value">${txn.id}</span></div>
            <div class="result-item"><span class="result-label">Type</span><span class="result-value">${transType.replace('_', ' ').toUpperCase()}</span></div>
            <div class="result-item"><span class="result-label">Amount</span><span class="result-value">${formatCurrency(amount)}</span></div>
            <div class="result-item"><span class="result-label">Card</span><span class="result-value">${formatCardNumber(cardNumber)}</span></div>
            <div class="result-item"><span class="result-label">Response Code</span><span class="result-value">${result.code}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Unmatched Refund - Process
    document.getElementById('processRefund').addEventListener('click', function () {
        const amount = document.getElementById('refundAmount').value.trim();
        const cardNumber = document.getElementById('refundCardNumber').value.trim().replace(/\s/g, '');
        const expMonth = document.getElementById('refundExpMonth').value.trim();
        const expYear = document.getElementById('refundExpYear').value.trim();
        const reason = document.getElementById('refundReason').value;
        const confirmed = document.getElementById('refundConfirm').checked;

        if (!amount || !cardNumber || !expMonth || !expYear || !reason) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please fill in all required fields (Amount, Card Number, Expiration Date, Reason).</p>');
            return;
        }

        if (isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a valid refund amount.</p>');
            return;
        }

        if (cardNumber.length < 13 || cardNumber.length > 19) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a valid card number.</p>');
            return;
        }

        if (!confirmed) {
            showModal('Confirmation Required', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> You must confirm the unmatched refund authorization checkbox before processing.</p>');
            return;
        }

        const result = simulateTransaction();
        const txn = {
            id: generateTransactionId(),
            date: new Date().toISOString(),
            type: 'unmatched_refund',
            amount: parseFloat(amount),
            cardLast4: cardNumber.slice(-4),
            status: result.status,
            responseCode: result.code,
            responseMessage: result.status === 'approved' ? 'Refund Approved' : result.message,
            reason: reason,
            reasonDescription: document.getElementById('refundReasonDescription').value,
            customerName: document.getElementById('refundCustomerName').value,
            customerEmail: document.getElementById('refundCustomerEmail').value,
            notes: document.getElementById('refundNotes').value
        };

        transactions.unshift(txn);
        saveTransactions();

        const statusClass = result.status === 'approved' ? 'result-success' : 'result-error';
        const statusIcon = result.status === 'approved' ? 'fa-check-circle' : 'fa-times-circle';
        const resultMessage = result.status === 'approved' ? 'Unmatched Refund Approved' : result.message;

        showModal('Unmatched Refund Result', `
            <p class="${statusClass}" style="font-size:16px;margin-bottom:16px;">
                <i class="fas ${statusIcon}"></i> ${resultMessage}
            </p>
            <div class="result-item"><span class="result-label">Transaction ID</span><span class="result-value">${txn.id}</span></div>
            <div class="result-item"><span class="result-label">Type</span><span class="result-value">UNMATCHED REFUND</span></div>
            <div class="result-item"><span class="result-label">Refund Amount</span><span class="result-value">${formatCurrency(amount)}</span></div>
            <div class="result-item"><span class="result-label">Card</span><span class="result-value">${formatCardNumber(cardNumber)}</span></div>
            <div class="result-item"><span class="result-label">Reason</span><span class="result-value">${reason.replace(/_/g, ' ')}</span></div>
            <div class="result-item"><span class="result-label">Response Code</span><span class="result-value">${result.code}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Void Transaction
    document.getElementById('processVoid').addEventListener('click', function () {
        const transId = document.getElementById('voidTransId').value.trim();

        if (!transId) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a Transaction ID.</p>');
            return;
        }

        const txnIndex = transactions.findIndex(t => t.id === transId);
        if (txnIndex === -1) {
            showModal('Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Transaction not found.</p>');
            return;
        }

        transactions[txnIndex].status = 'voided';
        saveTransactions();

        showModal('Void Result', `
            <p class="result-success" style="font-size:16px;margin-bottom:16px;">
                <i class="fas fa-check-circle"></i> Transaction Voided Successfully
            </p>
            <div class="result-item"><span class="result-label">Transaction ID</span><span class="result-value">${transId}</span></div>
            <div class="result-item"><span class="result-label">Original Amount</span><span class="result-value">${formatCurrency(transactions[txnIndex].amount)}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Matched Refund
    document.getElementById('processMatchedRefund').addEventListener('click', function () {
        const transId = document.getElementById('refundTransId').value.trim();
        const refundAmt = document.getElementById('matchedRefundAmount').value.trim();

        if (!transId) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a Transaction ID.</p>');
            return;
        }

        const txnIndex = transactions.findIndex(t => t.id === transId);
        if (txnIndex === -1) {
            showModal('Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Transaction not found.</p>');
            return;
        }

        const originalTxn = transactions[txnIndex];
        const amount = refundAmt ? parseFloat(refundAmt) : originalTxn.amount;

        const refundTxn = {
            id: generateTransactionId(),
            date: new Date().toISOString(),
            type: 'refund',
            amount: amount,
            cardLast4: originalTxn.cardLast4,
            status: 'approved',
            responseCode: '00',
            responseMessage: 'Refund Approved',
            originalTransId: transId
        };

        transactions.unshift(refundTxn);
        saveTransactions();

        showModal('Refund Result', `
            <p class="result-success" style="font-size:16px;margin-bottom:16px;">
                <i class="fas fa-check-circle"></i> Refund Processed Successfully
            </p>
            <div class="result-item"><span class="result-label">Refund ID</span><span class="result-value">${refundTxn.id}</span></div>
            <div class="result-item"><span class="result-label">Original Transaction</span><span class="result-value">${transId}</span></div>
            <div class="result-item"><span class="result-label">Refund Amount</span><span class="result-value">${formatCurrency(amount)}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Capture Transaction
    document.getElementById('processCapture').addEventListener('click', function () {
        const transId = document.getElementById('captureTransId').value.trim();

        if (!transId) {
            showModal('Validation Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Please enter a Transaction ID.</p>');
            return;
        }

        const txnIndex = transactions.findIndex(t => t.id === transId && t.type === 'auth_only');
        if (txnIndex === -1) {
            showModal('Error', '<p class="result-error"><i class="fas fa-exclamation-circle"></i> Authorization transaction not found.</p>');
            return;
        }

        transactions[txnIndex].type = 'capture';
        transactions[txnIndex].status = 'approved';
        saveTransactions();

        showModal('Capture Result', `
            <p class="result-success" style="font-size:16px;margin-bottom:16px;">
                <i class="fas fa-check-circle"></i> Transaction Captured Successfully
            </p>
            <div class="result-item"><span class="result-label">Transaction ID</span><span class="result-value">${transId}</span></div>
            <div class="result-item"><span class="result-label">Amount</span><span class="result-value">${formatCurrency(transactions[txnIndex].amount)}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Settle Batch
    document.getElementById('settleBatch').addEventListener('click', function () {
        const unsettled = transactions.filter(t => t.status === 'approved' && (t.type === 'sale' || t.type === 'capture'));
        if (unsettled.length === 0) {
            showModal('Settlement', '<p class="result-error"><i class="fas fa-info-circle"></i> No transactions to settle.</p>');
            return;
        }

        let total = 0;
        unsettled.forEach(t => {
            t.status = 'settled';
            total += t.amount;
        });
        saveTransactions();

        showModal('Batch Settlement', `
            <p class="result-success" style="font-size:16px;margin-bottom:16px;">
                <i class="fas fa-check-circle"></i> Batch Settled Successfully
            </p>
            <div class="result-item"><span class="result-label">Transactions Settled</span><span class="result-value">${unsettled.length}</span></div>
            <div class="result-item"><span class="result-label">Total Amount</span><span class="result-value">${formatCurrency(total)}</span></div>
            <div class="result-item"><span class="result-label">Date</span><span class="result-value">${new Date().toLocaleString()}</span></div>
        `);

        updateDashboard();
    });

    // Search Transactions
    document.getElementById('searchTransactions').addEventListener('click', function () {
        const dateFrom = document.getElementById('searchDateFrom').value;
        const dateTo = document.getElementById('searchDateTo').value;
        const typeFilter = document.getElementById('searchTransType').value;
        const statusFilter = document.getElementById('searchStatus').value;

        let filtered = [...transactions];

        if (dateFrom) {
            filtered = filtered.filter(t => new Date(t.date) >= new Date(dateFrom));
        }
        if (dateTo) {
            const toDate = new Date(dateTo);
            toDate.setHours(23, 59, 59);
            filtered = filtered.filter(t => new Date(t.date) <= toDate);
        }
        if (typeFilter) {
            filtered = filtered.filter(t => t.type === typeFilter);
        }
        if (statusFilter) {
            filtered = filtered.filter(t => t.status === statusFilter);
        }

        renderTransactionTable(filtered);
    });

    function renderTransactionTable(txns) {
        const tbody = document.getElementById('transactionTableBody');
        if (txns.length === 0) {
            tbody.innerHTML = '<tr class="empty-row"><td colspan="7">No transactions found.</td></tr>';
            return;
        }

        tbody.innerHTML = txns.map(txn => {
            const badgeClass = txn.status === 'approved' || txn.status === 'settled' ? 'badge-success' :
                txn.status === 'declined' ? 'badge-danger' :
                    txn.status === 'voided' ? 'badge-warning' : 'badge-info';
            return `
                <tr>
                    <td><strong>${txn.id}</strong></td>
                    <td>${new Date(txn.date).toLocaleDateString()}</td>
                    <td>${txn.type.replace(/_/g, ' ').toUpperCase()}</td>
                    <td>${formatCurrency(txn.amount)}</td>
                    <td>****${txn.cardLast4}</td>
                    <td><span class="badge ${badgeClass}">${txn.status}</span></td>
                    <td>
                        ${txn.status === 'approved' && txn.type === 'sale' ? `<button class="btn btn-sm btn-danger" onclick="voidTxn('${txn.id}')">Void</button>` : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Make voidTxn globally accessible
    window.voidTxn = function (id) {
        const idx = transactions.findIndex(t => t.id === id);
        if (idx !== -1) {
            transactions[idx].status = 'voided';
            saveTransactions();
            document.getElementById('searchTransactions').click();
            updateDashboard();
        }
    };

    // Clear forms
    document.getElementById('clearForm').addEventListener('click', function () {
        const section = document.getElementById('page-key-enter-card');
        section.querySelectorAll('input, textarea').forEach(el => { el.value = ''; });
        section.querySelectorAll('select').forEach(el => { el.selectedIndex = 0; });
    });

    document.getElementById('clearRefundForm').addEventListener('click', function () {
        const section = document.getElementById('page-unmatched-refund');
        section.querySelectorAll('input, textarea').forEach(el => {
            if (el.type === 'checkbox') el.checked = false;
            else el.value = '';
        });
        section.querySelectorAll('select').forEach(el => { el.selectedIndex = 0; });
    });

    // Card number formatting
    function formatCardInput(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 16) value = value.substr(0, 16);
        const formatted = value.replace(/(\d{4})(?=\d)/g, '$1 ');
        e.target.value = formatted;
    }

    document.getElementById('cardNumber').addEventListener('input', formatCardInput);
    document.getElementById('refundCardNumber').addEventListener('input', formatCardInput);

    // Dashboard update
    function updateDashboard() {
        const today = new Date().toDateString();
        const todayTxns = transactions.filter(t => new Date(t.date).toDateString() === today);

        const sales = todayTxns.filter(t => (t.type === 'sale' || t.type === 'capture') && t.status === 'approved');
        const refunds = todayTxns.filter(t => t.type === 'refund' || t.type === 'unmatched_refund');
        const declined = todayTxns.filter(t => t.status === 'declined');

        const totalSales = sales.reduce((sum, t) => sum + t.amount, 0);
        const totalRefunds = refunds.reduce((sum, t) => sum + t.amount, 0);

        document.getElementById('todaySales').textContent = formatCurrency(totalSales);
        document.getElementById('todayTransactions').textContent = todayTxns.length;
        document.getElementById('todayRefunds').textContent = formatCurrency(totalRefunds);
        document.getElementById('todayDeclined').textContent = declined.length;

        // Recent transactions
        const recentTbody = document.getElementById('recentTransactions');
        const recent = transactions.slice(0, 10);
        if (recent.length === 0) {
            recentTbody.innerHTML = '<tr class="empty-row"><td colspan="5">No recent transactions.</td></tr>';
        } else {
            recentTbody.innerHTML = recent.map(txn => {
                const badgeClass = txn.status === 'approved' || txn.status === 'settled' ? 'badge-success' :
                    txn.status === 'declined' ? 'badge-danger' :
                        txn.status === 'voided' ? 'badge-warning' : 'badge-info';
                return `
                    <tr>
                        <td><strong>${txn.id}</strong></td>
                        <td>${new Date(txn.date).toLocaleDateString()}</td>
                        <td>${txn.type.replace(/_/g, ' ').toUpperCase()}</td>
                        <td>${formatCurrency(txn.amount)}</td>
                        <td><span class="badge ${badgeClass}">${txn.status}</span></td>
                    </tr>
                `;
            }).join('');
        }
    }

    // Show Hints
    document.getElementById('showHints').addEventListener('click', function () {
        showModal('Hints', `
            <ul style="padding-left:16px;line-height:2;">
                <li>Required fields are marked with an orange indicator (●)</li>
                <li>Card numbers are formatted automatically as you type</li>
                <li>Use "Unmatched Refund" to refund without a matching original transaction</li>
                <li>Transaction IDs are needed for Void and Refund operations</li>
                <li>All transactions can be viewed in the "View Transactions" page</li>
                <li>Use "Settle Transactions" to batch settle approved transactions</li>
            </ul>
        `);
    });

    // Help button
    document.getElementById('helpBtn').addEventListener('click', function () {
        showModal('Help', `
            <h4 style="margin-bottom:8px;">Virtual Terminal Help</h4>
            <p style="margin-bottom:12px;">This virtual terminal allows you to process card-not-present transactions.</p>
            <h4 style="margin-bottom:8px;">Transaction Types:</h4>
            <ul style="padding-left:16px;line-height:2;">
                <li><strong>Sale</strong> - Authorize and capture in one step</li>
                <li><strong>Auth Only</strong> - Authorize only, capture later</li>
                <li><strong>Credit</strong> - Issue a credit to a card</li>
                <li><strong>Unmatched Refund</strong> - Refund without original transaction reference</li>
            </ul>
        `);
    });

    // Customer search (simulated)
    document.getElementById('searchCustomer').addEventListener('click', function () {
        showModal('Customer Search', '<p style="color:var(--text-muted);text-align:center;padding:20px;">No customers found matching your criteria.</p>');
    });

    // Shipping estimate (simulated)
    document.getElementById('shippingEstimate').addEventListener('click', function () {
        showModal('Shipping Estimate', '<p style="color:var(--text-muted);text-align:center;padding:20px;">Please enter billing address to calculate shipping estimate.</p>');
    });

    // Initialize dashboard on load
    updateDashboard();
});
