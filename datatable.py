import remi.gui as gui

import logging
log = logging.getLogger("datatable")

import json

class DataTable(gui.Widget):
    @gui.decorate_constructor_parameter_types([dict,  ])
    def __init__(self, data_table_options={}, **kwargs):
        "data_table_options = dictionay of data table options.  see  https://datatables.net/reference/option/"
        self.rows=[]
        self.column_headings=[]
        self.data_table_options=data_table_options
        super(DataTable, self).__init__(**kwargs)


    def repr(self, client, changed_widgets={}):
        self.attributes['style'] = gui.jsonize(self.style)
        attribute_string = ' '.join('%s="%s"' % (k, v) if v is not None else k for k, v in
                                                self.attributes.items())
        table_id = "%s_table"%(self.attributes["id"])

        html = '<div %s><table id="%s"><thead><tr>'%(attribute_string, table_id)

        for heading in self.column_headings:
            html += '<th>%s</th>'%heading
        html += '</tr></thead>'

        tbody = '<tbody>'
        for row in self.rows:
            trow = '<tr>'
            for col in row:
                trow += "<td>"+str(col)+"</td>"
            trow += '</tr>'
            tbody += trow
        tbody += '</tbody>'
        html +=  tbody + '</table></div><script>'

        data_table_options_string=""
        for key in self.data_table_options:
            data_table_options_string += "%s:%s, "%(key, self.data_table_options[key])

        html += """
            $(document).ready( function () {
                $('#%s').DataTable({%s});
            } );
        </script>"""%(table_id, data_table_options_string)

        return html


class DataTableFromDomData(DataTable):
    """ DataTable that uses data from the DOM """

    def set_column_headings(self, headings):
        self.column_headings = headings

    def add_row(self, row):
        self.rows.append(row)



class DataTableWithServerSideProcessing(DataTable):
    """ DataTable that uses onDataRequest handler in python to
        provide data.
    """

    @gui.decorate_constructor_parameter_types([object, dict,  ])
    def __init__(self, app, data_table_options={}, **kwargs):
        """ app = the App instance
            data_table_options = dictionary of data table options.  see  https://datatables.net/reference/option/
        """
        self.app = app
        data_table_options["serverSide"]='true'
        super(DataTableWithServerSideProcessing, self).__init__( data_table_options, **kwargs)
        self.data_table_options["ajax"]="""function(data, callback, settings)
            {{
            console.log("DTWSP ajac data req "+data["draw"]);
            if (typeof(window.data_table_callbacks)=='undefined'){{ window.data_table_callbacks = new Map(); console.log('added dtc'); }} else {{ console.log('already added dtc'); }}
            window.data_table_callbacks['{identifier}']=callback
            sendCallbackParam('{identifier}', '_onDataRequest', {{'request':JSON.stringify(data), 'callback':callback}});
            }}
        """.format(identifier=self.identifier)

            #/*callback({{"draw":data["draw"], "recordsTotal":2, "recordsFiltered":2, "data":[["One nigh","Bob","80s","2:14"],["Money","Pink F", "Prog", "7:36"]]}});*/


    def _onDataRequest(self, *args, **kwargs):
        """ parse raw request from front-end and call onData(....) """
        log.debug("onDataRequest(%s, %s)"%(args, kwargs))

        # the full contents of request is documented here:
        #   https://datatables.net/manual/server-side
        request = json.loads(kwargs["request"])

        draw = request["draw"]
        start = request["start"]
        length = request["length"]
        search = request["search"]["value"]
        order = request["order"][0]

        response = self.onDataRequest(draw, start, length, search, order, **kwargs)

        response_json = json.dumps(response)
        log.debug("response: %s"%response_json)

        js = """window.data_table_callbacks['{identifier}']({json});""".format(identifier=self.identifier, json=response_json)
        log.debug(js)
        self.app.execute_javascript(js)


    def onDataRequest(self, draw, start, length, search, order, **kwargs):
        """ return response dictionary as defined at https://datatables.net/manual/server-side """
        raise NotImplementedError
