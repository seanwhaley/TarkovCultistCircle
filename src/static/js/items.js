document.addEventListener('DOMContentLoaded', function() {
    const validatePrice = (price) => {
        const parsed = parseFloat(price);
        return !isNaN(parsed) && parsed > 0;
    };

    const validateDuration = (duration) => {
        const parsed = parseInt(duration);
        return !isNaN(parsed) && parsed > 0;
    };

    const showError = (element, message) => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        element.classList.add('is-invalid');
        element.parentNode.appendChild(errorDiv);
    };

    const clearErrors = (form) => {
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    };

    // Price Override Modal
    document.querySelectorAll('.price-override-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            document.querySelector('#priceModal input[name="item_id"]').value = itemId;
        });
    });

    // Price Override Form Validation
    document.querySelector('#priceOverrideForm').addEventListener('submit', function(e) {
        e.preventDefault();
        clearErrors(this);
        
        const price = this.querySelector('input[name="price"]').value;
        if (!validatePrice(price)) {
            showError(this.querySelector('input[name="price"]'), 'Please enter a valid price greater than 0');
            return;
        }
        
        this.submit();
    });

    // Duration Form Validation (both lock and blacklist)
    ['lockForm', 'blacklistForm'].forEach(formId => {
        document.querySelector(`#${formId}`).addEventListener('submit', function(e) {
            e.preventDefault();
            clearErrors(this);
            
            const duration = this.querySelector('input[name="duration"]').value;
            if (!validateDuration(duration)) {
                showError(this.querySelector('input[name="duration"]'), 'Please enter a valid duration in hours');
                return;
            }
            
            this.submit();
        });
    });

    // Initialize DataTable
    $('#itemsTable').DataTable({
        order: [[0, 'asc']],
        pageLength: 25,
        responsive: true
    });
});
