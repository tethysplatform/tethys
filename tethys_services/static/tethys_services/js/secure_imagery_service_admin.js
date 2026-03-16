console.log("Secure Imagery Service Admin JS Loaded");document.addEventListener("DOMContentLoaded", function () {
    const authMethodField = document.getElementById("id_authentication_method")
    const apiKeyRow = document.querySelector(".form-row.field-api_key")
    const authKeyRow = document.querySelector(".form-row.field-authentication_key")

    function updateFields() {
        const method = authMethodField.value

        if (method === "api_key") {
            apiKeyRow.style.display = ""
            authKeyRow.style.display = "none"
        } else if (method === "oauth") {
            apiKeyRow.style.display = "none"
            authKeyRow.style.display = ""
        } else {
            apiKeyRow.style.display = "none"
            authKeyRow.style.display = "none"
        }
    }

    authMethodField.addEventListener("change", updateFields)
    updateFields()
})