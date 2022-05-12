/*****************************************************************************
 * FILE: ESRI Map Library
 * DATE:    December 20, 2016
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2016
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var ESRI_MAP = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
        //Options Attributes
    var BASE_MAP_ATTRIBUTE = 'data-esri-base-map',
        VIEW_ATTRIBUTE = 'data-esri-view',
        LAYERS_ATTRIBUTE = 'data-esri-layers';

    //Objects
    var public_interface,				// Object returned by the module
        m_map,                          // The map
        m_view,
        m_base_map_options,
        m_view_options,
        m_layers_options,
        m_layer_extent;

    //Selectors
    var m_map_target;


    /************************************************************************
     *                    PRIVATE METHOD DECLARATIONS
     *************************************************************************/
        //Initialization Methods
    var parse_options,esri_base_map_init, esri_layers_init, esri_view_init,esri_legend_init,esri_initialize_all;

    // Utility Methods
    var is_defined;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    parse_options = function(){
        var $map_element = $('#'+m_map_target);
        m_base_map_options = $map_element.attr(BASE_MAP_ATTRIBUTE);
        m_view_options = $map_element.attr(VIEW_ATTRIBUTE);
        m_layers_options = $map_element.attr(LAYERS_ATTRIBUTE);
        if (is_defined(m_base_map_options)) {
            m_base_map_options = JSON.parse(m_base_map_options);
        }
        if(is_defined(m_layers_options)){
            m_layers_options = JSON.parse(m_layers_options)
        }
        if (is_defined(m_view_options)) {
            m_view_options = JSON.parse(m_view_options);
        }


    };

    esri_base_map_init = function(){

        //Declarations
        require([
            "esri/Map",
            "esri/views/MapView",
            "esri/layers/FeatureLayer",
            "dojo/domReady!"
        ], function(Map, MapView) {
            m_map = new Map({
                basemap: m_base_map_options
            });

            m_view = new MapView({
                container: m_map_target,  // Reference to the DOM node that will contain the view
                map: m_map,
                zoom:4,
                center: [15,55]// References the map object created in step 3
            });
        });

    };

    esri_layers_init = function(){
        if(is_defined(m_layers_options)){
            for (var i = m_layers_options.length;i--;){
                var current_layer,
                    layer, Type, Url;

                current_layer = m_layers_options[i];
                if(current_layer.type == 'FeatureLayer'){
                    require(["esri/layers/FeatureLayer"],function (FeatureLayer) {
                        layer = new FeatureLayer({
                            url: current_layer.url
                        });
                        m_map.add(layer);

                    });
                }

                if(current_layer.type == 'MapImageLayer'){
                    require(["esri/layers/MapImageLayer"],function (MapImageLayer) {
                        layer = new MapImageLayer({
                            portalItem:{
                                id: current_layer.url
                            }
                        });
                        m_map.add(layer);
                    });
                }

                if(current_layer.type == 'VectorTileLayer'){
                    require(["esri/layers/VectorTileLayer"],function (VectorTileLayer) {
                        layer = new VectorTileLayer({
                            url: current_layer.url
                        });
                        m_map.add(layer);
                    });
                }

                if(current_layer.type == 'ImageryLayer'){
                    require(["esri/layers/ImageryLayer"],function (ImageryLayer) {
                        layer = new ImageryLayer({
                            url: current_layer.url,
                            format: "jpgpng"
                        });
                        m_map.add(layer);
                    });
                }


            }
        }

    };

    esri_view_init = function () {
        //Declarations
        var view_json;

        var $map_element = $('#' + m_map_target);
        view_json = $map_element.attr('data-esri-view');


        if (typeof  view_json !== typeof undefined && view_json !== false){
            var view_obj;

            view_obj =  JSON.parse(view_json);

            if('center' in view_obj && 'zoom' in view_obj){
                    require([
                        "esri/views/MapView",
                        "esri/widgets/LayerList",
                        "dojo/domReady!"
                    ], function(MapView) {
                        m_view = new MapView({
                            container: m_map_target,  // Reference to the DOM node that will contain the view
                            map: m_map,
                            zoom:view_obj['zoom'],
                            center: view_obj['center']
                        });

                        esri_layers_init();


                    });



            }
        }
    };

    esri_legend_init = function(){
        require([
            "esri/views/MapView",
            "esri/widgets/LayerList",
            "dojo/domReady!"],function (MapView,LayerList) {
                var layerList = new LayerList({
                    view: m_view
                });
                layerList.on("trigger-action",function(event){

                    var id = event.action.id;


                });
                // Add widget to the top right corner of the view
                m_view.ui.add(layerList, "top-right");
        });

    };


    esri_initialize_all = function(){
        m_map_target = 'esri_map_view';

        parse_options();

        esri_base_map_init();

        esri_view_init();

        esri_legend_init();

    };


    is_defined = function(variable)
    {
        return !!(typeof variable !== typeof undefined && variable !== false);
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

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        // Initialize Global Variables;
        esri_initialize_all();

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.