import Card from 'react-bootstrap/Card';
import Feature from 'ol/Feature';
import Map from 'ol/Map';
import OSM from 'ol/source/OSM';
import Overlay from 'ol/Overlay';
import Point from 'ol/geom/Point';
import Select from 'ol/interaction/Select';
import TileLayer from 'ol/layer/Tile';
import VectorSource from 'ol/source/Vector';
import View from 'ol/View';
import { Circle, Fill, Stroke, Style } from 'ol/style';
import { Vector as VectorLayer } from 'ol/layer';
import { fromLonLat } from 'ol/proj';
import { useEffect, useRef, useState } from 'react';

import 'ol/ol.css';

function Home() {
  const [map, setMap] = useState(null);
  const mapWrapperRef = useRef();
  const mapRef = useRef();
  const popupRef = useRef();
  mapRef.current = map;

  useEffect(() => {
    // Skip if the mapWrapper element already has content in it
    if (mapWrapperRef.current.childNodes.length !== 0) {
      return;
    }

    // Create map element
    let mapContainer = document.createElement("div");
    mapContainer.style = "height: 100%; width: 100%; overflow-y: hidden;";
    mapContainer.dataset.testid = 'map-container';
    mapWrapperRef.current.append(mapContainer);
    
    // Create a point on the Clyde Building at BYU
    const cldBldgCoord = fromLonLat([-111.648149, 40.247094]);
    const clydeBldg = new Feature({
      geometry: new Point(cldBldgCoord),
    });

    clydeBldg.setStyle(
      new Style({
        image: new Circle({
          radius: 10,
          fill: new Fill({
            color: '#002E5D',
          }),
          stroke: new Stroke({
            color: 'white',
            width: 3
          })
        }),
      })
    );

    const vectorSource = new VectorSource({
      features: [clydeBldg],
    });

    const vectorLayer = new VectorLayer({
      source: vectorSource,
    });

    const initialMap = new Map({
      target: mapContainer,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
        vectorLayer,
      ],
      view: new View({
        center: cldBldgCoord,
        zoom: 5,
      }),
    });

    // Setup the select interaction
    const selectedStyle =  new Style({
      image: new Circle({
        radius: 10,
        fill: new Fill({
          color: 'red',
        }),
        stroke: new Stroke({
          color: 'white',
          width: 3
        })
      }),
    });

    const selectInteraction = new Select({style: selectedStyle});
    initialMap.addInteraction(selectInteraction);

    // Initialize popup
    const popup = new Overlay({
      element: popupRef.current,
      positioning: 'bottom-center',
      offset: [0, -15],
    });
    initialMap.addOverlay(popup);

    // Create popup when selected / hide when not selected
    selectInteraction.on('select', (evt) => {
      const pos = evt.selected.length > 0 ? cldBldgCoord : null;
      popupRef.current.classList.remove('d-none');
      popup.setPosition(pos);
    });
  
    setMap(initialMap);
  }, []);

  return (
    <div className="h-100">
      <div ref={mapWrapperRef} data-testid="map-wrapper" className="h-100"></div>
      <div ref={popupRef} data-testid="map-popup" className="d-none">
        <Card style={{ width: '18rem' }}>
          <Card.Body>
            <Card.Title>Birthplace of Tethys Platform</Card.Title>
            <Card.Text>BYU Clyde Engineering Building circa 2012.</Card.Text>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
}

export default Home;
