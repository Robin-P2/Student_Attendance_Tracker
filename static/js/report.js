// reports.js - Reports and chart functionality

document.addEventListener('DOMContentLoaded', function() {
    // Only run on reports pages
    if (!document.querySelector('.reports-page')) return;

    console.log('Reports page loaded');

    initializeReportsPage();
    initializeCharts();
    handleReportFilters();
    handleExportButtons();
});

function initializeReportsPage() {
    // Initialize date range picker
    const dateRangeInput = document.getElementById('date-range');
    if (dateRangeInput) {
        dateRangeInput.addEventListener('change', updateDateRange);
    }

    // Initialize class filter
    const classFilter = document.getElementById('class-filter');
    if (classFilter) {
        classFilter.addEventListener('change', filterByClass);
    }

    // Initialize search
    const searchInput = document.getElementById('report-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchReports, 300));
    }
}

function updateDateRange() {
    const value = this.value;
    const [start, end] = value.split(' to ');

    // Update hidden inputs or submit form
    const startInput = document.getElementById('start_date');
    const endInput = document.getElementById('end_date');

    if (startInput && endInput) {
        startInput.value = start;
        endInput.value = end;
        this.closest('form').submit();
    }
}

function filterByClass() {
    const selectedClass = this.value;
    const rows = document.querySelectorAll('.student-row');

    rows.forEach(row => {
        const studentClass = row.dataset.class;
        if (!selectedClass || studentClass === selectedClass) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function searchReports() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('.student-row');

    rows.forEach(row => {
        const studentName = row.dataset.name.toLowerCase();
        const studentId = row.dataset.id.toLowerCase();

        if (studentName.includes(searchTerm) || studentId.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function initializeCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }

    // Attendance Overview Chart
    const overviewCtx = document.getElementById('attendanceOverviewChart');
    if (overviewCtx) {
        const overviewChart = new Chart(overviewCtx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Late', 'Excused'],
                datasets: [{
                    data: overviewCtx.dataset.present ? [
                        parseInt(overviewCtx.dataset.present),
                        parseInt(overviewCtx.dataset.absent),
                        parseInt(overviewCtx.dataset.late),
                        parseInt(overviewCtx.dataset.excused)
                    ] : [75, 15, 5, 5],
                    backgroundColor: [
                        '#28a745', // Green
                        '#dc3545', // Red
                        '#ffc107', // Yellow
                        '#17a2b8'  // Blue
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Monthly Trend Chart
    const trendCtx = document.getElementById('monthlyTrendChart');
    if (trendCtx && trendCtx.dataset.labels) {
        const labels = JSON.parse(trendCtx.dataset.labels);
        const presentData = JSON.parse(trendCtx.dataset.present || '[]');
        const absentData = JSON.parse(trendCtx.dataset.absent || '[]');

        const trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Present',
                        data: presentData,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Absent',
                        data: absentData,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    }
                }
            }
        });
    }

    // Class-wise Attendance Chart
    const classCtx = document.getElementById('classWiseChart');
    if (classCtx && classCtx.dataset.labels) {
        const classLabels = JSON.parse(classCtx.dataset.labels);
        const classPercentages = JSON.parse(classCtx.dataset.percentages || '[]');

        const classChart = new Chart(classCtx, {
            type: 'bar',
            data: {
                labels: classLabels,
                datasets: [{
                    label: 'Attendance Percentage',
                    data: classPercentages,
                    backgroundColor: classPercentages.map(p => {
                        if (p >= 80) return '#28a745';
                        if (p >= 60) return '#ffc107';
                        return '#dc3545';
                    }),
                    borderColor: '#495057',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Attendance %'
                        }
                    }
                }
            }
        });
    }
}

function handleReportFilters() {
    const filterForm = document.getElementById('report-filter-form');
    if (filterForm) {
        // Auto-submit on filter change
        filterForm.querySelectorAll('.filter-change-submit').forEach(element => {
            element.addEventListener('change', function() {
                filterForm.submit();
            });
        });

        // Reset filters
        const resetBtn = document.getElementById('reset-filters');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                filterForm.reset();
                filterForm.submit();
            });
        }
    }
}

function handleExportButtons() {
    // CSV Export
    const csvExportBtn = document.getElementById('export-csv');
    if (csvExportBtn) {
        csvExportBtn.addEventListener('click', function() {
            showNotification('Preparing CSV download...', 'info');
        });
    }

    // Print Report
    const printBtn = document.getElementById('print-report');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for testing
window.Reports = {
    initializeCharts,
    filterByClass,
    searchReports
};