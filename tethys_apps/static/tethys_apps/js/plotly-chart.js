import "https://cdn.plot.ly/plotly-3.0.1.min.js"
import createPlotlyComponent from 'https://esm.sh/react-plotly.js/factory?deps=react@19.0,react-dom@19.0,react-is@19.0';

export function Plot (...props) {
  const _Plot = createPlotlyComponent(Plotly);
  return React.createElement(_Plot, ...props);
}