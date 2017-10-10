from pywps import Process, LiteralInput, LiteralOutput, Format, FORMATS
import sqlite3
import os
import psycopg2  # connect to postgis db

class StreamHUCQuery(Process):
    def __init__(self):
        # init process
        inputs = [LiteralInput('id', 'ID value', data_type='string'),
                  LiteralInput('type', 'ID type', data_type='string', allowed_values=('comid','huc8','huc10','huc12'))]
        outputs = [LiteralOutput('output', 'ComIDs or HUC 12', data_type='string')]

        super(StreamHUCQuery, self).__init__(
            self._handler,
                identifier='streamhucquery',
            version='0.1',
            title="NWM stream ComID and HUC bidirectional query process",
            abstract='This process returns ComIDs of all included streams from user-input HUC 8/10/12, and returns HUC 12 from user-input stream ComID',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )



    def _handler(self, request, response):

        #get input values
        id_value = request.inputs['id'][0].data
        id_type = request.inputs['type'][0].data

        # Run
        output = fetch_data(id_value, id_type)

        response.outputs['output'].data = output

        return response

def fetch_data(id_value, id_type):
    connection = None
    try:

        ## connect to postgis db
        # connection = psycopg2.connect(database="nwm_db",host="127.0.0.1",port="5435",user="tethys_super", password="pass")
        # table_name = 'nwmstreams'

        # connect to db file
        current_path = os.path.abspath(__file__)
        db_path = current_path[0:current_path.rfind('/')+1]+'huc.db'
        connection = sqlite3.connect(db_path)
        table_name = 'huc'

        cursor = connection.cursor()

        if id_type == 'comid':
            output = fetch_huc12(cursor, table_name, id_value)
        elif 'huc' in id_type:
            output = fetch_comid(cursor, table_name, id_value, id_type)

        return output

    except Exception as ex:

        return ex.message

    finally:
        if connection is not None:
            connection.close()

def fetch_huc12(cursor, table_name, id_value):

    sql = "SELECT huc_12 FROM %s WHERE station_id = '%s';" % (table_name, id_value)
    cursor.execute(sql)
    huc_12 = [str(item[0]) for item in cursor.fetchall()]

    return huc_12[0]


def fetch_comid(cursor, table_name, id_value, id_type):

    if id_type == 'huc8':
        huc = 'huc_8'
    elif id_type == 'huc10':
        huc = 'huc_10'
    elif id_type == 'huc12':
        huc = 'huc_12'

    sql = "SELECT station_id FROM %s WHERE %s = '%s';" % (table_name, huc, id_value)
    cursor.execute(sql)
    comid_list = [str(item[0]) for item in cursor.fetchall()]

    return comid_list