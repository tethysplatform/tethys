document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('[data-social-refresh-url]').forEach(function(button) {
    button.addEventListener('click', function() {
      var token = get_csrf_token() || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
      if (!token) {
        console.error('Social token refresh: CSRF token not found on page.');
        return;
      }

      var form = document.createElement('form');
      form.method = 'POST';
      form.action = button.dataset.socialRefreshUrl;

      [['csrfmiddlewaretoken', token], ['next', button.dataset.next]].forEach(function(pair) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = pair[0];
        input.value = pair[1];
        form.appendChild(input);
      });

      document.body.appendChild(form);
      form.submit();
    });
  });
});