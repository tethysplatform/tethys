import {LayersHalf} from "https://esm.sh/react-bootstrap-icons@1.11.4?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=LayersHalf";
export {LayersHalf};
import {SidePanel} from 'https://esm.sh/ol-side-panel@1.0.6?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0&exports=SidePanel';
import LayerSwitcher from "https://esm.sh/ol-layerswitcher@4.1.2?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0&bundle=false";

class LayerPanelClass extends SidePanel {
  constructor() {
    super()
    const layersPane = this.definePane({
      paneId: 'layers',
      name: "Layers",
      icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-layers-half" viewBox="0 0 16 16"><path d="M8.235 1.559a.5.5 0 0 0-.47 0l-7.5 4a.5.5 0 0 0 0 .882L3.188 8 .264 9.559a.5.5 0 0 0 0 .882l7.5 4a.5.5 0 0 0 .47 0l7.5-4a.5.5 0 0 0 0-.882L12.813 8l2.922-1.559a.5.5 0 0 0 0-.882zM8 9.433 1.562 6 8 2.567 14.438 6z"/></svg>'
    });
    
    let thisControl = this;
    const layerContainer = document.createElement('div');
    layerContainer.classList.add("layer-switcher");
    layersPane.addWidgetElement(layerContainer);

    window.setTimeout(function () {
      LayerSwitcher.renderPanel(thisControl.getMap(), layerContainer, { reverse: true });
    }, 500);
  }
}

export function LayerPanel (props) {
  let head = document.getElementsByTagName('head')[0];
  if (document.querySelectorAll(`style[id="layer-panel-styles"]`).length === 0) {
      // Creating link element 
      var style = document.createElement('style');
      style.id = 'layer-panel-styles';
      style.innerText = `
      .ol-side-panel.ol-control {
        box-sizing: content-box;
        background-color: unset !important;
        -webkit-transition: background-color 1000ms linear;
        -ms-transition: background-color 1000ms linear;
        transition: background-color 400ms linear, width 500ms;
      }
      .map-with-ol-side-panel:not(.ol-side-panel-collapsed) .ol-side-panel.ol-control {
        background-color: white !important;
      }
      .layer-switcher {
        position: unset !important;
      }
      .ol-side-panel-tabs > button {
        line-height: 38px !important;
      }
      .ol-side-panel-tabs > button:hover {
        outline: 0 !important;
        border: 1px solid var(--ol-subtle-foreground-color) !important;
      }
      .ol-side-panel-tabs > button.active {
        color: var(--ol-foreground-color) !important;
      }`;
      head.append(style);
  }
  return React.createElement('control', {cls: LayerPanelClass, ...props});
}
