/*****************************************************************************
 * FILE:    tethys_map_view.js
 * DATE:    21 April 2014
 * AUTHOR: Scott D. Christensen
 * COPYRIGHT: (c) 2014 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var MAP_VIEW = (function() {
  // Wrap the library in a package function
  "use strict"; // And enable strict mode for this library
  
  /************************************************************************
    * MODULE LEVEL / GLOBAL VARIABLES / PRIVATE VARIABLES / INSTANCE VARIABLES
    *************************************************************************/
   var ge,                   // Default overlay value
       viewer,               // MapView instance
       viewerOptions,        // Options configured in API
       publicInterface;      // Library object that is returned        

  /************************************************************************
    *                    PRIVATE FUNCTION DECLARATIONS
    *************************************************************************/
    
    //----------------------------------------------------------------------------------------------------
    //
    //  Utilities
    //
    //----------------------------------------------------------------------------------------------------    
    
    function bind(fn, context){
      return function(){
        fn.apply(context,arguments);
      };
    }
    
    // creates a global "addWheelListener" method
    // example: addWheelListener( elem, function( e ) { console.log( e.deltaY ); e.preventDefault(); } );
    (function(window,document) {
    
        var prefix = "", _addEventListener, onwheel, support;
    
        // detect event model
        if ( window.addEventListener ) {
            _addEventListener = "addEventListener";
        } else {
            _addEventListener = "attachEvent";
            prefix = "on";
        }
    
        // detect available wheel event
        support = "onwheel" in document.createElement("div") ? "wheel" : // Modern browsers support "wheel"
                  document.onmousewheel !== undefined ? "mousewheel" : // Webkit and IE support at least "mousewheel"
                  "DOMMouseScroll"; // let's assume that remaining browsers are older Firefox
    
        window.addWheelListener = function( elem, callback, useCapture ) {
            _addWheelListener( elem, support, callback, useCapture );
    
            // handle MozMousePixelScroll in older Firefox
            if( support == "DOMMouseScroll" ) {
                _addWheelListener( elem, "MozMousePixelScroll", callback, useCapture );
            }
        };
    
        function _addWheelListener( elem, eventName, callback, useCapture ) {
            elem[ _addEventListener ]( prefix + eventName, support == "wheel" ? callback : function( originalEvent ) {
                !originalEvent && ( originalEvent = window.event );
    
                // create a normalized event object
                var event = {
                    // keep a ref to the original event object
                    originalEvent: originalEvent,
                    target: originalEvent.target || originalEvent.srcElement,
                    type: "wheel",
                    deltaMode: originalEvent.type == "MozMousePixelScroll" ? 0 : 1,
                    deltaX: 0,
                    delatZ: 0,
                    preventDefault: function() {
                        originalEvent.preventDefault ?
                            originalEvent.preventDefault() :
                            originalEvent.returnValue = false;
                    }
                };
                
                // calculate deltaY (and deltaX) according to the event
                if ( support == "mousewheel" ) {
                    event.deltaY = - 1/40 * originalEvent.wheelDelta;
                    // Webkit also support wheelDeltaX
                    originalEvent.wheelDeltaX && ( event.deltaX = - 1/40 * originalEvent.wheelDeltaX );
                } else {
                    event.deltaY = originalEvent.detail;
                }
    
                // it's time to fire the callback
                return callback( event );
    
            }, useCapture || false );
        }
    
    })(window,document);
    
    
    //----------------------------------------------------------------------------------------------------
    //
    //  Definition of GE_Viewer Class
    //
    //----------------------------------------------------------------------------------------------------
    
    var MapView = function(legendOn, legendOptions){
        this.setBindings();
        
        this.div = $('#map-view');
        this.map = $( '#map-view-map' );
        this.divider = $('#map-view-divider');
        this.handle = $('#map-view-handle'); 
        
        this.container = $('#map-view-container');
        this.fullscreenBtn = $('#map-view-fullscreen');
        this.fullscreen = false;
        
        this.loading = $('#map-view-loading');
        
        this._setDimensions();
        
        this.legend = new Legend(this, legendOptions);
        this.legendVisible = false;
        
        if(legendOn){
          this.showLegend();
        }
        else{
          this.legend.detach();
          this.legend = null;
          this.divider.detach();
        }
        
        this.setListeners();
    };
    
    MapView.prototype = {
      
      getHeight: function(){
        return this.height;
      },
      
      getWidth: function(){
        return this.width;
      },
      
      getLegend: function(){
        return this.legend;
      },
      
      showLoading: function(){
        this.loading.show();
      },
      
      hideLoading: function(){
        this.loading.hide();
      },
      
      _setDimensions: function(){
        this.height = this.div.height();
        this.width = this.div.width();
        this.containerHeight = this.container.height();
        this.containerWidth = this.container.width();
      },
      
      toggleFullscreen: function(){
        
        if(this.fullscreen){
          this.fullscreen = false;
          //undo fullscreen
          this.div.css({'position':'relative',
                        'z-index':'0',
                        'height':'100%',
                        'width':'100%'});
          
          $('body').css('overflow','auto'); 
                    
          this.fullscreenBtn.attr('src', 'http://earth-api-samples.googlecode.com/svn/trunk/external/dinther_fullscreen_tofull.png' );
        }
        else{
          this.fullscreen = true;
          this.div.css({'position':'fixed',
                        'z-index':'1001',
                        'height':'100%',
                        'width':'100%',
                        'top':'0',
                        'left':'0'});
          
          $('body').css('overflow','hidden');  
               
          this.fullscreenBtn.attr('src', 'http://earth-api-samples.googlecode.com/svn/trunk/external/dinther_fullscreen_tonormal.png' );
        }
        
        
        this._setDimensions();             
        var x = parseInt(this.divider.css('left'));           
        this.resize(x);
      },
      
      resize: function(x){
        var legend = this.legend.legend;
        var resizeBuffer = this.width * .1;
        var maxX = this.width - resizeBuffer;
        var minX = resizeBuffer;
        
        if(x > maxX)
          x = maxX;
        else if(x < minX)
          x = minX;
          
        if(this.legendVisible)
        {
          this.divider.css('left', x);
          this.map.width(this.width - x);
          legend.width(x);
        }
        else if(legend.width() > maxX)
        {
          legend.width(maxX);
          legend.css('margin-left', -maxX);
          this.map.width(this.width);
        }
      },
      
      showLegend: function(){
        this.legendVisible = true;
        var that = this;
        this.divider.mousedown(
          function(e){
            that.handle.addClass('map-view-handle-visible');
            $(document).mousemove(
              function(e){
                var leftOffset = that.div.offset().left; 
                var x = e.pageX - leftOffset;
                that.resize(x);
            });
        });
        this.handle.off('dblclick',this.showLegend);
        this.handle.dblclick(this.hideLegend);
        this.handle.find('i').toggleClass('icon-chevron-left icon-chevron-right');
        var left = -parseInt(this.legend.legend.css('margin-left'));
        var mapWidth = (this.width - left);
        var easing = 'swing';
        this.legend.legend.animate({marginLeft:0},'100',easing);
        this.divider.animate({left:left},'100',easing);
        this.map.animate({width:mapWidth},'100',easing);
      },
     
      hideLegend: function(){
        this.legendVisible = false;
        this.divider.off('mousedown');
        this.handle.off('dblclick',this.hideLegend);
        this.handle.dblclick(this.showLegend);
        this.handle.find('i').toggleClass('icon-chevron-right icon-chevron-left');
        var left = parseInt(this.divider.css('left'));
        var easing = 'swing';
        this.legend.legend.animate({marginLeft:'-' + left},'100',easing);
        this.divider.animate({left:-1},'100',easing);
        this.map.animate({width:'100%'},'100',easing);
      },
      
      addLayer: function(kmlUrl){
        var that = this;
        var feature;
        google.earth.fetchKml(ge, kmlUrl, function(kmlObj) {
          ge.getFeatures().appendChild(kmlObj);
          feature = new Feature(kmlObj);
          feature.zoomToLayer();
          
          if(that.legend){
            that.legend.addLayer(feature);
          }
        });
      },
      
      setBindings: function(){
        this.toggleFullscreen = bind(this.toggleFullscreen, this);
        this.resize = bind(this.resize, this);
        this.showLegend = bind(this.showLegend, this);
        this.hideLegend = bind(this.hideLegend, this);
        this.addLayer = bind(this.addLayer, this);
      },
      
      setListeners: function(){
        var that = this;
        
        $(window).resize(
          function(e){
            that._setDimensions();
            var x = parseInt(that.divider.css('left'));
            that.resize(x);
        });
         
        $(document).mouseup(
          function(){
            $(document).off('mousemove');
            that.handle.removeClass('map-view-handle-visible');
        });
        
        that.fullscreenBtn.click(that.toggleFullscreen);
      }
    };
    
    //----------------------------------------------------------------------------------------------------
    //
    //  Definition of Legend Class
    //
    //----------------------------------------------------------------------------------------------------
    
    var Legend = function(map, options){
      this.init(map, options);
    };
    
    Legend.prototype = {
      init: function(map, options){
        this.setBindings();
        
        this.map = map;
        this.legend = $('#map-view-legend');
        this.tree = $('#map-view-tree');
        this.container = {content: this.tree};
        
        this.header = $('#map-view-legend-header');
        this.headerHeight = this.header.height();
        this.MAX_TREE_TOP = 0;
        
        this.urlField = $("#map-view-url-field");
        this.addLayerForm = $('#map-view-add-modal');
        
        if(!options.addLayers){
          $('#map-view-add-button').detach();
        }
        
        this.setListeners();
      },
      
      scrollTree: function(e){
        var delta = -e.deltaY;
        var treeTop = parseInt(this.tree.css('margin-top'));
        var newTreeTop = treeTop + delta;
        
        var treeHeight = this.tree[0].scrollHeight;
        var minTreeTop = this.map.getHeight() - treeHeight - this.headerHeight;
        //minTreeTop = minTreeTop > this.MAX_TREE_TOP ? this.MAX_TREE_TOP : minTreeTop;
        
        if(newTreeTop > this.MAX_TREE_TOP  || minTreeTop > this.MAX_TREE_TOP)
        {
          newTreeTop = this.MAX_TREE_TOP;
        }
        else if(newTreeTop < minTreeTop)
        { 
          newTreeTop = minTreeTop; 
        }
    
        this.tree.css('margin-top',newTreeTop);
        
        e.preventDefault();
      },
      
      addLayer: function(feature){
        var loading = this.map.loading.clone().css('position','static').appendTo(this.tree);
        var that = this;
        setTimeout(function(){
          that._traverse(that.container,feature);
          loading.detach();
        },1000);
        
      },
      
      //Should the feature traversing happen in the Feature class?
      _traverse: function(parentContainer,parent)
      {
        var container = new Container(parentContainer, parent);
        var that = this;
        //setTimeout(function(){
          if(parent.hasChildren()){
            var childFeatures = parent.children;
            var child = childFeatures.getFirstChild();
            do{
              var childFeature = new Feature(child);
              that._traverse(container,childFeature);
            }while(child = child.getNextSibling());  
          }
        //},1000);
      },
      
      detach: function(){
        this.legend.detach();
      },
      
      setBindings: function(){
        this.scrollTree = bind(this.scrollTree,this);
        this.addLayer = bind(this.addLayer, this);
        this._traverse = bind(this._traverse, this);
      },
      
      setListeners: function(){
        addWheelListener( this.legend[0], this.scrollTree );
        
        var that = this;
        $('#map-view-add-layer-btn').click(
          function(){
            $('#map-view-add-modal').modal('hide');
            var val = that.urlField.val();
            that.urlField.val('');
            that.map.addLayer(val);
        });
      }
    };
    
    
    //----------------------------------------------------------------------------------------------------
    //
    //  Definition of Feature Class
    //
    //----------------------------------------------------------------------------------------------------
    var Feature = function(kmlFeature){
      this.init(kmlFeature);
    };
    
    
    Feature.prototype = {
      
      init: function(kmlFeature){
        this.setBindings();
      
        this.kmlFeature = kmlFeature;
        this.name = kmlFeature.getName();
        this.url = kmlFeature.getUrl();
        this.children = this.getChildren();
        this.TYPES = ['KmlDocument','KmlFolder','KmlPlacemark'];
      },
      
      getType: function(){
        return this.kmlFeature.getType();
      },
      
      isPlacemark: function(){
        //console.log(this.TYPES[2]);
        return this.getType() === 'KmlPlacemark';
      },
      
      getOpacity: function(){
        return this.kmlFeature.getOpacity();
      },
      
      setOpacity: function(opacity){
        this.kmlFeature.setOpacity(opacity);
      },
      
      getChildren: function(){
        if(!this.isPlacemark())
          try{
            this.children = this.kmlFeature.getFeatures();
            this.children.getFirstChild();
            return this.children;
          }catch(err){}
        else
          return null;
      },
      
      hasChildren: function(){
        return this.children != null;
      },
      
      show_hide: function(bool){
        var toggle = !this.kmlFeature.getVisibility();
        this.kmlFeature.setVisibility(toggle);
      },
      
      getFillColor: function(){
        //console.log(this.kmlFeature.getStyleUrl());
        function componentToHex(c) {
          var hex = c.toString(16);
          return hex.length == 1 ? "0" + hex : hex;
        }
        
        function rgbToHex(r, g, b) {
            return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
        }
        
        var kmlColor = this.kmlFeature.getComputedStyle().getPolyStyle().getColor();
        var r = kmlColor.getR();
        var g = kmlColor.getG();
        var b = kmlColor.getB();
        
        //return 'rgb(' + r + ',' + g + ',' + b + ')';
        return rgbToHex(r,g,b);
       },
       
       setFillColor: function(color){
         
         var r = color.substring(1,3);
         var g = color.substring(3,5);
         var b = color.substring(5,7);
         var kmlColorString = 'ff' + b + g + r;
         
         var kmlColor = this.kmlFeature.getComputedStyle().getPolyStyle().getColor();
         
         kmlColor.set(kmlColorString);
       },
       
       zoomToLayer: function(){
         zoomToLayer(this.url);
         
         //hack for when kmlObj don't have a view set
         function zoomToLayer(url){
                  
            var link, networkLink;
            
            // Load KML URL into Google Earth Instance
            link = ge.createLink('');
            link.setHref(url);
            
            networkLink = ge.createNetworkLink('');
            networkLink.set(link, true, true);  // Sets the link, refreshVisibility, and flyToView
            ge.getFeatures().appendChild(networkLink);
            setTimeout(function(){ge.getFeatures().removeChild(networkLink);},50);
          }
       },
      
      remove: function(){
        this.kmlFeature.getParentNode().getFeatures().removeChild(this.kmlFeature);
      },
      
      setBindings: function(){
        this.show_hide = bind(this.show_hide, this);
      }
    }; 
      
      
    
      
    //----------------------------------------------------------------------------------------------------
    //
    //  Definition of Container (and related) Classes
    //
    //----------------------------------------------------------------------------------------------------
    var Container = function(parent,kml){
      this.setBindings();
      
      this.kml = kml;
      this.div = $('<div />', { class: 'map-view-legend-elem-container'}).appendTo(parent.content);
      if(kml.isPlacemark()){
        this.header = new Placemark(this,kml);
      }
      else{
        this.header = new Header(this,kml);  
      }
      this.content = $('<div />', { class: 'map-view-legend-elem-content'}).appendTo(this.div);
    };
   
    Container.prototype = {
    
      expand_collapse: function(){
        this.header.handle.toggleClass("map-view-expanded map-view-collapsed");  
        this.content.slideToggle(500);
      },
    
      remove: function(){
        this.kml.remove();
        this.div.detach();
      },
    
      zoomToLayer: function(){
        this.kml.zoomToLayer();
      },
      
      setBindings: function(){
        this.expand_collapse = bind(this.expand_collapse,this);
        this.remove = bind(this.remove,this);
        this.zoomToLayer = bind(this.zoomToLayer,this);
      }
    };
    
    var Header = function(parent,kml){
      this.div = $('<div />', { class: 'map-view-legend-elem-header'}).appendTo(parent.div);
      this.handle = $('<i />', { class: 'icon-chevron-right map-view-expanded'})
        .click(parent.expand_collapse)
        .appendTo(this.div);
      this.cb = $('<input />', { type: 'checkbox', checked: true, text: name })
        .click(kml.show_hide)
        .appendTo(this.div);
      //this.label = $('<label />', { class: 'checkbox', 'for': this.cb, 'text': kml.name, 'title': kml.url })
       // .tooltip()
      this.name = $('<span />', {class: 'map-view-name', text: kml.name})
        .appendTo(this.div);
      this.options = new Options(parent,this.div,kml);
    };
    
    var Placemark = function(parent,kml){
      this.kml = kml;
      this.div = $('<div />', { class: 'map-view-legend-elem-placemark'}).appendTo(parent.div);
      this.cb = $('<input />', { type: 'checkbox', checked: true, text: name })
        .click(kml.show_hide)
        .appendTo(this.div);
      this.style = $('<span />', { class: 'map-view-style'})
        .css(this.getStyleCss())
        .appendTo(this.div);
      //this.label = $('<label />', { class: 'checkbox', 'for': this.cb, 'text': kml.name, 'title': kml.url })
       // .tooltip()
      this.name = $('<span />', { class: 'map-view-name', text: kml.name})
        .appendTo(this.div);
      this.options = new Options(parent,this.div,kml);
    };
    
    Placemark.prototype = {
      
      getStyleCss: function(){
        var fill =  this.kml.getFillColor();
        return {"background-color":fill};
      },
      
      setStyleCss: function(fill){
        this.style.css({"background-color":fill});
      }
    };
    
    var Options = function(container, div, kml){
      this.setBindings();
    
      this.container = container;
      this.kml = kml;
      this.btn_group = $('<div />', { class: 'btn-group map-view'})
        .appendTo(div);
      this.button = $('<a />', { class: 'btn btn-default btn-mini dropdown-toggle map-view-options-btn', type: 'button', 'data-toggle': 'dropdown'})
        .click(this.calculateMenuDirection)
        .appendTo(this.btn_group);
          $('<span />', {class: 'caret'}).appendTo(this.button);
      this.menu = $( '<ul />', {class: 'dropdown-menu map-view', role: 'menu'})
        .appendTo(this.btn_group);
          $( '<li><a href="#">Remove</a></li>')
            .click(container.remove)
            .appendTo(this.menu);
          $( '<li><a href="#">Zoom To Layer</a></li>')
            .click(container.zoomToLayer)
            .appendTo(this.menu);
          $( '<li class="divider"></li>')
            .appendTo(this.menu);
          $( '<li class=""><a href="#">Properties</a></li>')
            .click(this.configureLayerPropertiesDialog)
            .appendTo(this.menu);
    };
    
    Options.prototype = {
      
      calculateMenuDirection: function(event){
        var viewerOffset = viewer.getHeight() + viewer.div.offset().top;
        var menuHeight = this.menu.outerHeight(true);
        var btnPosition = this.button.offset().top;
        var menuBottom = btnPosition + this.button.height() + menuHeight;
        if(menuBottom > viewerOffset)
        {
          this.menu.parent().addClass('dropup');
        }
        else
        {
          this.menu.parent().removeClass('dropup');
        }
      },
      
      configureLayerPropertiesDialog: function(){
        var header = this.container.header;
        var kml = this.kml;
        
        var content = $('#map-view-layer-properties-modal-content');
        content.empty();
        
        var opacity = this.kml.getOpacity();
        content.append($('<label for="map-view-opacity">Opacity</label>'));
        var opacitySlider = $('<input />',{id:'map-view-opacity', type:"range", min:"0", max:"1", step:".01", value: opacity})
        .appendTo(content)
        .change(function(){
          opacity = parseFloat(this.value);
          kml.setOpacity(opacity);
          //that.container.header.setStyleCss(color);
        });
        
        
        if(this.container.header instanceof Placemark){
          var color = this.kml.getFillColor();
          
          content.append($("<label for='map-view-color'>Color</label>"));
          var colorPicker = $('<input />',{type:'color', value: color})
          .appendTo(content)
          .change(function(){
            color = this.value;
            kml.setFillColor(color);
            header.setStyleCss(color);
          });
        }
        
        $('#map-view-layer-properties-modal').modal('show');
      },
      
      setBindings: function(){
        this.calculateMenuDirection = bind(this.calculateMenuDirection, this);
        this.configureLayerPropertiesDialog = bind(this.configureLayerPropertiesDialog, this);
      }
    };
 
    //----------------------------------------------------------------------------------------------------
    //
    //  Viewer Initialization
    //
    //----------------------------------------------------------------------------------------------------
        function initMapView(){
          // viewer = new MapView(viewerOptions.legend, viewerOptions.addLayers);
          
          loadLayerData(viewerOptions.layerData);

          if(viewerOptions.kmlService){
            viewer.showLoading();
            retrieveKmlData(viewerOptions.kmlService);
          }
          
          //test(viewer);                   //uncomment this line to run the test code
        }
        
        // KML Data Retriever
        function retrieveKmlData(kml_service) {
          $.ajax({
            url: kml_service
          }).done(function(json) {
            viewer.hideLoading();
            // Set global map data variable
            if (json['kml_link']){
              loadLayerData(json['kml_link']);
            }
          });
        };
        
        //Loads an array of links to layer data
        function loadLayerData(layers){
          for(var i=0, len=layers.length; i<len; i++){
            viewer.addLayer(layers[i]);
          }
        }
    
    //----------------------------------------------------------------------------------------------------
    //
    //  GOOGLE INITIALIZATION FUNCTIONS
    //
    //----------------------------------------------------------------------------------------------------
    
    function initGoogleMap() {
      // Variable declarations
      var mapOptions, map;
      var layer;
      
      // Configure map
      mapOptions = {
        center: new google.maps.LatLng(-34.397, 150.644),
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.HYBRID,
          scaleControl: true,
          rotateControl: true,
      };
      
      // init map
      map = new google.maps.Map(document.getElementById('map-view-map'), 
                    mapOptions);
      
      initMapView();
    }
    
    function initGoogleEarth() {
      google.earth.createInstance('map-view-map', googleEarthInitCB, googleEarthFailureCB);
    }
    
    function googleEarthInitCB(instance) {
      
      
      // Initiate instance of Google Earth Plugin
      ge = instance;
      ge.getWindow().setVisibility(true);
      
      // Turn on controls
      ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

      initMapView();
    }
    
    function googleEarthFailureCB(errorCode) {
      google.load("maps", "3", {other_params:'sensor=false', callback: initGoogleMap});
    }



  
  /************************************************************************
    *                            TOP LEVEL CODE
    *************************************************************************/
  /*
   * Library object that contains public facing functions of the package.
   */
  publicInterface = {
    addLayer: function(url){
      viewer.addLayer(url);
    }
  };
  
  google.load("earth", "1");
  
  // Initialization: jQuery function that gets called when 
  // the DOM tree finishes loading
  $(function() {
    /* Initialize the globals */
   
    viewerOptions = {
      mapType:$('#map-view-container').attr('data-map-type'),
      legend:JSON.parse($('#map-view-container').attr('data-legend')),
      legendOptions:JSON.parse($('#map-view-container').attr('data-legend-options')),
      layerData:JSON.parse($('#map-view-container').attr('data-layer-data')),
      kmlService:$('#map-view-container').attr('data-kml-service'),
    };
    
    viewer = new MapView(viewerOptions.legend, viewerOptions.legendOptions);
    
    switch(viewerOptions.mapType){
      case 'google-earth':
        google.setOnLoadCallback(initGoogleEarth);
        break;
      case 'google-map':
        //code to initialize google map
        break;
      case 'open-layers':
        //code to initialize openlayers
        break;
      default:
        google.setOnLoadCallback(initGoogleEarth);
    }  
  });

  return publicInterface;

}()); // End of package wrapper

