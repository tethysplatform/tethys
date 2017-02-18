/*****************************************************************************
 * FILE:    Tethys Map View Layout
 * DATE:    January 17, 2017
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) Tethys Platform 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_MAP_VIEW_LAYOUT = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var m_public_interface;				// Object returned by the module

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// CSRF Management Methods
 	var csrf_safe_method, get_cookie;

 	// Event handler methods
 	var handle_save;

 	// UI methods
 	var resize_map;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
 	// CSRF Management Methods
 	csrf_safe_method = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

 	get_cookie = function(name) {
        var cookie_value = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookie_value;
    };

    // Event handler methods
    handle_save = function() {
        var geometry, csrf_token;

        // Get the JSON from the hidden field
        geometry = $('#map_view_geometry').val();

        // Handle CSRF protection
        csrf_token = get_cookie('csrftoken');

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrf_safe_method(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            }
        });

        // Setup AJAX
        $.ajax({
            'method': 'post',
            'data': {
                'event': 'on-save',
                'geometry': geometry
            },
        }).done(function(data) {
            if (!'success' in data || data.success === false) {
                console.error('Map View Template: Unsuccessful Save');
            }
        });
    };

    // UI methods
 	resize_map = function() {
 	    var header_height = $('.tethys-app-header').height(),
 	        window_height = $(window).height();
 	    $('#app-content, #inner-app-content').css('max-height', window_height - header_height);
 		$('#map_wrapper').css({
            'height': $('#app-content').height(),
            'max-height': $('#app-content').height(),
            'width': '100%',
        });
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
	m_public_interface = {};

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/
	$(function() {

	    // Bind to events
        $(window).resize(function() {
            resize_map();
        });

        // Save event
        $('#save-btn').click(handle_save);

        // Initialize map
        resize_map();
	});

	return m_public_interface;

}()); // End of package wrapper