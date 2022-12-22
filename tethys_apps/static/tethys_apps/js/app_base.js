/*****************************************************************************
 * FILE:      app_base.js
 * DATE:      6 September 2014
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) Brigham Young University 2014
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_APP_BASE = (function () {
  // Wrap the library in a package function
  "use strict"; // And enable strict mode for this library

  /************************************************************************
   *                      MODULE LEVEL / GLOBAL VARIABLES
   *************************************************************************/
  var public_interface, // The public interface object that is returned by the module
    apps_library_url, // The relative url of the apps library page
    app_header_selector, // String selector for the app header element
    app_content_selector, // String selector for the app content element
    wrapper_selector, // String selector for the app wrapper element
    toggle_nav_selector, // String selector for the toggle nav element
    app_navigation_selector, // String selector for the app navigation element
    tethys_nav_cookie_key, // Key for the tethys apps nav cookie
    nav_in_value, // Value of the nav cookie when nav is in
    nav_out_value, // Value of the nav cookie when nav is out
    nav_disabled; // True when the nav is disabled

  /************************************************************************
   *                    PRIVATE FUNCTION DECLARATIONS
   *************************************************************************/
  var app_entry_handler,
    check_responsive,
    no_nav_handler,
    exit_app,
    toggle_nav,
    csrf_safe_method,
    alert;

  /************************************************************************
   *                    PRIVATE FUNCTION IMPLEMENTATIONS
   *************************************************************************/

  // Create an alert message via JavaScript API
  alert = function(style, message) {
    // Validate
    const validStyles = [
      "primary", "secondary", "info", "success",
      "warning", "danger", "light", "dark"
    ];
    if (!validStyles.includes(style)) {
      console.log(`Invaid alert style: "${style}". Must be one of: "${validStyles.join('", "')}".`);
      return;
    }

    if (!message) {
      console.log('The "message" parameter is required for alert.');
      return;
    }

    // Find or create flash messages div
    let flashMessages = document.querySelector('.flash-messages');
    if (!flashMessages) {
      flashMessages = document.createElement('div');
      flashMessages.classList.add('flash-messages');
      document.body.appendChild(flashMessages);
    }

    // Build bootstrap-style alert
    let alert = document.createElement('div');
    flashMessages.appendChild(alert);
    alert.classList.add(
      "alert", `alert-${style}`, "alert-dismissible",
      "fade", "show", "mx-auto"
    );
    alert.innerText = message;

    // Add the close button
    let closeButton = document.createElement("button");
    alert.appendChild(closeButton);
    closeButton.classList.add("btn-close");
    closeButton.setAttribute("type", "button");
    closeButton.setAttribute("data-bs-dismiss", "alert");
    closeButton.setAttribute("aria-label", "close");

    return alert;
  };

  // Handle toggling nav effects
  toggle_nav = function () {
    // Add the with-transition class if not present
    if (!$(wrapper_selector).hasClass("with-transition")) {
      $(wrapper_selector).addClass("with-transition");
    }

    // Toggle the show-nav class
    if ($(wrapper_selector).hasClass("show-nav")) {
      // Do things on Nav Close
      $(wrapper_selector).removeClass("show-nav");

      // Toggle cookie
      docCookies.setItem(
        tethys_nav_cookie_key,
        nav_out_value,
        null,
        apps_library_url
      );
      $(toggle_nav_selector).trigger("tethys:hide-nav");
    } else {
      // Do thing on Nav Open
      $(wrapper_selector).addClass("show-nav");

      // Toggle cookie
      docCookies.setItem(
        tethys_nav_cookie_key,
        nav_in_value,
        null,
        apps_library_url
      );
      $(toggle_nav_selector).trigger("tethys:show-nav");
    }

    $(toggle_nav_selector).trigger("tethys:toggle-nav");
  };

  // Handle the entry entry transitions in the app
  app_entry_handler = function () {
    // Declare vars
    var referrer_no_protocol, referrer_no_host;

    // Get the referrer url and strip off protocol
    referrer_no_protocol = document.referrer.split("//")[1];

    // Check if referrer exists and it contains our host
    if (
      referrer_no_protocol &&
      referrer_no_protocol.indexOf(location.host) > -1
    ) {
      referrer_no_host = referrer_no_protocol.replace(location.host, "");

      // If the referrer was the app library, add transition classes to create a
      // smooth transition effect on app launch
      if (referrer_no_host === apps_library_url) {
        // Enable the transitions
        $(app_header_selector).addClass("with-transition");
        $(app_content_selector).addClass("with-transition");

        // Remove the nav cookie
        docCookies.removeItem(tethys_nav_cookie_key, apps_library_url);
      }
    }

    // Add the "show" classes appropriately to show things that are hidden by default
    $(app_header_selector).addClass("show-header");
    $(app_content_selector).addClass("show-app-content");

    // Check the nav cookie
    if (docCookies.hasItem(tethys_nav_cookie_key)) {
      var nav_cookie_value;

      // Read the cookie
      nav_cookie_value = docCookies.getItem(tethys_nav_cookie_key);

      if (nav_cookie_value == nav_out_value) {
        $(wrapper_selector).removeClass("show-nav");
      } else if (nav_cookie_value == nav_in_value && !nav_disabled) {
        $(wrapper_selector).addClass("show-nav");
      }
    }
  };

  // Handle case when there is no nav present
  no_nav_handler = function () {
    // If no nav present...
    if (!$(app_navigation_selector).length) {
      nav_disabled = true;

      // Hide the nav area
      $("#app-content").css("transition", "none");
      $(wrapper_selector).removeClass("show-nav");

      // Hide the toggle button and then remove it
      $(toggle_nav_selector).css("display", "none");
      $(toggle_nav_selector).remove();
    }
  };

  // Check for responsive parameters
  check_responsive = function () {
    var window_width;

    window_width = window.innerWidth;

    // Hide the nav if less than threshold
    if (window_width < 900 && $(wrapper_selector).hasClass("show-nav")) {
      $(wrapper_selector).removeClass("show-nav");
      docCookies.setItem(
        tethys_nav_cookie_key,
        nav_out_value,
        null,
        apps_library_url
      );
    }
  };

  // Apply transition effect to exit button press
  exit_app = function (url) {
    var redirect_delay;
    var url_params = new URLSearchParams(window.location.search);
    var back_url = url_params.get("back");

    redirect_delay = 400; // milliseconds

    setTimeout(function () {
      // Remove the nav cookie
      docCookies.removeItem(tethys_nav_cookie_key, apps_library_url);

      // Redirect to app home page
      window.location = !back_url ? url : back_url;
    }, redirect_delay);

    // Add transition classes if necessary
    if (!$(app_header_selector).hasClass("with-transition")) {
      $(app_header_selector).addClass("with-transition");
    }

    if (!$(app_content_selector).hasClass("with-transition")) {
      $(app_content_selector).addClass("with-transition");
    }

    // Hide tooltips
    $('[data-bs-toggle="tooltip"]').tooltip("hide");

    // Dismiss alerts
    $(".alert").alert("close");

    // Hide by removing "show" classes
    $(app_header_selector).removeClass("show-header");
    $(app_content_selector).removeClass("show-app-content");
  };

  csrf_safe_method = function (method) {
    // these HTTP methods do not require CSRF protection
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  };

  /************************************************************************
   *                        DEFINE PUBLIC INTERFACE
   *************************************************************************/
  /*
   * Library object that contains public facing functions of the package.
   * This is the object that is returned by the library wrapper function.
   * See below.
   * NOTE: The functions in the public interface have access to the private
   * functions of the library because of JavaScript function scope.
   */
  public_interface = {
    toggle_nav: toggle_nav,
    exit_app: exit_app,
    alert: alert,
  };

  /************************************************************************
   *                  INITIALIZATION / CONSTRUCTOR
   *************************************************************************/

  //add function changeSize to jQuery prototype
  //this is used for the map view but available for all jQuery elements
  $.fn.changeSize = function (fn) {
    var $this = this,
      w0 = $this.width(),
      h0 = $this.height(),
      pause = false,
      callback, //callback function after handle is called
      handler; //function to handle action

    callback = function () {
      pause = false;
      w0 = $this.width();
      h0 = $this.height();
    };
    handler = function () {
      fn($this);
      callback();
    };

    $this.sizeTO = setInterval(function () {
      if (!pause) {
        var w1 = $this.width();
        var h1 = $this.height();
        if (w1 != w0 || h1 != h0) {
          pause = true;
          handler();
        }
      }
    }, 100);
  };

  /*****************************************************************************
   *
   * Cross Site Request Forgery Token Configuration
   *   copied from (https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/)
   *
   *****************************************************************************/

  var csrftoken = document.querySelector("[name=csrfmiddlewaretoken]");
  if (csrftoken) {
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!csrf_safe_method(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken.value);
        }
      },
    });
  }

  // Initialization: jQuery function that gets called when
  // the DOM tree finishes loading
  $(function () {
    // Selector globals
    apps_library_url = "/apps/";
    app_header_selector = ".tethys-app-header";
    app_content_selector = "#app-content";
    wrapper_selector = "#app-content-wrapper";
    toggle_nav_selector = ".toggle-nav";
    app_navigation_selector = "#app-navigation";
    nav_disabled = false;

    // Cookie globals
    tethys_nav_cookie_key = "tethysappnav";
    nav_in_value = "a7dfd75f8f41f038258effc6d975cef7";
    nav_out_value = "3f64a50b313be90cc612d9a0a1debf30";

    // Bind toggle_nav to the click event of ".toggle-nav" element
    $(toggle_nav_selector).click(function () {
      public_interface.toggle_nav();
    });

    // Bind to the window resize event
    window.onresize = function () {
      check_responsive();
    };

    // Run no nav handler
    no_nav_handler();

    // Run the app entry handler
    app_entry_handler();

    // Perform responsive check
    check_responsive();

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip({ container: "body" });
  });

  return public_interface;
})(); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed, returning the public interface object.

// Global Functions for App Util
