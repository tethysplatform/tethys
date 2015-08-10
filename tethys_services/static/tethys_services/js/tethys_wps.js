/*****************************************************************************
 * FILE: tethys_wps.js
 * DATE: 2014
 * AUTHOR: Nathan Swain
 * COPYRIGHT: (c) Brigham Young University 2014
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

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