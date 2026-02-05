// attendance.js - Attendance marking functionality
document.addEventListener('DOMContentLoaded', function() {
    const attendanceSelects = document.querySelectorAll('.attendance-status');
    
    attendanceSelects.forEach(select => {
        // Set initial color
        updateRowColor(select);
        
        // Update color on change
        select.addEventListener('change', function() {
            updateRowColor(this);
        });
    });

    // Mark all present button
    const markAllPresentBtn = document.getElementById('mark-all-present');
    if (markAllPresentBtn) {
        markAllPresentBtn.addEventListener('click', function() {
            attendanceSelects.forEach(select => {
                select.value = 'present';
                updateRowColor(select);
            });
        });
    }

    // Mark all absent button
    const markAllAbsentBtn = document.getElementById('mark-all-absent');
    if (markAllAbsentBtn) {
        markAllAbsentBtn.addEventListener('click', function() {
            attendanceSelects.forEach(select => {
                select.value = 'absent';
                updateRowColor(select);
            });
        });
    }

    // Select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-students');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.student-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
});

function updateRowColor(selectElement) {
    const row = selectElement.closest('tr');
    const status = selectElement.value;
    
    // Remove all status classes
    row.classList.remove('table-success', 'table-danger', 'table-warning', 'table-info');
    
    // Add appropriate class
    switch(status) {
        case 'present':
            row.classList.add('table-success');
            break;
        case 'absent':
            row.classList.add('table-danger');
            break;
        case 'late':
            row.classList.add('table-warning');
            break;
        case 'excused':
            row.classList.add('table-info');
            break;
    }
}
