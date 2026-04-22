// Expense Tracker v2 - script.js

document.addEventListener('DOMContentLoaded', function () {

    // 1. Animate bar chart fills on load
    const bars = document.querySelectorAll('.bar-fill');
    bars.forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = target; }, 100);
    });

    // 2. Confirm before deleting
    const deleteLinks = document.querySelectorAll('.btn-delete');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            if (!confirm('Delete this expense?')) {
                e.preventDefault();
            }
        });
    });

    // 3. Auto-focus amount field
    const amountInput = document.querySelector('input[name="amount"]');
    if (amountInput) amountInput.focus();

});
