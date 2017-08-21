import remi.gui as gui

import json


class DataTable(gui.Widget):
    @gui.decorate_constructor_parameter_types([dict, ])
    def __init__(self, data_table_options={}, **kwargs):
        """data_table_options = dictionay of data table options.
           see  https://datatables.net/reference/option/
        """
        self.rows = []
        self.column_headings = []
        self.data_table_options = data_table_options
        super(DataTable, self).__init__(**kwargs)

    def repr(self, client, changed_widgets={}):
        self.attributes['style'] = gui.jsonize(self.style)
        attribute_string = ' '.join('%s="%s"' %
            (k, v) if v is not None else k for k, v in
            self.attributes.items())
        table_id = "%s_table" % (self.attributes["id"])

        html = '<div %s><table id="%s"><thead><tr>' % (attribute_string, table_id)

        for heading in self.column_headings:
            html += '<th>%s</th>' % heading
        html += '</tr></thead>'

        tbody = '<tbody>'
        for row in self.rows:
            trow = '<tr>'
            for col in row:
                trow += "<td>"+str(col)+"</td>"
            trow += '</tr>'
            tbody += trow
        tbody += '</tbody>'
        html += tbody + '</table></div><script>'

        data_table_options_string = ""
        for key in self.data_table_options:
            data_table_options_string += "%s:%s, " % (key, self.data_table_options[key])

        html += """
            $(document).ready( function () {
                $('#%s').DataTable({%s});
            } );
        </script>""" % (table_id, data_table_options_string)

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

    @gui.decorate_constructor_parameter_types([object, dict, ])
    def __init__(self, app, data_table_options={}, **kwargs):
        """ app = the App instance
            data_table_options = dictionary of data table options.
            see  https://datatables.net/reference/option/
        """
        self.app = app
        data_table_options["serverSide"] = 'true'
        super(DataTableWithServerSideProcessing, self).__init__(data_table_options, **kwargs)
        self.data_table_options["ajax"] = """function(data, callback, settings)
            {{
            if (typeof(window.data_table_callbacks)=='undefined')
            {{ window.data_table_callbacks = new Map(); }}
            window.data_table_callbacks['{identifier}']=callback
            sendCallbackParam('{identifier}', '_onDataRequest',
                {{'request':JSON.stringify(data), 'callback':callback}});
            }}
        """.format(identifier=self.identifier)

    def _onDataRequest(self, *args, **kwargs):
        """ parse raw request from front-end and call onData(....) """
        request = json.loads(kwargs["request"])
        response = self.onDataRequest(request)
        response_json = json.dumps(response)
        js = """window.data_table_callbacks['{identifier}']({json});""".format(identifier=self.identifier, json=response_json)
        self.app.execute_javascript(js)

    def onDataRequest(self, request):
        """ request: request object as documented at:
                https://datatables.net/manual/server-side

            return a response dictionary as defined in:
                https://datatables.net/manual/server-side

                for example:

                   response = {}
                   response["draw"]=request["draw"]
                   response["recordsTotal"]=total_number_of_records
                   response["recordsFiltered"]=number_of_records_after_filtering
                   response["data"]=[ ["row1 col1", "row1 col2",...], ...]
                   return response
        """
        raise NotImplementedError
