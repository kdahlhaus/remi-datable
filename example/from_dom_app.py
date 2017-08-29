import sys
sys.path.append("..")

import os

import remi.gui as gui
from remi import start, App

from remidatatable import DataTableFromDomData


data = (
    ("Title", "Artist", "Genre", "Length"),
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
    ("Another Brick in the Wall 2", "Pink Floyd",  "Progressive Rock",  "5:35"),
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


class ExampleFrame(gui.VBox):
    def __init__(self, **kwargs):
        super(ExampleFrame, self).__init__(**kwargs)

        self.row1 = gui.HBox()
        self.append(self.row1)

        self.table = DataTableFromDomData(
            {'paging': 'true',
             'scrollY': '"200px"',
             'scrollCollapse': 'false',
             'lengthChange': 'false',
             'select': "'single'",
             'colReorder': 'true'
             },
            style={"height": "300px", "float": "right"})
        self.row1.append(self.table)

        self.table.set_column_headings(data[0])
        for ri in range(1, len(data)):
            self.table.add_row(data[ri])


class MyApp(App):
    def __init__(self, *args):
        res_path = DataTableFromDomData.get_res_path()
        html_head = """
            <link rel="stylesheet" type="text/css" href="/res/datatables.css"/>
            <script type="text/javascript" src="/res/datatables.min.js"></script>
        """
        super(MyApp, self).__init__(*args, static_file_path=res_path, html_head=html_head)

    def main(self):
        main_container = ExampleFrame(width=700, height=300)
        return main_container


if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(MyApp, title="Beet Window", debug=True)
