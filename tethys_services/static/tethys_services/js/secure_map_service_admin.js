document.addEventListener("DOMContentLoaded", function () {
    const authMethodField = document.getElementById("id_authentication_method")
    const apiKeyRow = document.querySelector(".form-row.field-api_key")
    const oauthProviderRow = document.querySelector(".form-row.field-oauth_provider")
    function updateFields() {
        const method = authMethodField.value

        if (method === "api_key") {
            console.log("API Key authentication selected")
            apiKeyRow.style.display = ""
            oauthProviderRow.style.display = "none"
        } else if (method === "oauth") {
            console.log("OAuth authentication selected")
            oauthProviderRow.style.display = ""
            apiKeyRow.style.display = "none"
        } else {
            console.log("No authentication selected")
            apiKeyRow.style.display = "none"
            oauthProviderRow.style.display = "none"
        }
    }

    authMethodField.addEventListener("change", updateFields)
    updateFields()
})