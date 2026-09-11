document.addEventListener("DOMContentLoaded", function () {
    const authMethodField = document.getElementById("id_authentication_method")
    const apiKeyRow = document.querySelector(".form-row.field-api_key")
    const oauth2ProviderRow = document.querySelector(".form-row.field-oauth2_provider")
    function updateFields() {
        const method = authMethodField.value

        if (method === "api_key") {
            apiKeyRow.style.display = ""
            oauth2ProviderRow.style.display = "none"
        } else if (method === "oauth2") {
            oauth2ProviderRow.style.display = ""
            apiKeyRow.style.display = "none"
        } else {
            apiKeyRow.style.display = "none"
            oauth2ProviderRow.style.display = "none"
        }
    }

    authMethodField.addEventListener("change", updateFields)
    updateFields()
})