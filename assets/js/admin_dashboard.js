/* ============================================
   StockVision - Admin Dashboard JavaScript
   Charts & User Management Functions
   ============================================ */

(function () {
    'use strict';

    let predictionsChart = null;
    let modelUsageChart = null;
    let signupsChart = null;

    // ============================================
    // Initialize Dashboard
    // ============================================
    function init() {
        initPredictionsPerDayChart();
        initModelUsageChart();
        initSignupsChart();

        // Listen for theme changes
        window.addEventListener('themechange', updateAllChartsTheme);
    }

    // ============================================
    // Predictions Per Day Chart
    // ============================================
    function initPredictionsPerDayChart() {
        const ctx = document.getElementById('adminPredictionsPerDay');
        if (!ctx) return;

        const colors = getChartColors();
        const data = generatePredictionsData();

        predictionsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Predictions',
                    data: data.values,
                    backgroundColor: hexToRgba(colors.historical, 0.7),
                    borderColor: colors.historical,
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: colors.background,
                        titleColor: colors.text,
                        bodyColor: colors.text,
                        borderColor: colors.grid,
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: colors.text }
                    },
                    y: {
                        grid: { color: colors.grid, drawBorder: false },
                        ticks: { color: colors.text },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function generatePredictionsData() {
        const labels = [];
        const values = [];
        const today = new Date();

        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            labels.push(date.toLocaleDateString('en-IN', { weekday: 'short' }));
            values.push(Math.floor(Math.random() * 50) + 10);
        }

        return { labels, values };
    }

    // ============================================
    // Model Usage Chart (Pie)
    // ============================================
    function initModelUsageChart() {
        const ctx = document.getElementById('adminModelUsage');
        if (!ctx) return;

        const colors = getChartColors();

        modelUsageChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Linear Regression', 'LSTM', 'Both'],
                datasets: [{
                    data: [45, 35, 20],
                    backgroundColor: [
                        hexToRgba(colors.historical, 0.8),
                        hexToRgba(colors.predicted, 0.8),
                        hexToRgba('#f97316', 0.8)
                    ],
                    borderColor: colors.background,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
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
                        borderWidth: 1
                    }
                },
                cutout: '60%'
            }
        });
    }

    // ============================================
    // User Signups Chart
    // ============================================
    function initSignupsChart() {
        const ctx = document.getElementById('adminSignups');
        if (!ctx) return;

        const colors = getChartColors();
        const data = generateSignupsData();

        signupsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'New Users',
                    data: data.values,
                    borderColor: colors.predicted,
                    backgroundColor: hexToRgba(colors.predicted, 0.1),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: colors.predicted,
                    pointBorderColor: colors.background,
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: colors.background,
                        titleColor: colors.text,
                        bodyColor: colors.text,
                        borderColor: colors.grid,
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: colors.text }
                    },
                    y: {
                        grid: { color: colors.grid, drawBorder: false },
                        ticks: { color: colors.text },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function generateSignupsData() {
        const labels = [];
        const values = [];
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const currentMonth = new Date().getMonth();

        for (let i = 5; i >= 0; i--) {
            const monthIdx = (currentMonth - i + 12) % 12;
            labels.push(months[monthIdx]);
            values.push(Math.floor(Math.random() * 30) + 5);
        }

        return { labels, values };
    }

    // ============================================
    // Update All Charts on Theme Change
    // ============================================
    function updateAllChartsTheme() {
        const colors = getChartColors();

        if (predictionsChart) {
            predictionsChart.data.datasets[0].backgroundColor = hexToRgba(colors.historical, 0.7);
            predictionsChart.data.datasets[0].borderColor = colors.historical;
            predictionsChart.options.plugins.tooltip.backgroundColor = colors.background;
            predictionsChart.options.plugins.tooltip.titleColor = colors.text;
            predictionsChart.options.plugins.tooltip.bodyColor = colors.text;
            predictionsChart.options.plugins.tooltip.borderColor = colors.grid;
            predictionsChart.options.scales.x.ticks.color = colors.text;
            predictionsChart.options.scales.y.grid.color = colors.grid;
            predictionsChart.options.scales.y.ticks.color = colors.text;
            predictionsChart.update('none');
        }

        if (modelUsageChart) {
            modelUsageChart.data.datasets[0].backgroundColor = [
                hexToRgba(colors.historical, 0.8),
                hexToRgba(colors.predicted, 0.8),
                hexToRgba('#f97316', 0.8)
            ];
            modelUsageChart.data.datasets[0].borderColor = colors.background;
            modelUsageChart.options.plugins.legend.labels.color = colors.text;
            modelUsageChart.options.plugins.tooltip.backgroundColor = colors.background;
            modelUsageChart.options.plugins.tooltip.titleColor = colors.text;
            modelUsageChart.options.plugins.tooltip.bodyColor = colors.text;
            modelUsageChart.options.plugins.tooltip.borderColor = colors.grid;
            modelUsageChart.update('none');
        }

        if (signupsChart) {
            signupsChart.data.datasets[0].borderColor = colors.predicted;
            signupsChart.data.datasets[0].backgroundColor = hexToRgba(colors.predicted, 0.1);
            signupsChart.data.datasets[0].pointBackgroundColor = colors.predicted;
            signupsChart.data.datasets[0].pointBorderColor = colors.background;
            signupsChart.options.plugins.tooltip.backgroundColor = colors.background;
            signupsChart.options.plugins.tooltip.titleColor = colors.text;
            signupsChart.options.plugins.tooltip.bodyColor = colors.text;
            signupsChart.options.plugins.tooltip.borderColor = colors.grid;
            signupsChart.options.scales.x.ticks.color = colors.text;
            signupsChart.options.scales.y.grid.color = colors.grid;
            signupsChart.options.scales.y.ticks.color = colors.text;
            signupsChart.update('none');
        }
    }

    // ============================================
    // Helper Functions
    // ============================================
    function getChartColors() {
        if (window.StockVision && window.StockVision.getChartColors) {
            return window.StockVision.getChartColors();
        }

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
    // User Management Functions (Stubs)
    // ============================================
    window.changeUserRole = function (userId) {
        console.log('changeUserRole called for user ID:', userId);

        // TODO: Replace with actual API call
        // fetch(`/api/admin/users/${userId}/role`, {
        //   method: 'PUT',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ role: 'admin' })
        // })
        // .then(response => response.json())
        // .then(data => { ... });

        alert(`Role change requested for user ID: ${userId}\n(Backend integration pending)`);
    };

    window.deactivateUser = function (userId) {
        console.log('deactivateUser called for user ID:', userId);

        // TODO: Replace with actual API call
        // fetch(`/api/admin/users/${userId}/deactivate`, {
        //   method: 'PUT'
        // })
        // .then(response => response.json())
        // .then(data => { ... });

        alert(`Deactivation requested for user ID: ${userId}\n(Backend integration pending)`);
    };

    window.activateUser = function (userId) {
        console.log('activateUser called for user ID:', userId);

        // TODO: Replace with actual API call
        // fetch(`/api/admin/users/${userId}/activate`, {
        //   method: 'PUT'
        // })
        // .then(response => response.json())
        // .then(data => { ... });

        alert(`Activation requested for user ID: ${userId}\n(Backend integration pending)`);
    };

    // ============================================
    // Initialize on DOM Ready
    // ============================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
