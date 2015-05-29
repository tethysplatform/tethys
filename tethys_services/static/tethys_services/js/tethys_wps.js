function dynamic_search(value) {
  console.log(value);

  $(".list-group-item.process").each(function () {
      if ($(this).text().search(new RegExp(value, "i")) < 0) {
          $(this).hide();
      } else {
          $(this).show()
      }
  });
}