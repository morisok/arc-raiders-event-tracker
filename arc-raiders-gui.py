from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget
)
from PySide6.QtGui import (
    QFont
)
import sys
import requests
from datetime import datetime

class AppName(QWidget):
    def __init__(self):
        super().__init__()

        # variables used in the class

        self.map_names = ()
        self.event_names = ()

        self.init_ui()

    def init_ui(self):
        self.title = 'Arc Raiders Event Tracker'
        self.setWindowTitle(self.title)

        # populate QComboBox

        self.getEventNames()
        self.getMapNames()

        # layout settings

        self.layout = QVBoxLayout() # V is for vertical
        self.setLayout(self.layout)

        # labels

        self.title_label = QLabel(self.title)

        self.event_list = QListWidget()

        # inputs

        self.map_selection = QComboBox()
        self.map_selection.addItems(['-- Select a map --',] + list(self.map_names))

        self.event_selection = QComboBox()
        self.event_selection.addItems(['-- Select a specific event --',] + list(self.event_names))

        # buttons

        # show the widgets

        self.layout.addWidget(self.title_label)

        self.layout.addWidget(self.map_selection)
        self.layout.addWidget(self.event_selection)

        self.layout.addWidget(self.event_list)

        # widget modifications

        titleFont = QFont()
        titleFont.setPointSize(35)
        titleFont.setBold(True)

        self.title_label.setFont(titleFont)

        # connections go here

        self.map_selection.currentIndexChanged.connect(self.showSelectedMapEvents)
        self.event_selection.currentIndexChanged.connect(self.showSelectedMapEvents)

    # logic goes here

    def getEventNames(self):
        data = self.getEventSchedule()
        self.event_names = tuple(sorted({event['name'] for event in data['data']}))

    def getMapNames(self):
        data = self.getEventSchedule()
        self.map_names = tuple(sorted({event['map'] for event in data['data']}))

    def getEventSchedule(self) -> dict:
        url: str = 'https://metaforge.app/api/arc-raiders/events-schedule'

        response = requests.get(url)
        data: dict = response.json()
        return data

    def showSelectedMapEvents(self):
        selected_map = self.map_selection.currentText()
        selected_event = self.event_selection.currentText()

        if selected_map == '-- Select a map --':
            self.event_list.clear()
            return

        data = self.getEventSchedule()

        now_ms = int(datetime.now().timestamp() * 1000) # current time in ms

        upcoming_events = [
            event for event in data['data']
               if event['startTime'] > now_ms
               and (selected_event == '-- Select a specific event --' or event['name'] == selected_event) # skips the event filter if no event is selected
        ]

        upcoming_events.sort(key=lambda event: event['startTime']) # sorts by the starting time of the events
        # key is the value used to sort items

        self.event_list.clear() # clears the list
        if not upcoming_events:
            if selected_event == '-- Select a specific event --':
                msg = f'No upcoming events on {selected_map} right now.'
            else:
                msg = f'No upcoming {selected_event} on {selected_map}.'
            self.event_list.addItem(msg)
            self.event_list.addItem('Events rotate hourly - try again later or choose another.')
        else: # adds events to the list
            for event in upcoming_events:
                start_dt = datetime.fromtimestamp(event['startTime'] / 1000)
                end_dt = datetime.fromtimestamp(event['endTime'] / 1000)
                start_str = start_dt.strftime('%H:%M:%S (%d.%m.%Y)')
                end_str = end_dt.strftime('%H:%M:%S (%d.%m.%Y)')
                item_text = f"{event['name']} - Starts: {start_str} | Ends: {end_str}"
                self.event_list.addItem(item_text)

def main():
    app = QApplication(sys.argv)
    window = AppName()
    window.show()
    window.resize(600, 800)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
