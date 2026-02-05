// dashboard.js - Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Refresh dashboard button
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }

    // Update today's date display
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = today.toLocaleDateString('en-US', options);
    
    const dateElement = document.getElementById('today-date');
    if (dateElement) {
        dateElement.textContent = dateString;
    }

    // Make stats cards clickable
    document.querySelectorAll('.stats-card[data-target]').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            window.location.href = this.dataset.target;
        });
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.2s';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Calculate attendance percentage
    updateAttendancePercentage();
});

function updateAttendancePercentage() {
    const presentElement = document.querySelector('[data-stat="present"]');
    const totalElement = document.querySelector('[data-stat="total"]');
    
    if (presentElement && totalElement) {
        const present = parseInt(presentElement.textContent) || 0;
        const total = parseInt(totalElement.textContent) || 1;
        const percentage = Math.round((present / total) * 100);
        
        const percentageElement = document.getElementById('attendance-percentage');
        if (percentageElement) {
            // percentageElement.textContent = \\%\;
            
            // Update progress bar
            const progressBar = percentageElement.closest('.progress-bar');
            if (progressBar) {
                // progressBar.style.width = \\%\;
                
                // Update color based on percentage
                if (percentage >= 80) {
                    progressBar.classList.remove('bg-warning', 'bg-danger');
                    progressBar.classList.add('bg-success');
                } else if (percentage >= 60) {
                    progressBar.classList.remove('bg-success', 'bg-danger');
                    progressBar.classList.add('bg-warning');
                } else {
                    progressBar.classList.remove('bg-success', 'bg-warning');
                    progressBar.classList.add('bg-danger');
                }
            }
        }
    }
}
