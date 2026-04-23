import "https://cdn.plot.ly/plotly-3.0.1.min.js"
import createPlotlyComponent from 'react-plotly.js/factory';

export function Plot (...props) {
  const _Plot = createPlotlyComponent(Plotly);
  return React.createElement(_Plot, ...props);
}