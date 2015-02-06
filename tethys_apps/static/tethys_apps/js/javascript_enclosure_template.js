/*****************************************************************************
 * FILE:    JavaScript Enclosure Template
 * DATE:    
 * AUTHOR: 
 * COPYRIGHT: (c) XXXX Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LIBRARY_OBJECT = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library
	
	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface,				// Object returned by the module
 		example_var,					// Example global variable
 		another_var;					// Another example variable
		
		
	
	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var hello_world, goodbye_world;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
 	
 	hello_world = function() {
 		console.log("Hello, World!");
 	};

 	goodbye_world = function() {
 		console.log("Goodbye, World!");
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
		hello_goodbye: function() {
			hello_world();
			goodbye_world();
		},
		my_name_is: function(name) {
			console.log("My Name Is: " + name);
		}
	};
	
	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/
	
	// Initialization: jQuery function that gets called when 
	// the DOM tree finishes loading
	$(function() {
		// Initialize Global Variables
		example_var = "Example";
		another_var = 1;
	});

	return public_interface;

}()); // End of package wrapper 
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper 
// function immediately after being parsed.