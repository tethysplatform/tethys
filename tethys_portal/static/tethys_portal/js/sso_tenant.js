$(function() {
  if (window.localStorage) {
    // Show the hidden remember checkbox only if local storage is supported
    $('label[for="id_remember"]').css('display', 'block');

    // Check local storage for saved data
    let backend = $('#backend').val();
    let remember_key = `${backend}-remember`;
    let tenant_key = `${backend}-tenant`;
    let remember = localStorage.getItem(remember_key);
    let tenant = localStorage.getItem(tenant_key);
    console.log(backend);
    console.log(remember_key);
    console.log(tenant_key);

    // Set remember field with saved value
    if (remember != null) {
      if (remember == 'true') {
        $('#id_remember').prop('checked', true);
      } else {
        $('#id_remember').prop('checked', false);
      }
    }

    // Set tenant field with saved value
    if (tenant != null) {
      $('#id_tenant').val(tenant);
    }
    // Bind to form submit
    $('#sso-tenant-form').on('submit', function(evt) {
      if ($('#id_remember').is(":checked")) {
        // Save form data
        let tenant = $('#id_tenant').val();
        localStorage.setItem(remember_key, 'true');
        localStorage.setItem(tenant_key, tenant);
      } else {
        // Clear saved form data
        localStorage.removeItem(remember_key);
        localStorage.removeItem(tenant_key);
      }
    });
  }
});