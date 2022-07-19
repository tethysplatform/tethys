import Container from 'react-bootstrap/Container';
import Plot from 'react-plotly.js';
import { useEffect, useState } from 'react';

import appAPI from 'services/api/app';
import LoadingAnimation from 'components/loader/LoadingAnimation';

function PlotView() {
  const [ plotData, setPlotData ] = useState(null);

  useEffect(() => {
    appAPI.getPlotData()
      .then((data) => {
        // Derived from this example: https://plotly.com/javascript/time-series/#time-series-with-rangeslider
        let traces = [];
        for (let series of data.series) {
          traces.push({
            type: "scatter",
            mode: "lines",
            name: series.title,
            x: series.x,
            y: series.y,
          })
        }

        let layout = {
          title: 'Time Series with Range Slider',
          width: '100%', 
          height: '100%', 
          xaxis: {
            autorange: true,
            range: ['2015-02-17', '2017-02-16'],
            rangeselector: {buttons: [
                {
                  count: 1,
                  label: '1m',
                  step: 'month',
                  stepmode: 'backward'
                },
                {
                  count: 6,
                  label: '6m',
                  step: 'month',
                  stepmode: 'backward'
                },
                {step: 'all'}
              ]},
            rangeslider: {range: ['2015-02-17', '2017-02-16']},
            type: 'date'
          },
          yaxis: {
            autorange: true,
            range: [86.8700008333, 138.870004167],
            type: 'linear'
          }
        };

        setPlotData({
          data: traces,
          layout: layout
        });
      });
  }, []);

  if (!plotData) {
    return (
      <LoadingAnimation />
    );
  } else {
    return (
      <Container className="py-5 h-100 d-flex justify-content-center">
        <Plot data={plotData.data} layout={plotData.layout} />
      </Container>
    );
  }
}

export default PlotView;