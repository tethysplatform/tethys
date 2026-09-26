document.addEventListener('click', function(event) {
  var button = event.target.closest('[data-social-refresh-url]');
  if (!button) { return; }

  var csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (!csrf) {
    console.error('Social token refresh: CSRF token not found on page.');
    return;
  }

  var form = document.createElement('form');
  form.method = 'POST';
  form.action = button.dataset.socialRefreshUrl;

  [['csrfmiddlewaretoken', csrf.value], ['next', button.dataset.next]].forEach(function(pair) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = pair[0];
    input.value = pair[1];
    form.appendChild(input);
  });

  document.body.appendChild(form);
  form.submit();
});