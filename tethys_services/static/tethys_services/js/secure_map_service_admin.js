document.addEventListener("DOMContentLoaded", function () {
    const authMethodField = document.getElementById("id_authentication_method")
    const apiKeyRow = document.querySelector(".form-row.field-api_key")
    const oauthProviderRow = document.querySelector(".form-row.field-oauth_provider")
    function updateFields() {
        const method = authMethodField.value

        if (method === "api_key") {
            apiKeyRow.style.display = ""
            oauthProviderRow.style.display = "none"
        } else if (method === "oauth") {
            oauthProviderRow.style.display = ""
            apiKeyRow.style.display = "none"
        } else {
            apiKeyRow.style.display = "none"
            oauthProviderRow.style.display = "none"
        }
    }

    authMethodField.addEventListener("change", updateFields)
    updateFields()
})