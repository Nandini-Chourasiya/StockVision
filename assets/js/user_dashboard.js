/* ============================================
   StockVision - User Dashboard JavaScript
   Chart.js Integration & Prediction Controls
   ============================================ */

(function () {
    'use strict';

    let priceChart = null;

    // ============================================
    // Initialize Dashboard
    // ============================================
    function init() {
        initDateDefaults();
        initPriceChart();
        initPredictionForm();
        initAlerts();

        // Listen for theme changes
        window.addEventListener('themechange', updateChartTheme);
    }

    // ============================================
    // Set Default Date Values
    // ============================================
    function initDateDefaults() {
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);

        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');

        if (startDateInput && endDateInput) {
            startDateInput.value = formatDate(thirtyDaysAgo);
            endDateInput.value = formatDate(today);
        }
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    // ============================================
    // Price Chart Initialization
    // ============================================
    function initPriceChart() {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;

        const colors = getChartColors();
        const data = generateDummyData();

        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Historical',
                        data: data.historical,
                        borderColor: colors.historical,
                        backgroundColor: hexToRgba(colors.historical, 0.1),
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    },
                    {
                        label: 'Predicted',
                        data: data.predicted,
                        borderColor: colors.predicted,
                        backgroundColor: hexToRgba(colors.predicted, 0.1),
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: colors.text,
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: colors.background,
                        titleColor: colors.text,
                        bodyColor: colors.text,
                        borderColor: colors.grid,
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: colors.grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: colors.text,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        grid: {
                            color: colors.grid,
                            drawBorder: false
                        },
                        ticks: {
                            color: colors.text,
                            callback: function (value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    // ============================================
    // Generate Dummy Data for Chart
    // ============================================
    function generateDummyData(days = 30) {
        const labels = [];
        const historical = [];
        const predicted = [];

        const basePrice = 2500 + Math.random() * 500;
        let price = basePrice;

        const today = new Date();

        for (let i = days; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            labels.push(date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }));

            // Generate realistic price movement
            const change = (Math.random() - 0.48) * 50;
            price = Math.max(price + change, basePrice * 0.8);

            if (i > 5) {
                historical.push(Math.round(price * 100) / 100);
                predicted.push(null);
            } else {
                historical.push(null);
                // Predicted values with slight offset
                const predictedPrice = price + (Math.random() - 0.5) * 30;
                predicted.push(Math.round(predictedPrice * 100) / 100);
            }
        }

        // Fill in predicted values overlap
        const lastHistorical = historical.filter(v => v !== null).pop();
        const predictedStartIdx = historical.lastIndexOf(lastHistorical);
        if (predictedStartIdx >= 0) {
            predicted[predictedStartIdx] = lastHistorical;
        }

        return { labels, historical, predicted };
    }

    // ============================================
    // Prediction Form Handler
    // ============================================
    function initPredictionForm() {
        const form = document.getElementById('prediction-form');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            runPrediction();
        });
    }

    function runPrediction() {
        const stockSelect = document.getElementById('stock-select');
        const startDate = document.getElementById('start-date');
        const endDate = document.getElementById('end-date');
        const modelInputs = document.querySelectorAll('input[name="model"]');

        let selectedModel = 'linear';
        modelInputs.forEach(input => {
            if (input.checked) selectedModel = input.value;
        });

        const params = {
            symbol: stockSelect.value,
            stock_name: stockSelect.value, // Use symbol as name for custom entries
            start_date: startDate.value,
            end_date: endDate.value,
            model: selectedModel
        };

        console.log('Running prediction with params:', params);

        const submitBtn = document.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Running...';
        submitBtn.disabled = true;

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateChart(data.prediction);
                    updateMetrics(data.prediction);
                    updateDashboardStats();
                    updateRecentPredictions();
                } else {
                    alert('Prediction failed: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Prediction error:', error);
                alert('An error occurred while running prediction.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
    }

    function updateChart(data) {
        if (!priceChart) return;

        const colors = getChartColors();

        // Convert backend data format to Chart.js format
        // Backend returns "historical" and "predicted" as separate arrays
        // We need to merge them for the chart or keep them separate as per design

        // Ensure labels match the data length (assuming backend returns aligned data)
        // If necessary, generate labels from dates

        // For simplicity, assuming backend returns data aligned with what the chart expects
        // But backend prediction object has 'historical' and 'predicted' lists

        // We might need to regenerate labels based on the data
        // For this implementation, let's assume valid data structure or basic label generation

        const totalPoints = data.historical.length + data.predicted.length;
        const labels = Array(totalPoints).fill('');
        // Ideally backend should return dates, but for now we might need to rely on the current chart config or regenerate
        // Let's rely on dummy label generation or just use index if dates aren't provided in the simpler response structure above
        // The backend response structure: "historical": [...], "predicted": [...]

        // Reuse label generation for now to keep it looking nice (or improve if backend sends dates)
        // Since backend doesn't send dates in the simple example, we might need to infer them.
        // However, let's just update the datasets directly.

        // NOTE: A robust implementation would get dates from backend.
        // For now, let's splice the arrays to match

        // Re-generate labels based on current date for visualization
        const newLabels = [];
        const today = new Date();
        const start = new Date(today);
        start.setDate(today.getDate() - data.historical.length);

        for (let i = 0; i < data.historical.length; i++) {
            const d = new Date(start);
            d.setDate(start.getDate() + i);
            newLabels.push(d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }));
        }
        for (let i = 0; i < data.predicted.length; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i + 1);
            newLabels.push(d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }));
        }

        priceChart.data.labels = newLabels;

        // Pad historical with nulls for prediction part
        const historicalData = [...data.historical, ...Array(data.predicted.length).fill(null)];

        // Pad predicted with nulls for historical part (except connecting point)
        const lastHist = data.historical[data.historical.length - 1];
        const predictedData = [...Array(data.historical.length - 1).fill(null), lastHist, ...data.predicted];

        priceChart.data.datasets[0].data = historicalData;
        priceChart.data.datasets[1].data = predictedData;

        priceChart.update('active');
    }

    function updateMetrics(prediction) {
        if (!prediction) return;

        document.getElementById('metric-mae').textContent = prediction.mae ? prediction.mae.toFixed(2) : '-';
        document.getElementById('metric-rmse').textContent = prediction.rmse ? prediction.rmse.toFixed(2) : '-';

        const trendEl = document.getElementById('metric-trend');
        trendEl.textContent = prediction.trend_label || '-';
        trendEl.parentElement.className = 'summary-item ' + (prediction.trend === 'bullish' ? 'positive' : prediction.trend === 'bearish' ? 'negative' : '');

        document.getElementById('metric-confidence').textContent = prediction.confidence_label || '-';
    }

    // Fetch and update top dashboard stats
    function updateDashboardStats() {
        fetch('/api/user/stats')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const countEl = document.querySelector('.metric-value[data-counter]');
                    if (countEl) countEl.textContent = data.total_predictions;

                    const stocks = document.querySelectorAll('.metric-value');
                    if (stocks[1]) stocks[1].textContent = data.last_stock;

                    if (stocks[3]) stocks[3].textContent = data.avg_confidence_label;
                }
            })
            .catch(err => console.error('Failed to update stats:', err));
    }

    // Fetch and update recent predictions table
    function updateRecentPredictions() {
        fetch('/api/user/predictions?per_page=10')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.predictions) {
                    const tbody = document.querySelector('.data-table tbody');
                    if (!tbody) return;

                    tbody.innerHTML = '';

                    if (data.predictions.length === 0) {
                        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No predictions yet. Run your first one!</td></tr>`;
                        return;
                    }

                    data.predictions.forEach(pred => {
                        const row = document.createElement('tr');
                        const date = new Date(pred.created_at).toLocaleDateString() + ' ' + new Date(pred.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        const trendClass = pred.trend === 'bullish' ? 'active' : (pred.trend === 'bearish' ? 'inactive' : 'pending');

                        row.innerHTML = `
                            <td>${date}</td>
                            <td>${pred.stock.symbol}</td>
                            <td>${pred.model_used}</td>
                            <td>${pred.horizon_days} days</td>
                            <td><span class="status-badge ${trendClass}">${pred.trend_label}</span></td>
                            <td>${pred.confidence_label}</td>
                        `;
                        tbody.appendChild(row);
                    });
                }
            })
            .catch(err => console.error('Failed to update table:', err));
    }

    function updateChart(data) {
        if (!priceChart) return;

        const colors = getChartColors();

        priceChart.data.labels = data.labels;
        priceChart.data.datasets[0].data = data.historical;
        priceChart.data.datasets[0].borderColor = colors.historical;
        priceChart.data.datasets[0].backgroundColor = hexToRgba(colors.historical, 0.1);

        priceChart.data.datasets[1].data = data.predicted;
        priceChart.data.datasets[1].borderColor = colors.predicted;
        priceChart.data.datasets[1].backgroundColor = hexToRgba(colors.predicted, 0.1);

        priceChart.update('active');
    }

    // ============================================
    // Alert System
    // ============================================
    function initAlerts() {
        const alertForm = document.getElementById('alert-form');
        if (alertForm) {
            alertForm.addEventListener('submit', handleAlertSubmit);
        }

        // Request notification permission and setup push
        setupPushNotifications();

        renderAlerts();
        startMockTicker();
    }

    // Push Notification Setup
    async function setupPushNotifications() {
        const statusEl = document.getElementById('notification-status');

        if (!("Notification" in window)) {
            if (statusEl) statusEl.textContent = "Not Supported";
            return;
        }

        // Request permission
        if (Notification.permission === "default") {
            await Notification.requestPermission();
        }

        if (Notification.permission === "granted") {
            if (statusEl) {
                statusEl.textContent = "Notifications Enabled";
                statusEl.className = "status-badge active";
            }

            // Register service worker and subscribe to push
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                try {
                    const registration = await navigator.serviceWorker.register('/sw.js');
                    console.log('[Push] Service Worker registered');

                    // Get VAPID public key from server
                    const vapidResponse = await fetch('/api/vapid-public-key');
                    const vapidData = await vapidResponse.json();

                    if (vapidData.success && vapidData.publicKey) {
                        // Subscribe to push
                        const subscription = await registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: urlBase64ToUint8Array(vapidData.publicKey)
                        });

                        // Send subscription to backend
                        await fetch('/api/push/subscribe', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(subscription.toJSON())
                        });

                        console.log('[Push] Subscribed successfully');
                    } else {
                        console.log('[Push] VAPID not configured on server');
                    }
                } catch (err) {
                    console.error('[Push] Setup failed:', err);
                }
            }
        } else if (Notification.permission === "denied") {
            if (statusEl) {
                statusEl.textContent = "Blocked";
                statusEl.className = "status-badge inactive";
            }
        }
    }

    // Helper: Convert VAPID key
    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    function handleAlertSubmit(e) {
        e.preventDefault();

        const symbol = document.getElementById('alert-stock-select').value;
        const high = parseFloat(document.getElementById('alert-high').value);
        const low = parseFloat(document.getElementById('alert-low').value);

        if (!high && !low) {
            alert('Please set at least one threshold (High or Low).');
            return;
        }

        const alertData = {
            symbol: symbol,
            high: high || null,
            low: low || null,
            id: Date.now()
        };

        const alerts = getAlerts();
        alerts.push(alertData);
        saveAlerts(alerts);

        renderAlerts();
        e.target.reset();
        alert(`Alert set for ${symbol}`);
    }

    function getAlerts() {
        return JSON.parse(localStorage.getItem('stockVisionAlerts') || '[]');
    }

    function saveAlerts(alerts) {
        localStorage.setItem('stockVisionAlerts', JSON.stringify(alerts));
    }

    function deleteAlert(id) {
        const alerts = getAlerts().filter(a => a.id !== id);
        saveAlerts(alerts);
        renderAlerts();
    }

    // Expose deleteAlert to global scope for button click
    window.deleteAlert = deleteAlert;

    function renderAlerts() {
        const listEl = document.getElementById('dashboard-alerts-list');
        if (!listEl) return;

        const alerts = getAlerts();

        if (alerts.length === 0) {
            listEl.innerHTML = '<p class="text-secondary">No alerts set.</p>';
            return;
        }

        listEl.innerHTML = '';
        const ul = document.createElement('ul');
        ul.style.listStyle = 'none';
        ul.style.padding = '0';

        alerts.forEach(alert => {
            const li = document.createElement('li');
            li.className = 'alert-item';
            li.style.cssText = 'padding: 10px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;';

            let text = `<strong>${alert.symbol}</strong>: `;
            if (alert.high) text += `High > ₹${alert.high} `;
            if (alert.high && alert.low) text += '| ';
            if (alert.low) text += `Low < ₹${alert.low}`;

            li.innerHTML = `
                <span>${text}</span>
                <button onclick="window.deleteAlert(${alert.id})" class="btn btn-text" style="color: var(--danger-color); padding: 0;">✕</button>
            `;
            ul.appendChild(li);
        });

        listEl.appendChild(ul);
    }

    // ============================================
    // Mock Live Ticker
    // ============================================
    function startMockTicker() {
        // Run every 5 seconds
        setInterval(() => {
            const alerts = getAlerts();
            if (alerts.length === 0) return;

            // Pick a random alert to check (simulate active market)
            const randomAlert = alerts[Math.floor(Math.random() * alerts.length)];

            // Simulate current price (around thresholds to trigger excitement)
            const basePrice = (randomAlert.high || randomAlert.low || 3000);
            // Fluctuate by 5%
            const currentPrice = basePrice + (Math.random() - 0.5) * (basePrice * 0.1);

            checkAlerts(randomAlert.symbol, currentPrice);

        }, 5000);
    }

    function checkAlerts(symbol, price) {
        const alerts = getAlerts();
        alerts.filter(a => a.symbol === symbol).forEach(alert => {
            if (alert.high && price > alert.high) {
                notifyUser(`🚀 ${symbol} crossed above ₹${alert.high}! Current: ₹${price.toFixed(2)}`);
            }
            if (alert.low && price < alert.low) {
                notifyUser(`🔻 ${symbol} dropped below ₹${alert.low}! Current: ₹${price.toFixed(2)}`);
            }
        });
    }

    function notifyUser(message) {
        // Check for recent notification to avoid spam (debounce)
        const lastNotif = sessionStorage.getItem('lastNotification');
        if (lastNotif && lastNotif === message) return; // Ignore duplicate

        sessionStorage.setItem('lastNotification', message);
        setTimeout(() => sessionStorage.removeItem('lastNotification'), 30000); // Reset after 30s

        // 1. Local browser notification (immediate)
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification("StockVision Alert", { body: message });
        }

        // 2. Trigger backend alert (SMS + Push)
        // This runs async; errors are logged to console
        fetch('/api/alert/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    console.log('[Alert] Backend trigger results:', data.results);
                } else {
                    console.warn('[Alert] Backend trigger failed:', data.error);
                }
            })
            .catch(err => console.error('[Alert] Backend trigger error:', err));

        // Fallback console log
        console.log('ALERT:', message);
    }


    // ============================================
    // Theme Update for Chart
    // ============================================
    function updateChartTheme() {
        if (!priceChart) return;

        const colors = getChartColors();

        // Update dataset colors
        priceChart.data.datasets[0].borderColor = colors.historical;
        priceChart.data.datasets[0].backgroundColor = hexToRgba(colors.historical, 0.1);
        priceChart.data.datasets[1].borderColor = colors.predicted;
        priceChart.data.datasets[1].backgroundColor = hexToRgba(colors.predicted, 0.1);

        // Update scale and legend colors
        priceChart.options.plugins.legend.labels.color = colors.text;
        priceChart.options.plugins.tooltip.backgroundColor = colors.background;
        priceChart.options.plugins.tooltip.titleColor = colors.text;
        priceChart.options.plugins.tooltip.bodyColor = colors.text;
        priceChart.options.plugins.tooltip.borderColor = colors.grid;
        priceChart.options.scales.x.grid.color = colors.grid;
        priceChart.options.scales.x.ticks.color = colors.text;
        priceChart.options.scales.y.grid.color = colors.grid;
        priceChart.options.scales.y.ticks.color = colors.text;

        priceChart.update('none');
    }

    // ============================================
    // Helper Functions
    // ============================================
    function getChartColors() {
        if (window.StockVision && window.StockVision.getChartColors) {
            return window.StockVision.getChartColors();
        }

        // Fallback colors
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        return {
            historical: isDark ? '#6366f1' : '#4f46e5',
            predicted: isDark ? '#22c55e' : '#10b981',
            grid: isDark ? '#1f2937' : '#e5e7eb',
            text: isDark ? '#9ca3af' : '#6b7280',
            background: isDark ? '#0f172a' : '#ffffff'
        };
    }

    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // ============================================
    // Initialize on DOM Ready
    // ============================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
