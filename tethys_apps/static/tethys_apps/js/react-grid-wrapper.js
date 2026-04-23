import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { AgGridReact as GridReact  } from 'ag-grid-react';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

export function AgGridReact (...props) {
  if (props.length > 0) {
    if (props[0].rowId) {
      let rowId = props[0].rowId;
      delete props[0].rowId;
      props[0].getRowId = (params) => params.data[rowId];
    }
  }
  return React.createElement(GridReact, ...props);
}