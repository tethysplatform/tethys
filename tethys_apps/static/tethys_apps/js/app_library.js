/*****************************************************************************
 * FILE:      app_library.js
 * DATE:      6 September 2014
 * AUTHOR:    Nathan Swain
 * COPYRIGHT: (c) Brigham Young University 2014
 * LICENSE:   BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_APPS_LIBRARY = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface;   // The public interface object that is returned by the module

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var filter_apps;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/

 	filter_apps = function(e) {
		let selected_tags = $(e.target).select2('data');

		$('.app-card-container').each(function(index, app_container) {
			// If no selected tags, show all apps
			if (selected_tags.length <= 0) {
				$(app_container).parent('.col').removeClass('d-none');
				return;
			}
			
			// Hide apps with no tags
			let app_tags_str = $(app_container).data('tags');
			console.log('app_tags_str:');
			console.log(app_tags_str);
			if (app_tags_str.length <= 0) {
				$(app_container).parent('.col').addClass('d-none');
				console.log('No tags, hiding app and moving on!')
				return;
			}

			// Discover which apps have at least one of the selected tags
			let app_tags_arr = app_tags_str.split(" ");
			let has_at_least_one_tag = false;
			for (let selected_tag of selected_tags) {
				if (app_tags_arr.includes(selected_tag.id)) {
					has_at_least_one_tag = true;
					break;
				}
			}

			// Hide apps that have at least one matching tag and show apps that do
			if (has_at_least_one_tag) {
				$(app_container).parent('.col').removeClass('d-none');
			} else {
				$(app_container).parent('.col').addClass('d-none');
			}
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
	public_interface = {};

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
	    // Add a contains method to the String prototype
	    if ( !String.prototype.contains ) {
            String.prototype.contains = function() {
                return String.prototype.indexOf.apply( this, arguments ) !== -1;
            };
        }

		// Display help info icon on hover of the app tile
		$('.app-card-container').each(function() {
			let card_container = this;
			let help_icon = $(card_container).children('.app-help-icon, .app-settings-icon');

			if (help_icon.length) {
				$(card_container).hover(
					function() {
						help_icon.removeClass('d-none');
					}, 
					function() {
						help_icon.addClass('d-none');
					}
				);
			}
		});

		// Apply help-icon click event 
		$('.app-help-icon').each(function() {
			let info_icon = this;
			let info_text = $(info_icon).siblings('.app-help-info');
			let settings_icon = $(info_icon).siblings('.app-settings-icon');
			$(info_icon).on('click', function(e) {
				e.stopPropagation();
				info_text.removeClass('d-none');
				settings_icon.addClass('d-none');
			});
			$(info_text).children('.btn-close').on('click', function(e) {
				e.stopPropagation();
				info_text.addClass('d-none');
				settings_icon.removeClass('d-none');
			});
		});

		// Initialize tag search select2
		$('.tag-search-field').select2({
			placeholder: "Filter by tag",
		});

		// Bind to the select2 change event
		$('.tag-search-field').on('change.select2', filter_apps);

	});
	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed, returning the public interface object.