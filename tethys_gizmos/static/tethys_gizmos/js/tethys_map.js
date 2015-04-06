/*****************************************************************************
 * FILE:    tethys_map.js
 * DATE:    13 January 2014
 * AUTHOR: Nathan R. Swain
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_MAP = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library
	
	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var GE,							// GoogleEarth map object
 		google_map_urls,				// The url of the data to be loaded into the map
		libraryObject;				// Object returned by the module
		
	
	// Load Google Earth Library
	google.load("earth", "1");

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
	// Google Map and Earth Managment Function Declarations
	var initGoogleEarth, googleEarthInitCB, googleEarthFailureCB, initGoogleMap, parseJsonLinks,
		retrieveKmlData;
	
	googleEarthInitCB = function(instance) {
		// Variable declarations
		var link, networkLink;
		
		// Initiate instance of Google Earth Plugin
		GE = instance;
		GE.getWindow().setVisibility(true);
		
		// Turn on controls
		GE.getNavigationControl().setVisibility(GE.VISIBILITY_AUTO);
		
		// Load KML URLs into Google Earth Instance
		// NOTE: url variable is passed to js using a script on the google_map snippet
		for (var i = 0; i < google_map_urls.length; i++) {
			link = GE.createLink('');
		    link.setHref(google_map_urls[i]);
		    
		    networkLink = GE.createNetworkLink('');
		    networkLink.setLink(link);
		
		    GE.getFeatures().appendChild(networkLink);
		    networkLink.set(link, true, true);
		}
	};
	
	googleEarthFailureCB = function(errorCode) {
		google.load("maps", "3", {other_params:'sensor=false', callback: initGoogleMap});
	};
	
	// Google Earth Managment Functions
	initGoogleEarth = function() {
		google.earth.createInstance('google_map', googleEarthInitCB, googleEarthFailureCB);
	};
	
	// Google Map Managment Functions
	initGoogleMap = function() {
		// Variable declarations
		var mapOptions;
		
		// Configure map
		mapOptions = {
			center: new google.maps.LatLng(39.0, -96.0),
			zoom: 4,
			mapTypeId: google.maps.MapTypeId.HYBRID,
	    	scaleControl: true,
	    	rotateControl: true,
		};
		
		// init map
		var map = new google.maps.Map(document.getElementById('google_map'), mapOptions);
								  				  
		// Load KML
		for (var i = 0; i < google_map_urls.length; i++) {
			var layer = new google.maps.KmlLayer(google_map_urls[i]);
			layer.setMap(map);
		}
	};

	// Parse the json object retrieved by kml_service
    parseJsonLinks = function(json) {
        var kml_links;

        // Parse the json object returned
        if (json instanceof Array) {
            kml_links = json;

        } else if (json instanceof Object && 'kml_links' in json) {
            kml_links = json['kml_links'];

        } else if (json instanceof Object && 'kml_link' in json) {
            kml_links = json['kml_link'];

        } else {
            kml_links = [];
        }

        // Check for relative urls and append host if necessary
        for (var i = 0; i < kml_links.length; i++) {
            var current_link;

            current_link = kml_links[i];

            if (!current_link.contains('://')) {
                var host;

                // Assemble the host
                host = location.protocol + '//' + location.host;

                if (current_link.charAt(0) === '/') {
                    current_link = host + current_link;
                } else {
                    current_link = host + '/' + current_link;
                }

                // Overwrite the previous link
                kml_links[i] = current_link;
            }
        }

        return kml_links;
    };
	
	// KML Data Retriever
	retrieveKmlData = function(kml_service) {
		$.ajax({
			url: kml_service
		}).done(function(json) {
			var google_map_div;
			var height, width;
			
			// Set global map data variable
		    google_map_urls = parseJsonLinks(json);
			
			// Get height and width of loading div
			height = $('#google_map_loading').css('height');
			width = $('#google_map_loading').css('width');
			
			// Replace loading div with google earth div
			google_map_div = '<div id="google_map" style="height: ' + height + '; width: ' + width + ';"></div>';
			$('#google_map_loading').replaceWith(google_map_div);
			
			// Trigger google map load
			initGoogleEarth();
		});
	};
	
	/************************************************************************
 	*                            TOP LEVEL CODE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 */
	libraryObject = {};
	
	/************************************************************************
 	*                            Initialization
 	*************************************************************************/
	$(function() {
	    // Add contains method to String prototype
        if ( !String.prototype.contains ) {
            String.prototype.contains = function() {
                return String.prototype.indexOf.apply( this, arguments ) !== -1;
            };
        }

		// Initialize globals
		google_map_urls = [];
		
		// Retrieve data for maps
		$('.google_map_loading').each(function() {
			var kml_service = $(this).attr('data-kml-service');
			retrieveKmlData(kml_service);
		});

    // Deprecation warning
    console.log('WARNING: You have used the "google_map" gizmo. This gizmo has been deprecated and may not be supported in future releases.')
	});

	return libraryObject;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/
// No public functions... it just works for now.