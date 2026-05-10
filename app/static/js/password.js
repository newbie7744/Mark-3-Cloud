function togglePassword(fieldId) {

    const passwordField = document.getElementById(fieldId);

    if (passwordField.type === "password") {
        passwordField.type = "text";
    } 
    else {
        passwordField.type = "password";
    }

}

function validatePasswordPolicy(password) {
    if (password.length < 9) {
        return false;
    }
    const hasLowercase = /[a-z]/.test(password);
    const hasUppercase = /[A-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);

    return hasLowercase && hasUppercase && hasNumber && hasSymbol;
}

document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.querySelector(".signup-form");
    if (signupForm) {
        signupForm.addEventListener("submit", function (event) {
            const passwordField = document.getElementById("password");
            const confirmField = document.getElementById("repassword");

            if (passwordField && !validatePasswordPolicy(passwordField.value)) {
                event.preventDefault();
                alert("Password must be at least 9 characters and include lowercase, uppercase, a number, and a symbol.");
                return;
            }

            if (passwordField && confirmField && passwordField.value !== confirmField.value) {
                event.preventDefault();
                alert("Passwords do not match.");
            }
        });
    }
});