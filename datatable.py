import remi.gui as gui

import logging
log = logging.getLogger("datatable")

import json

class DataTableWithDomData(gui.Widget):

    @gui.decorate_constructor_parameter_types([dict,  ])
    def __init__(self, data_table_options={}, **kwargs):
        "data_table_options = dictionay of data table options.  see  https://datatables.net/reference/option/"
        self.rows=[]
        self.column_headings=[]
        self.data_table_options=data_table_options
        log.debug("DataTable.__iniit__ kwargs=%s"%kwargs)
        super(DataTableWithDomData, self).__init__(**kwargs)
        log.debug("DT style after init %s"%(self.style))
        log.debug("DT attributes after init %s"%(self.attributes))

    def set_column_headings(self, headings):
        self.column_headings = headings

    def add_row(self, row):
        self.rows.append(row)

    def repr(self, client, changed_widgets={}):
        #log.debug("datatable repr self.style:%s"%str(self.style))
        #log.debug("datatable repr self.attributes:%s"%str(self.attributes))
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
        #log.debug("datatable repr returning: %s"%html)

        return html


class DataTableWithServerSideProcessing(DataTableWithDomData):
    """https://datatables.net/manual/server-side"""

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
            sendCallbackParam('{identifier}', '_onDataRequest', {{'data':JSON.stringify(data), 'callback':callback}});
            }}""".format(identifier=self.identifier)

            #/*callback({{"draw":data["draw"], "recordsTotal":2, "recordsFiltered":2, "data":[["One nigh","Bob","80s","2:14"],["Money","Pink F", "Prog", "7:36"]]}});*/



    def _onDataRequest(self, *args, **kwargs):
        log.debug("onDataRequest(%s, %s)"%(args, kwargs))
        data = json.loads(kwargs["data"])
        draw = data["draw"]
        start = data["start"]
        length = data["length"]
        search = data["search"]["value"]
        callback = kwargs["callback"]
        log.debug(f"params  draw:{draw} start:{start} length:{length} search:{search} ")

        records_total = 25
        records_filtered = 25


        data =[]
        for i in range(start, min(length+start, records_total)):
            data.append(["One night %d"%i, "Bob", "80s", "2:15"])

        response = {}
        response["draw"]=draw
        response["recordsTotal"]=records_total
        response["recordsFiltered"]=records_filtered
        response["data"]=data

        data_json = json.dumps(response)
        log.debug("response: %s"%data_json)

        #js = """window.data_table_callbacks['{identifier}']({{"draw":{draw}, "recordsTotal":{records_total}, "recordsFiltered":{records_filtered}, "data":[["One nigh","Bob","80s","2:14"],["Money","Pink F", "Prog", "7:36"]]}});""".format(identifier=self.identifier, draw=draw, records_total=records_total, records_filtered=records_filtered)
        js = """window.data_table_callbacks['{identifier}']({json});""".format(identifier=self.identifier, draw=draw, records_total=records_total, records_filtered=records_filtered, json=data_json)
        log.debug(js)
        self.app.execute_javascript(js)



