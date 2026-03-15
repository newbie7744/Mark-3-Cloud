function togglePassword(fieldId) {

    const passwordField = document.getElementById(fieldId);

    if (passwordField.type === "password") {
        passwordField.type = "text";
    } 
    else {
        passwordField.type = "password";
    }

}