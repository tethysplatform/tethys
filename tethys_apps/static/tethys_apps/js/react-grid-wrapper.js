import { AllCommunityModule, ModuleRegistry } from 'https://esm.sh/ag-grid-community@34.2.0?deps=react@19.0,react-dom@19.0,react-is@19.0';
import { AgGridReact as GridReact  } from 'https://esm.sh/ag-grid-react@34.2.0?deps=react@19.0,react-dom@19.0,react-is@19.0';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

export function AgGridReact (...props) {
  if (props[0].rowId) {
    let rowId = props[0].rowId;
    delete props[0].rowId;
    props[0].getRowId = (params) => params.data[rowId];
  } else {
    props[0].getRowId = (params) => params.data.id ? params.data.id : params.node.rowIndex;
  }
  return React.createElement(GridReact, ...props);
}