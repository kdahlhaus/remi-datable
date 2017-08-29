import logging

import operator
import os

import remi.gui as gui
from remi import start, App

from datatable import DataTableWithServerSideProcessing

sample_data = (
    ("Soul Man", "Blues Brothers", "Blues", "2:52"),
    ("Another Brick in the Wall", "Pink Floyd",  "Progressive Rock",  "5:35"),
    ("Feier Frei!", "Rammstein", "Hard Rock", "3:10"),
    ("Walk Like an Egyptian", "Bangles", "80's", "3:10"),
    ("46 and 2", "Tool", "Hard Rock", "2:15"),
    ("I Ran", "Flock of Seagulls", "80's", "3:12"),
    ("Jackson", "Johnny Cash", "Country", "1:10"),
    ("Pop Music", "M Factor", "Pop", "3:40"),
    ("Du Hast", "Rammstein", "Hard Rock", "3:10"),
    ("Engel", "Rammstein", "Hard Rock", "3:10"),
    ("Tubular Bells", "Mike Oldfield", "Progressive Rock", "12:10"),
    ("Soul Man 2", "Blues Brothers", "Blues", "2:52"),
    ("Another Brick in the Wall 2", "Pink Floyd",  "Progressive Rock", "5:35"),
    ("Feier Frei! 2", "Rammstein", "Hard Rock", "3:10"),
    ("Walk Like an Egyptian 2", "Bangles", "80's", "3:10"),
    ("46 and 2 2", "Tool", "Hard Rock", "2:15"),
    ("I Ran 2", "Flock of Seagulls", "80's", "3:12"),
    ("Jackson 2", "Johnny Cash", "Country", "1:10"),
    ("Pop Music 2", "M Factor", "Pop", "3:40"),
    ("Du Hast 2", "Rammstein", "Hard Rock", "3:10"),
    ("Engel 2", "Rammstein", "Hard Rock", "3:10"),
    ("Tubular Bells 2", "Mike Oldfield", "Progressive Rock", "12:10"),
)


log = logging.getLogger("server_side_app")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class ServerSideMusicDataTable(DataTableWithServerSideProcessing):

    def onDataRequest(self, request):
        log.debug("request: %s" % request)

        # the full contents of request is documented here:
        #   https://datatables.net/manual/server-side
        start = request["start"]
        length = request["length"]
        search = request["search"]["value"]
        order = request["order"][0]

        # filter based on search parameter
        if search != "":
            filtered_data = []
            for r in sample_data:
                if search in str(r):
                    filtered_data.append(r)
        else:
            filtered_data = sample_data

        num_records_total = len(sample_data)
        num_records_after_filtering = len(filtered_data)

        # paginate
        data = []
        for i in range(start, min(length+start, num_records_after_filtering)):
            sd = filtered_data[i]
            data.append([sd[0], sd[1], sd[2], sd[3]])

        # sort per request
        col_index = order["column"]
        ascending = order["dir"] == "asc"
        data.sort(key=operator.itemgetter(col_index), reverse=(not ascending))

        # build response object
        response = {}
        response["draw"] = request["draw"]
        response["recordsTotal"] = num_records_total
        response["recordsFiltered"] = num_records_after_filtering
        response["data"] = data

        log.debug("response: %s" % response)
        return response


class ExampleFrame(gui.VBox):
    def __init__(self, app,  **kwargs):
        super(ExampleFrame, self).__init__(**kwargs)

        self.row1 = gui.HBox()
        self.append(self.row1)

        self.table = ServerSideMusicDataTable(
            app,
            {'paging': 'true',
             'scrollY': '"200px"',
             'scrollCollapse': 'false',
             'lengthChange': 'false',
             'select': "'single'",
             'colReorder': 'false',
             'columns': """[
             {'name':'title', 'title':'Title'},
             {'name':'artist', 'title':'Artist'},
             {'name':'genre', 'title':'Genre'},
             {'name':'length','title':'Length'}]""",
             },
            style={"height": "300px", "width": "700px"}
        )
        self.row1.append(self.table)


class MyApp(App):
    def __init__(self, *args):
        # The following assumes running from 'remi-datatable/example'.
        # Copy the contents of remi-datatabe/res to your own app's res
        # directory and remove the '..' path segment from the following
        # line when using remi-datatable in your own apps.
        res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',  'res')
        html_head = """
            <link rel="stylesheet" type="text/css" href="/res/datatables.css"/>
            <script type="text/javascript" src="/res/datatables.min.js"></script>
        """
        super(MyApp, self).__init__(*args, static_file_path=res_path,
                                    html_head=html_head)

    def main(self):
        return ExampleFrame(self, width=700, height=300)


if __name__ == "__main__":
    start(MyApp, title="Server-Side Data Grid", debug=True)
