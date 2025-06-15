document.addEventListener('DOMContentLoaded', function() {
    // Date validation
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.max = today;
        dateInput.value = today;
    }

    // Chart initialization
    try {
        const ctx = document.getElementById('expenseChart');
        if (!ctx) return;

        const dataContainer = document.getElementById('chart-data');
        if (!dataContainer) {
            ctx.insertAdjacentHTML('afterend', '<div class="alert alert-warning">Chart data container missing</div>');
            return;
        }

        const categoryNames = JSON.parse(dataContainer.dataset.names || '[]');
        const categoryTotals = JSON.parse(dataContainer.dataset.totals || '[]');

        if (categoryNames.length === 0) {
            ctx.insertAdjacentHTML('afterend', '<div class="alert alert-info">No expense data available for chart</div>');
            return;
        }

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categoryNames,
                datasets: [{
                    data: categoryTotals,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56',
                        '#4BC0C0', '#9966FF', '#FF9F40',
                        '#8AC24A', '#FF5722', '#607D8B'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ₹${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error("Chart error:", error);
        const chartContainer = document.querySelector('.chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="alert alert-danger">
                    Error loading chart: ${error.message}
                    <br><small>Check console for details</small>
                </div>
            `;
        }
    }
});