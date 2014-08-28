var j=0;
recurse();
console.log(self);
//console.log(window);
console.log(j);


function recurse(){
 for(var i=0;i<1000000;i++){
   var k = i;
 }
 if(j++ < 10000)
    recurse();
}

 
 
      //Should the feature traversing happen in the Feature class?
      function traverse(parentContainer,parent)
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
        return;
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