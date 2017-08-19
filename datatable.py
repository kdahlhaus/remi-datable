import remi.gui as gui

import logging
log = logging.getLogger("datatable")


class DataTableWithDomData(gui.Widget):

    @gui.decorate_constructor_parameter_types([dict,  ])
    def __init__(self, data_table_options={}, **kwargs):
        "data_table_options = dictionay of data table options.  see  https://datatables.net/reference/option/"
        self.rows=[]
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

        return html
