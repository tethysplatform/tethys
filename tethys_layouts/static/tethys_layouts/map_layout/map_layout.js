/*****************************************************************************
 * FILE:    map_layout.js
 * DATE:    October 19, 2018
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) Aquaveo 2018
 * LICENSE:
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var MAP_LAYOUT = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	// Constants
    var SELECTED_POINT_COLOR =           '#7300e5',
 	    SELECTED_LINE_COLOR =            '#7300e5',
 	    SELECTED_POLYGON_COLOR =         '#7300e5';

 	// Module variables
 	var m_public_interface;				// Object returned by the module

 	var m_map,                          // OpenLayers map object
 	    m_layers,                       // OpenLayers layer objects mapped to by layer by layer_name
 	    m_layer_groups,                 // Layer and layer group metadata
 	    m_workspace,                    // Workspace from SpatialManager
 	    m_extent,                       // Home extent for map
        m_capabilities,                 // WMS Capabilities 
 	    m_show_properties_popup,        // Show properties pop-up
 	    m_show_map_click_popup,         // Show the properties pop-up at the clicked point (instead of the centroid of the selected feature if feature selection is on)
 	    m_select_interaction,           // TethysMap select interaction for vector layers
 	    m_drawing_layer;                // The drawing layer

 	var m_geocode_objects,              // An array of the current items in the geocode select
        m_geocode_layer;                // Layer used to store geocode location

    var m_props_popup_overlay,          // OpenLayers overlay containing the properties popup
        m_$props_popup_container,       // Properties popup container element
        m_$props_popup_content,         // Properties popup content element
        m_$props_popup_closer;          // Properties popup close button


    var m_plot,                         // Plot object
        m_plot_config;                  // Configuration options for the plot

    // Permissions
    var p_can_geocode,                  // Can use geocode feature
        p_can_plot;                     // Can use plotting feature

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// Config
 	var parse_attributes, parse_permissions, setup_ajax, setup_map, csrf_token, sync_layer_visibility;

 	// Map management
 	var remove_layer_from_map, get_layer_name_from_feature, get_layer_id_from_layer, get_feature_id_from_feature;

 	// Action Button
 	var generate_action_button, bind_action_buttons, load_action;

 	// Plotting
 	var init_plot, generate_plot_button, bind_plot_buttons, load_plot, fit_plot, update_plot, show_plot, hide_plot,
	    post_update_plot;

 	// Layers tab
 	var init_layers_tab, init_new_layers_tab, init_visibility_controls, init_opacity_controls, init_rename_controls,
 	    init_remove_controls, init_zoom_to_controls, init_collapse_controls, init_collapse_control,
 	    init_add_layer_controls, init_download_layer_controls, init_dropdown_layer_toggle_controls;

    // Legends tab
    var init_legends, show_legend, hide_legend, update_legend, update_division_legend_and_layer, update_wms_legend,
        update_result_layer, update_layer_style;

    // Properties pop-up
    var init_pop_up_overlay, init_map_clicked_pop_up, display_properties, show_properties_pop_up,
        hide_properties_pop_up, close_properties_pop_up, reset_properties_pop_up, append_properties_pop_up_content,
        reset_ui, generate_properties_table_title, generate_properties_table, generate_dataset_row,
        generate_custom_properties_table_content, initialize_custom_content;

 	// Feature selection
 	var init_feature_selection, points_selection_styler, lines_selection_styler,
 	    polygons_selection_styler, on_select_vector_features, on_select_wms_features;

 	// Action modal
 	var init_action_modal, build_action_modal, show_action_modal, hide_action_modal;

 	// Geocode feature
 	var init_geocode, do_geocode, clear_geocode;

 	// Cache methods
 	var is_in_cache, add_to_cache, remove_from_cache, get_from_cache;

 	// Drawing methods
 	var init_draw_controls;

 	// Utility Methods
 	var generate_uuid, load_layers, hide_layers, show_layers;

 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
    // Config
    parse_attributes = function() {
        var $map_attributes = $('#map-layout-attributes');
        m_layer_groups = $map_attributes.data('layer-groups');
        m_extent = $map_attributes.data('map-extent');
        m_workspace = $map_attributes.data('workspace');
        m_show_properties_popup = $map_attributes.data('show-properties-popup');
        m_show_map_click_popup = $map_attributes.data('show-map-click-popup');
    };

    parse_permissions = function() {
        var $map_permissions = $('#map-layout-permissions');
        p_can_geocode = $map_permissions.data('can-use-geocode');
        p_can_plot = $map_permissions.data('can-use-plot');
        if (typeof p_can_plot !== "boolean") {
            p_can_plot = false;
        }
    };

    setup_ajax = function() {
        // Ajax options
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", get_csrf_token());
                }
            }
        });
    };

    setup_map = function() {
        // Change Extent Button from "E" to Extent Symbol
        let $extent_button = $('button[title="Fit to extent"]');
        $extent_button.html('<i class="bi bi-house-fill"></i>');

        // Get handle on map
	    m_map = TETHYS_MAP_VIEW.getMap();

	    // Setup layer map
	    m_layers = {};
	    m_drawing_layer = null;
        m_capabilities = {};

	    // Get id from tethys_data attribute
	    m_map.getLayers().forEach(function(layer, index, array) {
	        // Handle normal layers (skip basemap layers)
	        if ('tethys_data' in layer && 'layer_id' in layer.tethys_data) {
	           if (layer.tethys_data.layer_id in m_layers) {
	               console.log('Warning: layer_name already in layers map: "' + layer.tethys_data.layer_id + '".');
	           }
	           m_layers[layer.tethys_data.layer_id] = layer;

               // Lookup extent from WMS GetCapabilities if applicable
               let source = layer.getSource();
               if ((source instanceof ol.source.TileWMS || source instanceof ol.source.ImageWMS) && !layer.tethys_legend_extent) {
                    const capabilities_parser = new ol.format.WMSCapabilities();

                    // Callback for then on GetCapabilities fetch requests
                    let then_lookup_extent = function (capabilities) {
                        let cap_layers = capabilities.Capability.Layer.Layer;
                        let cap_layer = cap_layers.find(function(cl) {
                            return source.getParams().LAYERS.includes(cl.Name);
                        });

                        if (cap_layer) {
                            let BBOX_84 = cap_layer.BoundingBox.find(function(bb) {
                                return ["CRS:84", "EPSG:4326"].includes(bb.crs);
                            });

                            if (BBOX_84) {
                                layer.tethys_legend_extent = BBOX_84.extent;  // save to tethys_legend_extent
                            }
                        }

                        return capabilities;
                    };

                    // Fetch the WMS GetCapabilities for each layer
                    $.each(source.getUrls(), function(i, url) {
                        let capabilities_url = `${url}?request=GetCapabilities`;
                        
                        // Use cache if layer on same server as previous lookup
                        if (capabilities_url in m_capabilities) {
                            m_capabilities[capabilities_url].then(then_lookup_extent);
                        } 
                        // Fetch GetCapabilities and save to cache
                        else {
                            m_capabilities[capabilities_url] = fetch(capabilities_url)
                            .then(function(response){ return response.text(); })
                            .then(function(text) { return capabilities_parser.read(text); })
                            .then(then_lookup_extent);
                        }
                    });
               }
	        }
	        // Handle drawing layer
	        else if ('tethys_legend_title' in layer && layer.tethys_legend_title == 'Drawing Layer') {
	            m_drawing_layer = layer;
	            m_layers['drawing_layer'] = m_drawing_layer;
	        }
	    });

        // Setup feature selection
	    init_feature_selection();
    };

    // Sync layer visibility
    sync_layer_visibility = function() {
        let layer_tab_panel = $('#layers-tab-panel');
        let layer_groups = layer_tab_panel.find('.layer-group-item');
        let i;
        let check_status;
        $.each(layer_groups, function(index, content) {
            // Get Group check status
            if (content.id) {
                check_status = $(`#${content.id}`).find('.layer-group-visibility-control')[0].checked;

                let layer_list_id = $(`#${content.id}`).next()[0].id;

                if (layer_list_id) {
                    let layer_lists =  $(`#${layer_list_id}`).children();

                    // Do not show any layers associated with unchecked layer groups
                    if (check_status == false) {
                        $.each(layer_lists, function(layer_index, layer_content) {
                            let layer_id = layer_content.getElementsByClassName('layer-visibility-control')[0].dataset.layerId;
                            if (m_layers[layer_id]) {
                                m_layers[layer_id].setVisible(false);
                            }
                        })
                    } else {
                        $.each(layer_lists, function(layer_index, layer_content) {
                            let layer_id = layer_content.getElementsByClassName('layer-visibility-control')[0].dataset.layerId;
                            let checked = $(layer_content).find(`[data-layer-id='${layer_id}']`)[0].checked;
                            if (checked) {
                                show_legend(layer_id);
                            }
                            else {
                                hide_legend(layer_id);
                            }
                        })
                    }
                }
            }
        });
    };

    // Map Management
    remove_layer_from_map = function(layer_name) {
        // Remove from map
        m_map.removeLayer(m_layers[layer_name]);

        // Remove from layers list
        delete m_layers[layer_name];
    };

    get_layer_name_from_feature = function(feature) {
        // Get layer_name from property of the feature
        let layer_name = feature.get('layer_name');

        // Attempt to derive layer name from ID assigned by GeoServer to be able to map to features to layers in map (<layer_name>.<fid>)
        // e.g.: 0958cc07-c194-4af9-81c5-118a77d335ac_stream_links.fid--72787a80_169a16811e6_-7aa6
        if (!layer_name) {
            let feature_id = feature.getId() || feature.get('id');
            layer_name = feature_id.split('.')[0];

            // Prepend the workspace for everything except the drawing layer
            if (layer_name !== 'drawing_layer') {
                layer_name = m_workspace + ':' + layer_name;
            }
        }

        return layer_name;
    };

    get_layer_id_from_layer = function(layer) {
        // Skip if there is no tethys_data attribute on the layer
        if (!layer || !layer.hasOwnProperty('tethys_data') || !layer.tethys_data) {
            return '';
        }

        // Attempt to get layer_id property
        if (layer.tethys_data.hasOwnProperty('layer_id')) {
            return layer.tethys_data.layer_id;
        }

        // Fall back on the layer_name property
        if (layer.tethys_data.hasOwnProperty('layer_name')) {
            return layer.tethys_data.layer_name;
        }

        return '';
    };

    get_feature_id_from_feature = function(feature) {
        let feature_id = feature.getId();

        if (feature_id) {
            if (feature_id.includes != undefined && feature_id.includes('.fid')) {
                // Derive fid from ID assigned by GeoServer (<layer_name>.<fid>)
                // e.g.: 0958cc07-c194-4af9-81c5-118a77d335ac_stream_links.fid--72787a80_169a16811e6_-7aa6
                feature_id = feature_id.split('.')[1];
            }
        } else {
            feature_id = feature.get('id');
        }

        return feature_id;
    };

    // Plotting
    init_plot = function() {
        // Skip if no permission to use plot
        if (!p_can_plot) {
            return;
        }

        m_plot = 'map-plot';
        m_plot_config = {scrollZoom: true};

        let data = [];

        let layout = {
            autosize: true,
            height: 415,
            margin: {l: 80, r: 80, t: 20, b: 80},
            xaxis:  {
                title: {
                  text: 'X Axis Title',
                }
            },
            yaxis: {
                title: {
                  text: 'Y Axis Title',
                }
            }
        };

        // Create initial plot
        update_plot('Plot Title', data, layout);

        // Setup plot resize when slide sheet changes size
        $(window).resize(function() {
            fit_plot();
        });

        // Resize plot when nav is opened or closed
        $('.toggle-nav').on('tethys:toggle-nav', function(e) {
            fit_plot();
        });
    };

    update_plot = function(title, data, layout) {
        let out = Plotly.validate(data, layout);
        if (out) {
            $(out).each(function(index, item) {
                console.log(`PlotlyValidationWarning: ${item.msg}`);
            });
        }

        // Update plot
        Plotly.react(m_plot, data, layout, m_plot_config).then(function(p) {
            // Resize plot to fit after rendering the first time
            fit_plot();

            // Update slide sheet title
            $('#plot-slide-sheet .slide-sheet-title').html(title);
	    
	    // Call post plot update callback
	    if (post_update_plot) { post_update_plot(p); }
        });
    };

    generate_plot_button = function(feature, layer) {
        // Skip if no permission to use plot
        if (!p_can_plot) {
            return;
        }
        let layer_id = get_layer_id_from_layer(layer);
        let fid = get_feature_id_from_feature(feature);

        // Check if layer is plottable
        if (!layer ||
            !layer.hasOwnProperty('tethys_data') ||
            !layer.tethys_data.hasOwnProperty('plottable') ||
            !layer.tethys_data.plottable) {
            return;
        }

        // Build Plot Button Markup
        let plot_button =
            '<div class="plot-btn-wrapper">' +
                '<a class="btn btn-primary btn-popup btn-plot my-2" ' +
                    'href="javascript:void(0);" ' +
                    'role="button" ' +
                    'data-feature-id="' + fid +'" ' +
                    'data-layer-id="' + layer_id + '" ' +
                    'data-layer-data="' + encodeURIComponent(JSON.stringify(layer.tethys_data)) + '"' +
                    'data-feature-props="' + encodeURIComponent(JSON.stringify(feature.getProperties())) + '"' +
                '>Plot</a>' +
            '</div>';

        return plot_button;
    };

    generate_action_button = function(feature, layer) {
        // Skip if no permission to use plot
        if (!p_can_plot) {
            return;
        }

        let layer_id = get_layer_id_from_layer(layer);
        let fid = get_feature_id_from_feature(feature);

        // Check if layer is has action
        if (!layer ||
            !layer.hasOwnProperty('tethys_data') ||
            !layer.tethys_data.hasOwnProperty('has_action') ||
            !layer.tethys_data.has_action) {
            return;
        }

        // Build Action Button Markup
        let action_button =
            '<div class="action-btn-wrapper">' +
                '<a class="btn btn-primary btn-popup btn-action" ' +
                    'href="javascript:void(0);" ' +
                    'role="button"' +
                    'data-feature-id="' + fid +'"' +
                    'data-layer-id="' + layer_id + '"' +
                '>Action</a>' +
            '</div>';

        return action_button;
    };

    bind_plot_buttons = function() {
        // Reset click events on plot buttons
        $('.btn-plot').off('click');

        // Call load_plot when buttons are clicked
        $('.btn-plot').on('click', function(e) {
            let layer_name = $(e.target).data('layer-id');
            let feature_id = $(e.target).data('feature-id');
            let layer_data = decodeURIComponent($(e.target).data('layer-data'));
            let feature_props = decodeURIComponent($(e.target).data('feature-props'));

            // Load the plot
            load_plot(e.target, layer_name, feature_id, layer_data, feature_props);
            hide_properties_pop_up();
        });
    };

    bind_action_buttons = function() {
        // Reset click events on action buttons
        $('.btn-action').off('click');

        // Call load_action when buttons are clicked
        $('.btn-action').on('click', function(e) {
            let layer_name = $(e.target).data('layer-id');
            let feature_id = $(e.target).data('feature-id');

            // Load the plot
            load_action(e.target, layer_name, feature_id);
        });
    };

    load_plot = function(plot_button, layer_name, feature_id, layer_data, feature_props) {
        // Disable plot button
        $(plot_button).attr('disabled', 'disabled');

        // Get plot data for feature
        $.ajax({
            url: '.',
            type: 'POST',
            data: {
                'method': 'get-plot-data',
                'layer_name': layer_name,
                'feature_id': feature_id,
                'layer_data': layer_data,
                'feature_props': feature_props,
            },
        }).done(function(data){
            // Update plot
            update_plot(data.title, data.data, data.layout);

            // Show the plot slide sheet
            show_plot();

            // Enable plot button
            $(plot_button).removeAttr('disabled');
        });
    };

    load_action = function(action_button, layer_name, feature_id) {
        // Use public interface in Apps to customize action
    };

    fit_plot = function() {
        let plot_container_width = $('#plot-slide-sheet').width();
        Plotly.relayout(m_plot, {width: plot_container_width});
    };

    show_plot = function() {
        SLIDE_SHEET.open('plot-slide-sheet');
    };

    hide_plot = function() {
        SLIDE_SHEET.close('plot-slide-sheet');
    };

    // Action modal
    init_action_modal = function() {
        // Remove action button click events whenever modal hides
        $('#action-modal').on('hide.bs.modal', function(e) {
            let $modal_do_action_button = $('#action-modal #do-action-button');
            $modal_do_action_button.off('click');
        });

        // Enable autofocus on modal
        $('#action-modal').on('shown.bs.modal', function() {
            $(this).find('[autofocus]').focus();
        });
    };

    build_action_modal = function(modal_title, modal_content, modal_action, modal_style) {
        let $modal = $('#action-modal');
        let $modal_title = $('#action-modal #action-modal-title');
        let $modal_content = $('#action-modal #action-modal-content');
        let $modal_do_action_button = $('#action-modal #do-action-button');

        $modal_title.html(modal_title);
        $modal_content.html(modal_content);
        $modal_do_action_button.html(modal_action);
        $modal_do_action_button.attr('class', 'btn btn-' + modal_style);

        return {
            'modal': $modal,
            'title': $modal_title,
            'content': $modal_content,
            'action_button': $modal_do_action_button,
        };
    };

    show_action_modal = function() {
        let $modal = $('#action-modal');
        $modal.modal('show');
    };

    hide_action_modal = function() {
        let $modal = $('#action-modal');
        $modal.modal('hide');
    };

    // Layers tab methods
    init_layers_tab = function() {
        // Init controls
        init_action_modal();
        init_visibility_controls();
        init_opacity_controls();
        init_rename_controls();
        init_dropdown_layer_toggle_controls();
        init_remove_controls();
        init_zoom_to_controls();
        init_download_layer_controls();
        init_add_layer_controls();
        init_collapse_controls();
    };

    init_new_layers_tab = function(group_id) {
        // Init controls
        init_action_modal();
        init_visibility_controls();
        init_opacity_controls();
        init_rename_controls();
        init_dropdown_layer_toggle_controls();
        init_remove_controls();
        init_zoom_to_controls();
        init_collapse_control(group_id + '--collapse');
    };

    init_visibility_controls = function() {
        // Setup deselect event on radio buttons in layers menu
        let selected_radios = {};

        // Credits for radio deselect event: https://stackoverflow.com/questions/11173685/how-to-detect-radio-button-deselect-event
        $('input[type="radio"]').on('click', function() {
            if (this.name in selected_radios) {
                // A non-active radio button is clicked
                if (this != selected_radios[this.name]) {
                    // Fire the deselect event on the previously active radio button
                    $(selected_radios[this.name]).trigger("deselect");

                    // Save this radio as the new active radio button
                    selected_radios[this.name] = this;
                }
                // The the active radio is clicked again
                else {
                    // Uncheck the radio (like a checkbox)
                    this.checked = false;
                    // Fire the deselect event on the radio
                    $(this).trigger("deselect");
                    // No radio is selected in this group,
                    // so remove it from the selected radios object
                    delete selected_radios[this.name];
                }
            }
            else {
                // Save which radio was just checked on
                selected_radios[this.name] = this;
            }

        }).filter(':checked').each(function() {
            // Note initial state of radio buttons
            selected_radios[this.name] = this;
        });

        // Layer group visibility
        $('.layer-group-visibility-control').on('change', function(e) {
            let $target = $(e.target);
            let layer_group_checked = $target.is(':checked');
            let $layer_group_item = $target.closest('.layer-group-item');
            let $layer_list = $layer_group_item.next('.layer-list');

            // Reset the ui
            reset_ui();

            // For each layer visibilty control...
            let $layer_visiblity_controls = $layer_list.find('.layer-visibility-control');

            $layer_visiblity_controls.each(function(index, item) {
                // Set disabled
                let $item = $(item);
                $item.prop('disabled', !layer_group_checked);

                // Set layer visibility
                let layer_name = $item.data('layer-id');
                let layer_checked = $item.is(':checked');
                let layer_variable = $item.data('layer-variable');
                if (m_layers[layer_name]) { // handle empty layer groups. E.g. empty Custom Layers
                    m_layers[layer_name].setVisible(layer_group_checked && layer_checked);
                }

                if (layer_group_checked && layer_checked) {
                    show_legend(layer_name);
                } else {
                    hide_legend(layer_name);
                }

            });

            // For each context menu...
            let $layers_context_menu = $layer_list.find('.layers-context-menu');

            $layers_context_menu.each(function(index, item) {
                let $dropdown_toggle = $(item).find('.dropdown-toggle');

                if (layer_group_checked) {
                    $dropdown_toggle.removeClass('disabled');
                }

                else {
                    $dropdown_toggle.addClass('disabled');
                }
            });
        });

        // Layer visibility
        $('.layer-visibility-control').on('change', function(e) {
            let $target = $(e.target);
            let checked = $target.is(':checked');
            let layer_name = $target.data('layer-id');
            let layer_variable = $target.data('layer-variable');

            // Reset the ui
            reset_ui();

            // Set the visibility of layer
            if (m_layers[layer_name]) { // handle empty layer groups. E.g. empty Custom Layers
                m_layers[layer_name].setVisible(checked);
            }

            // Set the visibility of legend
            if (checked) {
                show_legend(layer_name);
            }
            else {
                hide_legend(layer_name);
            }

            // TODO: Save state to local storage
        });

        // Handle radio deselect events
        $('.layer-visibility-control').on('deselect', function(e) {
            let $target = $(e.target);
            let checked = $target.is(':checked');
            let layer_name = $target.data('layer-id');
            let layer_variable = $target.data('layer-variable');

            // Set the visibility of layer
            if (m_layers[layer_name]) { // handle empty layer groups. E.g. empty Custom Layers
                m_layers[layer_name].setVisible(checked);
            }

            // Set the visibility of legend
            hide_legend(layer_name);

            // TODO: Save state to local storage
        });
    };

    init_opacity_controls = function() {
        // Handle changes to the opacity controls
        $('.layer-opacity-control').on('input', function(e) {
            let $target = $(e.target);
            let val = $target.val();

            // Update display value
            let $label = $target.prev('label');
            let $label_value = $label.children('.slider-value').first();
            $label_value.html(val + '%');

            // Update opacity of layer
            let layer_name = $target.data('layer-id');
            m_layers[layer_name].setOpacity(val/100);

            // TODO: Save state to local storage
        });
    };

    init_rename_controls = function() {
        // Rename layer
        $('.rename-action').on('click', function(e) {
            let $action_button = $(e.target);

            if (!$action_button.hasClass('rename-action')) {
                $action_button = $action_button.closest('.rename-action');
            }

            let $layer_label = $action_button.closest('.layers-context-menu').prev();
            let $display_name = $layer_label.find('.display-name').first();
            let current_name = $display_name.html();

            // Build Modal
            let modal_content = '<div class="form-group">'
                              +     '<label class="sr-only" for="new-name-field">New name:</label>'
                              +     '<input class="form-control" type="text" id="new-name-field" value="' + current_name + '" autofocus onfocus="this.select();">'
                              + '</div>';

            let modal = build_action_modal('Rename Layer', modal_content, 'Rename', 'success');

            // Show Modal
            show_action_modal();

            // Handle Modal Action
            modal.action_button.on('click', function(e) {
                // Rename layer label
                let new_name = modal.content.find('#new-name-field').first().val();
                $display_name.html(new_name);

                // Hide the modal
                hide_action_modal();

                csrf_token = $("input[name=csrfmiddlewaretoken]").val();
                $.ajax({
                  type: "POST",
                  url: "",
                  data: {
                    method: "on_rename_tree_item",
                    new_name: new_name,
                    current_name: current_name,
                  },
                  beforeSend: (xhr) => {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                  },
                }).done(function(data) {
                    if (data.success) {
                        TETHYS_APP_BASE.alert("success", `Successfully renamed layer "${current_name}" to "${new_name}".`);
                    } else {
                        TETHYS_APP_BASE.alert("warning", `Unable to save new name for layer "${current_name}" permanently.`);
                        console.log(data.message);
                    }
                });
            });
        });
    };

    init_remove_controls = function() {
        $('.remove-action').on('click', function(e) {
            let removed_layer_ids = [];
            let $action_button = $(e.target);
            // If button has custom layer container as parent, it is a button on a custom layer
            let is_custom = $action_button.parents('#custom_layers_associated_layers').length > 0;

            if (!$action_button.hasClass('remove-action')) {
                $action_button = $action_button.closest('.remove-action');
            }

            let remove_type = $action_button.data('remove-type');
            let $layer_label = $action_button.closest('.layers-context-menu').prev();
            let display_name = $layer_label.find('.display-name').first().html();

            // Build Modal
            let modal_title = '';
            let modal_content = '';
            if (remove_type === 'layer') {
                modal_title = 'Remove Layer'
                modal_content = '<p>Are you sure you want to remove the "' + display_name
                              + '" layer?</p>';
            } else {
                modal_title = 'Remove Layer Group'
                modal_content = '<p>Are you sure you want to remove the "' + display_name
                              + '" layer group and all of its layers?</p>';
            }

            let modal = build_action_modal(modal_title, modal_content, 'Remove', 'danger');

            // Show Modal
            show_action_modal();


            // Handle Modal Action
            modal.action_button.on('click', function(e) {
                // Reset the ui
                reset_ui();
                let layer_group_id = null;
                if (remove_type === 'layer') {
                    // Remove layer from map
                    let layer_id = $action_button.data('layer-id');
                    removed_layer_ids.push(layer_id);
                    remove_layer_from_map(layer_id);

                    // Remove item from layers tree
                    let layer_list_item = $action_button.closest('.layer-list-item');
                    layer_list_item.remove();
                } else {
                    // Remove layers from map
                    layer_group_id = $action_button.data('layer-group-id');
                    let $layer_group_item = $action_button.closest('.layer-group-item');
                    let $layer_list = $layer_group_item.next('.layer-list');

                    let $layer_visiblity_controls = $layer_list.find('.layer-visibility-control');

                    // Remove all layers in layer group
                    $layer_visiblity_controls.each(function(index, item) {
                        let layer_id = $(item).data('layer-id');
                        removed_layer_ids.push(layer_id);
                        remove_layer_from_map(layer_id);
                    });

                    // Remove layer group item
                    $layer_group_item.remove();

                    // Remove layer list item
                    $layer_list.remove();
                }

                // Hide the modal
                hide_action_modal();

                // Call server callback method to persist removal
                csrf_token = $("input[name=csrfmiddlewaretoken]").val();
                $.ajax({
                  type: "POST",
                  url: "",
                  data: {
                    method: "on_remove_tree_item",
                    layer_ids: removed_layer_ids,
                    remove_type: remove_type,
                    is_custom: is_custom,
                    layer_group_id: layer_group_id,
                  },
                  beforeSend: (xhr) => {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                  },
                }).done(function(data) {
                    if (data.success) {
                        TETHYS_APP_BASE.alert("success", `Successfully removed ${remove_type.replace('-', ' ')}.`);
                    } else {
                        TETHYS_APP_BASE.alert("warning", `Unable to remove ${remove_type.replace('-', ' ')} permanently.`);
                        console.log(data.message);
                    }
                });
            });
        });
    };

    init_dropdown_layer_toggle_controls = function() {
        // Rename layer
        $('.layer-dropdown-toggle').on('switchChange.bootstrapSwitch', function(e, state) {
            let $action_button = $(e.target);
            let $layer_label = $action_button.closest('.layers-context-menu').prev();
            let display_name = $layer_label.find('.display-name').first().html();

            // TODO: Save state to local storage
        });
    };

    init_zoom_to_controls = function() {
        // Zoom to layer
        $('.zoom-to-layer-action').on('click', function(e) {
            let $action_button = $(e.target);

            if (!$action_button.hasClass('zoom-to-layer-action')) {
                $action_button = $action_button.closest('.zoom-to-layer-action');
            }

            let layer_name = $action_button.data('layer-id');
            let extent = m_layers[layer_name].getExtent();

            if (extent) {
                // Zoom to layer extent
                TETHYS_MAP_VIEW.zoomToExtent(extent);
            }
            else if ('tethys_legend_extent' in m_layers[layer_name] && m_layers[layer_name].tethys_legend_extent) {
                // use tethys legend extent if it is part of the layer
                TETHYS_MAP_VIEW.zoomToExtent(m_layers[layer_name].tethys_legend_extent);
            }
            else {
                // TODO: Query GeoServer to get layer extent?
                // Zoom to map extent if layer has no extent
                TETHYS_MAP_VIEW.zoomToExtent(m_extent);
            }
        });
    };

    var init_download_layer_action = function() {
        // Zoom to layer
        $('.download-layer').on('click', function(e) {
            let $action_button = $(e.target);
            // Only create href link when it's not there so we don't have to run the same thing again and again
            if (!$action_button.attr('href') || $action_button.attr('href') === "javascript:void(0);") {
                if (!$action_button.hasClass('download-layer')) {
                    $action_button = $action_button.closest('.download-layer');
                }
                //Get File Name and replace spaces with underscore
                let layer_name = $action_button.closest('.layer-list-item').find('.display-name').html();
                if (typeof(layer_name) === 'string') {
                    layer_name =  layer_name.split(' ').join('_');
                }

                // Get layer_id
                let layer_id = $action_button.closest('.layer-list-item').find('.layer-visibility-control').data('layer-id');

                // Get feature
                let feature_layer = m_layers[layer_id];
                let features = feature_layer.getSource().getFeatures();

                // Write out feature to GeoJSON format
                let format = new ol.format.GeoJSON({featureProjection: 'EPSG:3857'});
                let json = format.writeFeatures(features);

                // Convert GeoJSON to shapefile. Note that shapefile only allows one shape type (point, line or polygon).
                // This method convert using the first shape type it finds.
                $.ajax({
                        type: 'POST',
                        url: '',
                        data: {'method': 'convert_geojson_to_shapefile',
                               'id': layer_id,
                               'data': json},
                        xhrFields: {
                            responseType: 'blob',
                        },
                        beforeSend: xhr => {
                            xhr.setRequestHeader('X-CSRFToken',  get_csrf_token());
                        }
                })
                .done(function(data) {
                    let url = window.URL || window.webkitURL;
                    url = url.createObjectURL(data);
                    // create a temporary element to put the href in and click on it on the first time.
                    // I need to do this since for some reason $action_button.click() does not work here.
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = layer_name + '.zip';
                    document.body.append(a);
                    a.click();
                    a.remove();
                    $action_button.attr("download", layer_name + '.zip');
                    $action_button.attr("href", url);
                })
            }
        });
    };

    init_collapse_control = function(group_id) {
        $('#' + group_id).on('click', function(e) {
        let $action_button = $(e.target);

        if (!$action_button.hasClass('collapse-action')) {
            $action_button = $action_button.closest('.collapse-action');
        }

        let $layer_group_item = $action_button.closest('.layer-group-item');
        let $layer_list = $layer_group_item.next('.layer-list');
        let is_collapsed = $layer_list.data('collapsed') || false;

        if (is_collapsed) {
            expand_section($layer_list.get(0));
            $layer_list.data('collapsed', false);
            $action_button.data('collapsed', false);
        }
        else {
            collapse_section($layer_list.get(0));
            $layer_list.data('collapsed', true);
            $action_button.data('collapsed', true);
        }
        });
    }

    init_collapse_controls = function() {
        $('.collapse-action').on('click', function(e) {
            let $action_button = $(e.target);

            if (!$action_button.hasClass('collapse-action')) {
                $action_button = $action_button.closest('.collapse-action');
            }

            let $layer_group_item = $action_button.closest('.layer-group-item');
            let $layer_list = $layer_group_item.next('.layer-list');
            let is_collapsed = $layer_list.data('collapsed') || false;

            if (is_collapsed) {
                expand_section($layer_list.get(0));
                $layer_list.data('collapsed', false);
                $action_button.data('collapsed', false);
            }
            else {
                collapse_section($layer_list.get(0));
                $layer_list.data('collapsed', true);
                $action_button.data('collapsed', true);
            }
        });
    };

    init_download_layer_controls = function() {
        // TODO: move init download action here...
    };

    init_add_layer_controls = function() {
        $('.add-layer-to-layer-group').on('click', function(e) {
            let $action_button = $(e.target);

            if (!$action_button.hasClass('add-layer-to-layer-group')) {
                $action_button = $action_button.closest('.add-layer-to-layer-group');
            }

            let $layer_label = $action_button.closest('.layers-context-menu').prev();
            let $display_name = $layer_label.find('.display-name').first();
            let $new_layer = $layer_label.parent().next().first();
            var uuid = generate_uuid();
            // Build Modal
            let modal_content = '<div class="form-group">'
                              + '<label class="sr-only" for="new-name-field">Layer Title:</label>'
                              + '<input class="form-control" type="text" id="new-name-field" style="margin-bottom:10px" placeholder="e.g.: State Population">'
                              + '<label class="sr-only" for="service-type">Map Service Type</label>'
                              + '<select class="form-control" style="margin-bottom:10px" id="service-type">'
                              + '<option value="WMS" selected>WMS</option>'
                              + '<option value="TileArcGISRest">ArcGIS Map Server</option>'
                              + '</select>'
                              + '<label class="sr-only" for="services-link">Service Link</label>'
                              + '<input class="form-control" type="text" id="services-link" placeholder="e.g.: https://example.com/geoserver/topp/wms">'
                              + '<label class="sr-only" for="service-layer-name">Layer Name</label>'
                              + '<input class="form-control" type="text" id="service-layer-name" placeholder="e.g.: topp:states" style="margin-top: 10px">'
                              + '</div>';

            let modal = build_action_modal('Add Layer', modal_content, 'Add', 'success');

            // Show Modal
            show_action_modal();

            // Handle Modal Action
            modal.action_button.on('click', function(e) {
                // Rename layer label
                let new_name = modal.content.find('#new-name-field').first().val();
                let service_type = modal.content.find('#service-type').first().val();
                let service_link =  modal.content.find('#services-link').first().val();
                let service_layer_name =  modal.content.find('#service-layer-name').first().val();
                
                var append_layer;
                if (service_type == "TileArcGISRest") {
                    append_layer =
                        new ol.layer.Tile({
                            source: new ol.source.TileArcGISRest({
                                url:service_link,
                            })
                        })
                }
                else {
                    append_layer =
                        new ol.layer.Tile({
                            source: new ol.source.TileWMS({
                                url:service_link,
                                params: {'service': service_type, 'version': '1.3.0', 'request': 'GetMap',
                                         'LAYERS': service_layer_name, 'TILED': true},
                                serverType: 'geoserver'
                            })
                        })
                }

                // todo: add layer attributes (id, variable, etc.)
                load_layers(
                    'layers-tab-panel', 
                    'Custom Layers', 
                    'custom_layers', 
                    [append_layer],
                    [new_name], 
                    ['12345'], // todo generate id
                    ['custom_layer'], // todo variable?
                    true  // todo show download?
                ); // todo: extent

                // Hide the modal
                hide_action_modal();
                init_new_layers_tab(uuid);

                // Save to resource
                csrf_token = $('input[name=csrfmiddlewaretoken]').val();
                $.ajax({
                    type: 'POST',
                    url: '',
                    data: {
                        'method': 'on_add_custom_layer',
                        'layer_title': new_name,
                        'layer_id': uuid,
                        'layer_name': service_layer_name,
                        'service_endpoint': service_link,
                        'service_type': service_type,
                    },
                    beforeSend: xhr => {
                        xhr.setRequestHeader('X-CSRFToken', csrf_token);
                    },
                }).done(function (data) {
                    if (data.success) {
                        TETHYS_APP_BASE.alert("success", `Successfully added layer "${service_layer_name}".`);
                    } else {
                        TETHYS_APP_BASE.alert("warning", `Unable to add layer permanently.`);
                        console.log(data.message);
                    }
                });
            });
        });

        // TODO: Save state to local storage
    };

    // Legend tab
    init_legends = function() {
        $('.map-layout-color-ramp-picker').each(function(index, select) {
            $(select).on('change', function(){
                var selected_style = $(select).find(':selected').val();
                var legend_wrapper = $(this).closest('.legend-wrapper');
                var legend_attrs = $(legend_wrapper).data('legend-attrs');

                // Reload layer with new style
                if (legend_attrs.type.includes('wms-legend')) {
                    update_layer_style(legend_attrs.layer_id, selected_style, legend_attrs.type);
                    update_wms_legend(legend_wrapper, legend_attrs, selected_style);
                } else if (legend_attrs.type === 'custom-divisions') {
                    update_division_legend_and_layer(legend_wrapper, legend_attrs, selected_style);
                }
            });
        });
    };

    update_layer_style = function(layer_id, new_style, style_type) {
        const existing_imagery_layer = m_layers[layer_id];
        const params = existing_imagery_layer.getSource().getParams();

        // Update appropriate parameter based on the style type
        if (style_type.includes('wms-legend')) {
            params['STYLES'] = new_style;
        } else if (style_type === 'geoserver-env-string') {
            params['ENV'] = new_style;
        }

        // Apply updated params
        existing_imagery_layer.getSource().updateParams(params);
    };

    update_result_layer = function(layer_id, color_ramp) {
        $.ajax({
            type: 'POST',
            url: ".",
            async: false,
            data: {
                'method': 'update_result_layer',
                'layer_id': JSON.stringify(layer_id),
                'color_ramp': JSON.stringify(color_ramp),
            },
        })
    };

    update_division_legend_and_layer = function(legend_wrapper, legend_attrs, new_color_ramp) {
        var color_ramp_component = $(legend_wrapper).find('.color-ramp-component');
        $.ajax({
            type: 'POST',
            url: ".",
            async: false,
            data: {
                'method': 'build_legend_item',
                'div_id': JSON.stringify(color_ramp_component.id),
                'minimum': JSON.stringify(legend_attrs.minimum),
                'maximum': JSON.stringify(legend_attrs.maximum),
                'color_ramp': JSON.stringify(new_color_ramp),
                'layer_id': JSON.stringify(legend_attrs.layer_id),
            },
        }).done(function(data){
            update_result_layer(`${data.layer_id}`, `${data.color_ramp}`);  // TODO: What to do with this?
            update_layer_style(data.layer_id, data.division_string, 'geoserver-env-string');
            $(`#${data.div_id}`).html(data.response);
        });
    };

    update_wms_legend = function(legend_wrapper, legend_attrs, new_style) {
        var wms_url = legend_attrs.url;
        var wms_legend_image = $(legend_wrapper).find('.wms-legend-image');
        if (legend_attrs.type.includes("thredds")) {
          wms_url += `&PALETTE=${new_style.replace('boxfill/', '')}`;
        } else {
          wms_url += `&STYLE=${new_style}`;
        }
        wms_legend_image.attr('src', wms_url);
    };

    show_legend = function(layer_id) {
        let safe_layer_id = layer_id.replace(':', '_').replace(',', '_');
        $("#legend-for-" + safe_layer_id).removeClass('hidden');
    };

    hide_legend = function(layer_id) {
        let safe_layer_id = layer_id.replace(':', '_').replace(',', '_');
        $("#legend-for-" + layer_id).addClass('hidden');
    };

    // Properties pop-up
    init_pop_up_overlay = function() {
        if (m_show_properties_popup || m_show_map_click_popup) {
          m_$props_popup_container = $('#properties-popup');
          m_$props_popup_content = $('#properties-popup-content');
          m_$props_popup_closer = $('#properties-popup-close-btn');

          // Create the overlay
          m_props_popup_overlay = new ol.Overlay({
            element: m_$props_popup_container.get(0),
            autoPan: {
                animation: {
                    duration: 250
                }
            }
          });

          m_map.addOverlay(m_props_popup_overlay);

          // Handle closer click events
          m_$props_popup_closer.on('click', function() {
            close_properties_pop_up();
            return false;
          });

          // Unset Display None
          m_$props_popup_container.css('display', 'block');
        }
    };

    init_map_clicked_pop_up = function() {
      if (m_show_map_click_popup) {
        $('#' + TETHYS_MAP_VIEW.getTarget()).on('clicked.tethys-map-view', function(event) {
          show_properties_pop_up(event.coordinate);
        });
      }
    };

    show_properties_pop_up = function(coordinates) {
        let c = coordinates;

        if (coordinates instanceof ol.geom.Point) {
            c = coordinates.getCoordinates();
        }
        m_$props_popup_container.trigger('show.map-layout.popup');
        m_props_popup_overlay.setPosition(c);
        m_$props_popup_container.trigger('shown.map-layout.popup');
    };

    hide_properties_pop_up = function() {
        m_$props_popup_container.trigger('hide.map-layout.popup');
        m_props_popup_overlay.setPosition(undefined);
        m_$props_popup_closer.blur();
        m_$props_popup_container.trigger('hidden.map-layout.popup');
    };

    close_properties_pop_up = function() {
        m_$props_popup_container.trigger('closing.map-layout.popup');
        hide_properties_pop_up();
        TETHYS_MAP_VIEW.clearSelection();
        if (m_show_map_click_popup) {
          TETHYS_MAP_VIEW.clearClickedPoint();
        }
        m_$props_popup_container.trigger('closed.map-layout.popup');
    };

    reset_properties_pop_up = function() {
        m_$props_popup_content.empty();
        hide_properties_pop_up();
    };

    append_properties_pop_up_content = function(content) {
        m_$props_popup_content.append(content);
    };

    on_select_vector_features = function(event) {
        let selected = event.selected;
        if (m_show_properties_popup && selected.length > 0) {
            display_properties(selected);
        }
    };

    on_select_wms_features = function(points_layer, lines_layer, polygons_layer) {
        let layers = [points_layer, lines_layer, polygons_layer];
        if (m_show_properties_popup) {
          display_properties(layers);
        }
    };

    display_properties = function(layers_or_features) {
        let center_points = [];

        // TODO: Add hook to allow apps to customize properties table.

        // Clear popup
        // TODO: This hides the pop-up when both Map Click and Properties Pop-up are On...
        reset_ui(false);

        for (var i = 0; i < layers_or_features.length; i++) {
            let layer_or_features = layers_or_features[i],
                features = [];

            if (layer_or_features && layer_or_features instanceof ol.Feature) {
                features = [layer_or_features];
                center_points.push(compute_center(features));
            }
            else if (layer_or_features && layer_or_features.getSource()
                && layer_or_features.getSource().getFeatures().length) {

                let source = layer_or_features.getSource();
                features = source.getFeatures();
                center_points.push(compute_center(features));
            }
            else {
                continue;
            }

            // Generate one table of properties for each node
            for (var j = 0; j < features.length; j++) {
                let feature = features[j];
                let layer_name = get_layer_name_from_feature(feature);
                let layer = m_layers[layer_name];

                // Generate Title
                let title_markup = generate_properties_table_title(feature, layer);
                append_properties_pop_up_content(title_markup);

                // Generate properties table
                let properties_table = generate_properties_table(feature, layer);
                append_properties_pop_up_content(properties_table);

                // Generate custom content
                let custom_content = generate_custom_properties_table_content(feature, layer);
                append_properties_pop_up_content(custom_content);
                initialize_custom_content();

                // Generate plot button
                let plot_button = generate_plot_button(feature, layer);
                append_properties_pop_up_content(plot_button);
                bind_plot_buttons();

                // Generate plot button
                let action_button = generate_action_button(feature, layer);
                append_properties_pop_up_content(action_button);
                bind_action_buttons();
            }
        }

        // Compute popup location
        if (!m_show_map_click_popup) {
          let popup_location = compute_center(center_points);

          // Show the Popup
          if (popup_location) {
              show_properties_pop_up(popup_location);
          }
        }

        // TODO: Add hook to allow apps to customize properties table.
    };

    reset_ui = function(clear_selection=true) {
        // Clear selection
        if (clear_selection) {
            TETHYS_MAP_VIEW.clearSelection();
        }

        // Reset popup
        if (m_show_properties_popup) {
            reset_properties_pop_up();
        }

        // Hide plot slide sheet
        hide_plot();
    };

    generate_properties_table_title = function(feature, layer) {
        let title = '';

        // Get custom title from layer data properties
        if (layer.hasOwnProperty('tethys_data') && layer.tethys_data.hasOwnProperty('popup_title')) {
            title = layer.tethys_data.popup_title;
        }
        // Or use the legend title as a fallback
        else {
            title = layer.tethys_legend_title;
        }

        let title_markup = '<h6 class="properites-title">' + title + '</h6>';
        return title_markup;
    };

    generate_properties_table = function(feature, layer) {
        let properties = feature.getProperties();
        let geometry = feature.getGeometry();
        let geometry_type = geometry.getType().toLowerCase();
        let feature_class = (('type' in properties) ? properties['type'] : geometry_type);
        let layer_data = layer.tethys_data || {};
        let excluded_properties = ['geometry', 'the_geom'];
        let extra_table_content = '';

        // Get custom excluded properties
        if (layer_data.hasOwnProperty('excluded_properties')) {
            excluded_properties = excluded_properties.concat(layer_data.excluded_properties);
        }

        // Templates
        let kv_row_template = '<tr><td>{{KEY}}</td><td>{{VALUE}}&nbsp;<span id="{{ELEMENT_CLASS}}-{{PROPERTY}}-units"></span></td></tr>';
        kv_row_template = kv_row_template.replace('{{ELEMENT_CLASS}}', feature_class);
        let table_template = '<table class="table table-condensed table-striped {{CLASS}}">{{ROWS}}</table>';

        // Initial rows
        let rows = '';

        // Append the type of feature
        if (!excluded_properties.includes('type')) {
            rows += kv_row_template
                    .replace('{{KEY}}', 'Type')
                    .replace('{{VALUE}}', geometry.getType())
                    .replace('{{PROPERTY}}', 'type');
        }

        // Build property rows
        for(var property in properties) {
            // Skip excluded properties
            if (in_array(property, excluded_properties)) {
                continue;
            }

            let value = properties[property];

            // If value is an object, build row with appropriate method
            if (value instanceof Object) {
                if (value.hasOwnProperty('type') && value.hasOwnProperty('value') && value.type == 'dataset') {
                    rows += generate_dataset_row(property, value.value);
                } else {
                    console.log('WARNING: Unable to load property row - ' + var_to_title_case(property) + ': ' + value);
                }

            // Otherwise, build simple valued row
            } else {
                // Build row
                rows += kv_row_template
                    .replace('{{KEY}}', var_to_title_case(property))
                    .replace('{{VALUE}}', value)
                    .replace('{{PROPERTY}}', property);
            }

        }

        // Compose table
        if (rows.length) {
            table_template = table_template.replace('{{CLASS}}', feature_class);
            table_template = table_template.replace('{{ROWS}}', rows);
            return table_template;
        }
        else {
            return '';
        }
    };

    generate_dataset_row = function(property, dataset) {
        let dataset_row_template = '<tr><td colspan="2">{{VALUE}}</td></tr>';
        let row = '';
        let dataset_table = '<table class="table">';
        let dataset_table_row_template = '<tr>{{COLUMNS}}</tr>';

        // Get dataset metadata
        let columns = dataset.meta.columns;
        let length = dataset.meta.length;

        // Add dataset title
        row += dataset_row_template.replace('{{VALUE}}', var_to_title_case(property));

        // Add column header row
        let header_columns = '';
        let dataset_table_header_template = '<th>{{VALUE}}</th>';

        $.each(columns, function(index, col) {
            header_columns += dataset_table_header_template.replace('{{VALUE}}', col);
        });

        dataset_table += dataset_table_row_template.replace('{{COLUMNS}}', header_columns);

        // Add value rows
        let value_rows = '';
        let dataset_table_column_template = '<td>{{VALUE}}</td>';

        for (var i = 0; i < length; i++) {
            let row_columns = '';

            $.each(columns, function(index, col) {
                let val = dataset[col][i];
                row_columns += dataset_table_column_template.replace('{{VALUE}}', val);
            });

            value_rows +=  dataset_table_row_template.replace('{{COLUMNS}}', row_columns);
        }

        dataset_table += value_rows;

        // Close out dataset table
        dataset_table += '</table>';
        // Add row containing the dataset table
        row += dataset_row_template.replace('{{VALUE}}', dataset_table);


        return row;
    };

    generate_custom_properties_table_content = function(feature, layer) {
        // Use public API to override this method to add custom content to the properties popup for selected featuress.
        return '';
    };

    initialize_custom_content = function() {
        // Use public API to override this method with custom operations to perform after custom content has been rendered.
    };

    // Generate UUID
    generate_uuid = function () {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }


    // Feature Selection
    init_feature_selection = function() {
      TETHYS_MAP_VIEW.overrideSelectionStyler('points', points_selection_styler);
      TETHYS_MAP_VIEW.overrideSelectionStyler('lines', lines_selection_styler);
      TETHYS_MAP_VIEW.overrideSelectionStyler('polygons', polygons_selection_styler);
      // Bind wms select method
      TETHYS_MAP_VIEW.onSelectionChange(on_select_wms_features);

      // Bind vector select methods
      let select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();
      if (select_interaction){
        select_interaction.on('select', on_select_vector_features);
      }
    };

    points_selection_styler = function(feature, resolution) {
        return [new ol.style.Style({
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: SELECTED_POINT_COLOR
                }),
                stroke: new ol.style.Stroke({
                    color: 'white',
                    width: 1
                })
            })
        })];
    };

    lines_selection_styler = function(feature, resolution) {
        return [
            new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#ffffff',
                    width: 6
                })
              }
            ), new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: SELECTED_LINE_COLOR,
                    width: 4
                })
              }
            )
        ];
    };

    polygons_selection_styler = function(feature, resolution) {
        return [
            new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#ffffff',
                    width: 6
                }),
                fill: new ol.style.Fill({
                    color: 'rgba(115, 0, 229, 0.1)'
                })
              }
            ), new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: SELECTED_LINE_COLOR,
                    width: 4
                })
              }
            )
        ];
    };

 	// Geocode Methods
    init_geocode = function() {
        if (p_can_geocode) {
            // Add Geocode Control to OpenLayers controls container
            var $geocode_wrapper = $('#map-geocode-wrapper');
            var $overlay_container = $('.ol-overlaycontainer-stopevent');
            $overlay_container.append($geocode_wrapper);

            // Initialize select2 search field
            var $geocoder = $('#geocode_select');
            $geocoder.select2({
                theme: "bootstrap-5",
                dropdownParent: $("#geocode_select").parent(),
                minimumInputLength: 3,
                placeholder: "Search",
                allowClear: true,
                maximumSelectionLength: 1,
                ajax: {
                    url: '.',
                    delay: 2000,
                    type: 'POST',
                    data: function (params) {
                        return {
                            'method': 'find-location-by-query',
                            'q': params.term, // search term
                        };
                    },
                    processResults: function (data, params) {
                        m_geocode_objects = data.results;
                        return {
                            results: data.results,
                        };
                    }
                }
            });

            // Bind to on change event
            $geocoder.on('select2:select', do_geocode);
            $geocoder.on('select2:unselect', clear_geocode);
        }
    };

    do_geocode = function(event) {
      // Add classes For styling
      var $search_field = $(".select2-search.select2-search--inline");
      var i;

      $search_field.addClass("geocode-item-selected");

      // Get the point and add it to the map, also zoom to it's extent
      if (is_defined(m_geocode_objects)) {
          for (i = 0; i < m_geocode_objects.length; i++) {
              if (m_geocode_objects[i].id == $(event.target).val()) {
                  var selected_point = m_geocode_objects[i].point;
                  var selected_bbox = m_geocode_objects[i].bbox;

                  // Add point to the map
                  var geocode_source = new ol.source.Vector({
                      features: [
                          new ol.Feature({
                              geometry: new ol.geom.Point(ol.proj.transform(
                                  selected_point, 'EPSG:4326', 'EPSG:3857'
                              )),
                          }),
                      ],
                  });

                  if (is_defined(m_geocode_layer)) {
                      m_geocode_layer.setSource(geocode_source);
                  } else {
                      // Setup Map Layer
                      var fill = new ol.style.Fill({
                          color: 'rgba(255,0,0,0.9)'
                      });
                      var stroke = new ol.style.Stroke({
                          color: 'rgba(255,255,255,1)',
                          width: 2
                      });
                      var geocode_style = new ol.style.Style({
                          image: new ol.style.Circle({
                              fill: fill,
                              stroke: stroke,
                              radius: 8
                          }),
                          fill: fill,
                          stroke: stroke
                      });

                      m_geocode_layer = new ol.layer.Vector({
                          source: geocode_source,
                          style: geocode_style
                      });

                      m_map.addLayer(m_geocode_layer);
                  }

                  // Zoom to the bounding box provided
                  TETHYS_MAP_VIEW.zoomToExtent(selected_bbox);
              }
          }
      } else {
          console.error("No Geocode objects defined.")
      }
    };

    clear_geocode = function(event) {
        // Remove classes For styling
        var $search_field = $(".select2-search.select2-search--inline");
        $search_field.removeClass("geocode-item-selected");

        // Clear the map
        if (is_defined(m_geocode_layer)) {
          var source = m_geocode_layer.getSource();
          var features = source.getFeatures();
          if (features != null && features.length > 0) {
             for (var x in features) {
                source.removeFeature(features[x]);
             }
          }
        }
    };

    // Cache methods
    add_to_cache = function(cache, key, obj) {
        cache[key] = obj;
    };

    get_from_cache = function(cache, key) {
        if (is_in_cache(cache, key)) {
            return cache[key];
        }
    };

    is_in_cache = function(cache, key) {
        if (key in cache) {
            return true;
        }
        else {
            return false;
        }
    };

    remove_from_cache = function(cache, key) {
        if (is_in_cache(cache, key)) {
            delete cache[key];
        }
    };

    // Drawing methods
    init_draw_controls = function() {
        var left_position = 7,
            LEFT_POSITION_OFFSET = 42;
        $('.tethys-map-view-draw-control').each(function(index, control) {
            // Reset position of draw controls so they are left aligned on the bottom.
            $(control).css('left', left_position + 'px');
            $(control).css('bottom', '7px');
            $(control).css('top', 'auto');
            left_position += LEFT_POSITION_OFFSET;
        });

        // Reset tooltips to show on top
        $('[data-toggle="tooltip"]').tooltip('destroy');
        $('[data-toggle="tooltip"]').tooltip({'placement': 'top'});
    };

    // Create new layer groups with layers
    // This method allows user to create tree items and have them linked to the tree items created in this method.
    load_layers = function (tab_id, layer_group_name, layer_group_id, layer_data, layer_names, layer_ids, layer_legends, show_download) {
        // tab_id: name of the tab layer group
        // layer_group_name: name of the layer group - Ex: My Layer Group
        // layer_group_id: id of the layer group - Ex: my_layer_group_123456
        // layer_data: list of openlayer layers
        // layer_names: list of the name of the openlayer layers
        // layer_ids: list of the id of the open layer layers
        // layer_legends: list of the legend name of the open layer layers Ex: my-legend -> your legend id is going to be (#legend-my-legend)
        // Add layers to map
        var i = 0;
        if (tab_id == "") {
            tab_id = "layers-tab-panel"
        }
        for (i = 0; i < layer_data.length; i++) {
            m_layers[layer_ids[i]] = layer_data[i];
            m_map.getLayers().insertAt(i + 1, layer_data[i]);
        }
        var operation = 'create'
        // If the layer group is already created, we will have the solution added to the same layer groups
        if ($('#' + layer_group_id).length){
            operation = 'append'
        }
        $.ajax({
            type: 'POST',
            url: ".",
            async: false,
            data: {
                'method': 'build_layer_tree_item',
                'operation': operation,
                'layer_group_id': layer_group_id,
                'layer_group_name': layer_group_name,
                'layer_names': JSON.stringify(layer_names),
                'layer_ids': JSON.stringify(layer_ids),
                'layer_legends': JSON.stringify(layer_legends),
                'show_download': JSON.stringify(show_download),
            },
        }).done(function(data){
            if (operation == 'create') {
                $('#' + tab_id).append(data.response);
            } else {
                $('#' + layer_group_id + '_associated_layers').append(data.response);
            }
            init_new_layers_tab(layer_group_id);
        });
        
    };

    hide_layers = function(layer_ids) {
        for (var i=0; i < layer_ids.length; i++) {
            // Set layer to be visible first
            m_layers[layer_ids[i]].setVisible(false);

            // uncheck the layer if we hide it
            $('.layer-visibility-control[data-layer-id="' + layer_ids[i] + '"]')[0].checked = false;
            // Find the correct layer-list-item and add hidden class
            $('[data-layer-id="' + layer_ids[i] + '"]').first().closest("li").addClass("hidden");

        }
    };

    show_layers = function(layer_ids) {
        for (var i=0; i < layer_ids.length; i++) {
            // Find the correct layer-list-item and remove hidden class
            $('[data-layer-id="' + layer_ids[i] + '"]').first().closest("li").removeClass("hidden")

        }
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
	m_public_interface = {
	    /*
	     * Override the default properties table generator
	     */
	    properties_table_generator: function(f) {
	        generate_properties_table = f;
	    },
	    custom_properties_generator: function(f) {
	        generate_custom_properties_table_content = f;
	    },
	    custom_properties_initializer: function(f) {
	        initialize_custom_content = f;
	    },
	    action_button_generator: function(f) {
	        generate_action_button = f;
	    },
	    action_loader: function(f) {
	        load_action = f;
	    },
	    get_plot: () => { return m_plot; },
	    show_plot: show_plot,
	    hide_plot: hide_plot,
	    update_plot: update_plot,
	    plot_button_generator: function(f) {
	        generate_plot_button = f;
	    },
	    plot_loader: function(f) {
	        load_plot = f;
	    },
	    post_update_plot_callback: function(f) {
	        post_update_plot = f;
	    },
        get_layer_name_from_feature: get_layer_name_from_feature,
        get_layer_id_from_layer: get_layer_id_from_layer,
        get_feature_id_from_feature: get_feature_id_from_feature,
        show_properties_pop_up: show_properties_pop_up,
        hide_properties_pop_up: hide_properties_pop_up,
        reset_properties_pop_up: reset_properties_pop_up,
        close_properties_pop_up: close_properties_pop_up,
        load_layers: load_layers,
        update_legend: update_legend,
        hide_layers: hide_layers,
        show_layers: show_layers,
        remove_layer_from_map: remove_layer_from_map,
        init_layers_tab: init_layers_tab,
        init_download_layer_action: init_download_layer_action,
	};

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
	    // Load config
	    parse_permissions();
	    parse_attributes();

	    // Setup
	    setup_ajax();
	    setup_map();

		// Initialize
		init_layers_tab();
		init_legends();
        init_geocode();
        init_plot();
        init_draw_controls();
        init_download_layer_action();
        sync_layer_visibility();
        init_pop_up_overlay();
        init_map_clicked_pop_up();
	});

	return m_public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
