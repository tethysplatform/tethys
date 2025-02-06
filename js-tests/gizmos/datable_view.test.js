import $ from "jquery";

// Mock jQuery's DataTables plugin
$.fn.DataTable = jest.fn();

// Function to reload the module to trigger document ready function
const reloadDatatableView = () => {
    jest.resetModules(); // Clear Jest’s module cache
    return require("../../tethys_gizmos/static/tethys_gizmos/js/datatable_view");
};

describe("TETHYS_DATATABLE_VIEW", () => {
    beforeEach(() => {
        document.body.innerHTML = `
          <table class="data_table_gizmo_view">
            <thead>
              <tr><th>Column 1</th><th>Column 2</th></tr>
            </thead>
            <tbody>
              <tr><td>Data 1</td><td>Data 2</td></tr>
              <tr><td>Data 3</td><td>Data 4</td></tr>
            </tbody>
          </table>
        `;
        $.fn.DataTable = jest.fn();
    });

    

    test("should initialize DataTables when called manually", () => {
        const TETHYS_DATATABLE_VIEW = reloadDatatableView();
        const tableElement = $(".data_table_gizmo_view");
        // Call the initialization function manually
        TETHYS_DATATABLE_VIEW.initTableView(tableElement);
        // Ensure DataTables was called
        expect(tableElement.DataTable).toHaveBeenCalled();
    });
});test("should initialize DataTables on document ready", (done) => {
        const dataTableSpy = jest.spyOn($.fn, "DataTable");
        reloadDatatableView();

        // Wait for jQuery's document ready function
        setTimeout(() => {
            // Ensure DataTables was called
            expect(dataTableSpy).toHaveBeenCalled();
            dataTableSpy.mockRestore();
            done();
        }, 100); 
    });