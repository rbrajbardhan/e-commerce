// ===============================
// BOOTSTRAP INITIALIZATION
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

});


// ===============================
// BASIC FORM VALIDATION
// ===============================

document.addEventListener("submit", function (e) {

    const requiredFields = e.target.querySelectorAll("[required]");
    let valid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add("is-invalid");
            valid = false;
        } else {
            field.classList.remove("is-invalid");
        }
    });

    if (!valid) {
        e.preventDefault();
        alert("Please fill in all required fields.");
    }
});


// ===============================
//  AUTO UPDATE CART QUANTITY
// ===============================

document.addEventListener("change", function (e) {

    if (e.target.name === "quantity") {
        const form = e.target.closest("form");
        if (form) {
            form.submit();
        }
    }

});