/*****************************************************************************
 *                      Public Functions
 *****************************************************************************/

function addLayer(url) {
  MAP_VIEW.addLayer(url);
}



/*****************************************************************************
 *                      Test Code
 *****************************************************************************/

var kmzs=[
      "http://tethys.byu.edu/storage/f/2013-11-13T18%3A51%3A04.517Z/soil-poly-v1.kml",
      "http://tethys.byu.edu/storage/f/2013-11-13T18%3A58%3A10.477Z/soil-poly-v2.kml",
      "http://tethys.byu.edu/storage/f/2013-11-13T18%3A58%3A55.690Z/soil-poly-v3.kml",
      "http://tethys.byu.edu/storage/f/2013-11-22T18%3A02%3A16.551Z/ele-poly-terrain.kml",
      "http://tethys.byu.edu/storage/f/2013-11-22T18%3A04%3A18.544Z/ele-poly-aqua.kml",
      "http://tethys.byu.edu/storage/f/2013-11-13T18%3A59%3A29.967Z/soil-raster-v1.kmz",
      "http://tethys.byu.edu/storage/f/2013-11-13T20%3A24%3A46.862Z/ele-raster-v2.kmz",
      "http://ciwweb.chpc.utah.edu/storage/f/2014-01-14T19%3A10%3A23.223Z/ele-poly-terrain.kml",
      "http://ciwweb.chpc.utah.edu/storage/f/2014-01-14T19%3A13%3A22.826Z/soil-poly-v3.kml",
      ];
              

function test(map)              
{
  console.log('testing');
  //map.addLayer(kmzs[2]);
  addKmzSelect();
}

var urlField, urlSelect; 
 
function addKmzSelect(){
  urlField = $("#map-view-url-field");
  urlSelect = $( '<select />', { type: 'text', name: 'url'}).change(function(){urlField.val($(this).val());}).appendTo($("#map-view-add-modal-content"));
  $('#map-view-add-layer-btn').click(function(){urlSelect.val(0);});
  $( '<option />', { value: '0', text: '-- Select --' }).appendTo(urlSelect); 
  for(var i = 0; i< kmzs.length; i++){
    $( '<option />', { value: kmzs[i], text: kmzs[i]}).appendTo(urlSelect);
  } 
}
