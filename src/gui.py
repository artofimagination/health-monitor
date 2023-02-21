from PyQt5.QtCore import QDate, QDateTime
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QGroupBox, QComboBox, QLabel, QSpinBox, QDateTimeEdit, QLineEdit
from PyQt5.QtWebKitWidgets import QWebView
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


# Main Qt UI window
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Initialize worker thread related members.
        self.df_users = pd.read_csv('src/data/users.csv')
        self.df_data = pd.read_csv('src/data/data.csv', usecols=[
            "name", "datetime", "systolic", "diastolic", "pulse", "systolic", "event", "description"])
        self.setMinimumSize(200, 100)
        mainLayout = self._createMainLayout()

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle("Health monitor")

        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry()
        self.resize(screenRect.width(), screenRect.height())
        self.show()

    # @QtCore.pyqtSlot(bool)
    def _updateControlEnabled(self, enabled):
        self.enablePump.setEnabled(enabled)
        self.enableValve.setEnabled(enabled)
        self.enableSolar.setEnabled(enabled)
        self.enableGenerator.setEnabled(enabled)

    def _createMainLayout(self):
        layout = QGridLayout()
        self.view = QWebView()
        layout.addWidget(self.view, 0, 0, 4, 1)
        inputGroupLayout = QGridLayout()
        userLabel = QLabel("User")
        self.userComboBox = QComboBox()

        for _, user in self.df_users.iterrows():
            self.userComboBox.addItem(user["name"])
        self.userComboBox.currentIndexChanged.connect(self._select_data)
        self.userComboBox.setCurrentIndex(1)
        dateTimeLabel = QLabel("Measurement datetime")
        self.dateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateTimeEdit.setMinimumDate(QDate.currentDate().addDays(-365))
        self.dateTimeEdit.setMaximumDate(QDate.currentDate().addDays(365))
        self.dateTimeEdit.setDisplayFormat("yyyy.MM.dd hh:mm")
        systolicPressureLabel = QLabel("Systolic")
        self.systolicPressureSpinBox = QSpinBox()
        self.systolicPressureSpinBox.setMinimum(0)
        self.systolicPressureSpinBox.setMaximum(250)
        diastolicPressureLabel = QLabel("Diastolic")
        self.diastolicPressureSpinBox = QSpinBox()
        self.diastolicPressureSpinBox.setMinimum(0)
        self.diastolicPressureSpinBox.setMaximum(250)
        pulseLabel = QLabel("Pulse")
        self.pulseSpinBox = QSpinBox()
        self.pulseSpinBox.setMinimum(0)
        self.pulseSpinBox.setMaximum(250)
        eventLabel = QLabel("Event")
        self.eventLineEdit = QLineEdit()
        descriptionLabel = QLabel("Detail")
        self.descriptionLineEdit = QLineEdit()
        pushButtonAdd = QPushButton("Add")
        pushButtonAdd.clicked.connect(self._update)
        pushButtonDeleteLast = QPushButton("Delete last")
        pushButtonDeleteLast.clicked.connect(self._delete_last)
        inputGroupLayout.addWidget(userLabel, 0, 0, 1, 10)
        inputGroupLayout.addWidget(self.userComboBox, 0, 1, 1, 10)
        inputGroupLayout.addWidget(dateTimeLabel, 1, 0, 1, 10)
        inputGroupLayout.addWidget(self.dateTimeEdit, 1, 1, 1, 10)
        inputGroupLayout.addWidget(systolicPressureLabel, 2, 0, 1, 10)
        inputGroupLayout.addWidget(self.systolicPressureSpinBox, 2, 1, 1, 10)
        inputGroupLayout.addWidget(diastolicPressureLabel, 3, 0, 1, 10)
        inputGroupLayout.addWidget(self.diastolicPressureSpinBox, 3, 1, 1, 10)
        inputGroupLayout.addWidget(pulseLabel, 4, 0, 1, 10)
        inputGroupLayout.addWidget(self.pulseSpinBox, 4, 1, 1, 10)
        inputGroupLayout.addWidget(eventLabel, 5, 0, 1, 10)
        inputGroupLayout.addWidget(self.eventLineEdit, 5, 1, 1, 10)
        inputGroupLayout.addWidget(descriptionLabel, 6, 0, 1, 10)
        inputGroupLayout.addWidget(self.descriptionLineEdit, 6, 1, 1, 10)
        inputGroupLayout.addWidget(pushButtonAdd, 7, 0, 1, 1)
        inputGroupLayout.addWidget(pushButtonDeleteLast, 7, 1, 1, 1)

        inputGroupBox = QGroupBox("Input")
        inputGroupBox.setLayout(inputGroupLayout)
        layout.addWidget(inputGroupBox, 4, 0, 1, 1)
        self._show_graph()
        return layout

    def _delete_last(self):
        df_all = pd.read_csv('src/data/data.csv', usecols=[
            "name", "datetime", "systolic", "diastolic", "pulse", "systolic", "event", "description"])
        df_without_current_user = df_all[df_all['name'] != self.userComboBox.currentText()]
        self.df_data.drop(self.df_data.index[-1], inplace=True)
        df = pd.concat([df_without_current_user, self.df_data])
        df.to_csv('src/data/data.csv', index=False)
        self._select_data()

    def _update(self):
        df_data = pd.read_csv('src/data/data.csv', usecols=[
            "name", "datetime", "systolic", "diastolic", "pulse", "systolic", "event", "description"])
        df_data = df_data.append({
            'name': self.userComboBox.currentText(),
            'datetime': self.dateTimeEdit.dateTime().toString("dd.MM.yyyy hh:mm"),
            'systolic': self.systolicPressureSpinBox.value(),
            'diastolic': self.diastolicPressureSpinBox.value(),
            'pulse': self.pulseSpinBox.value(),
            'event': self.eventLineEdit.text(),
            'description': self.descriptionLineEdit.text()}, ignore_index=True)
        df_data.to_csv('src/data/data.csv', index=False)
        self._select_data()

    def _select_data(self, index=0):
        self.df_data = pd.read_csv('src/data/data.csv', usecols=[
            "name", "datetime", "systolic", "diastolic", "pulse", "systolic", "event", "description"])
        self.df_data = self.df_data[self.df_data['name'] == self.userComboBox.currentText()]
        self._show_graph()

    def _show_graph(self):
        df_limits = pd.read_csv('src/data/limits.csv')
        datetime = pd.to_datetime(self.df_data['datetime'], format='%d.%m.%Y %H:%M')
        # Create figure with secondary y-axis
        self.fig = make_subplots(rows=3, cols=1,
                                 specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]],
                                 shared_xaxes=True,
                                 vertical_spacing=0.03,
                                 )

        # Add traces
        self.fig.add_trace(
            go.Scatter(x=datetime, y=self.df_data["systolic"], name="Systolic"),
            row=1, col=1
        )

        self.fig.add_hrect(row=1, col=1,
                           y0=70, y1=df_limits.iloc[0]["systolic"], line_width=0, fillcolor="blue", opacity=0.2,
                           annotation_text="low", annotation_position="right")
        self.fig.add_hrect(row=1, col=1,
                           y0=df_limits.iloc[0]["systolic"], y1=df_limits.iloc[1]["systolic"],
                           line_width=0, fillcolor="green", opacity=0.2,
                           annotation_text="normal", annotation_position="right")
        self.fig.add_hrect(row=1, col=1,
                           y0=df_limits.iloc[1]["systolic"], y1=df_limits.iloc[2]["systolic"],
                           line_width=0, fillcolor="yellow", opacity=0.2,
                           annotation_text="elevated", annotation_position="right")
        self.fig.add_hrect(row=1, col=1,
                           y0=df_limits.iloc[2]["systolic"], y1=df_limits.iloc[3]["systolic"],
                           line_width=0, fillcolor="orange", opacity=0.2,
                           annotation_text="hyper tension 1", annotation_position="right")
        self.fig.add_hrect(row=1, col=1,
                           y0=df_limits.iloc[3]["systolic"], y1=df_limits.iloc[4]["systolic"],
                           line_width=0, fillcolor="red", opacity=0.2,
                           annotation_text="hypertension 2", annotation_position="right")
        self.fig.add_hrect(row=1, col=1,
                           y0=df_limits.iloc[4]["systolic"], y1=200,
                           line_width=0, fillcolor="black", opacity=0.2,
                           annotation_text="critical", annotation_position="right")

        self.fig.add_trace(
            go.Scatter(x=datetime, y=self.df_data["diastolic"], name="Diastolic"),
            row=2, col=1
        )

        self.fig.add_hrect(row=2, col=1,
                           y0=40, y1=df_limits.iloc[0]["diastolic"], line_width=0, fillcolor="blue", opacity=0.2,
                           annotation_text="low", annotation_position="right")
        self.fig.add_hrect(row=2, col=1,
                           y0=df_limits.iloc[0]["diastolic"], y1=df_limits.iloc[1]["diastolic"],
                           line_width=0, fillcolor="green", opacity=0.2,
                           annotation_text="normal", annotation_position="right")
        self.fig.add_hrect(row=2, col=1,
                           y0=df_limits.iloc[2]["diastolic"], y1=df_limits.iloc[3]["diastolic"],
                           line_width=0, fillcolor="yellow", opacity=0.2,
                           annotation_text="elevated/hyper tension 1", annotation_position="right")
        self.fig.add_hrect(row=2, col=1,
                           y0=df_limits.iloc[3]["diastolic"], y1=df_limits.iloc[4]["diastolic"],
                           line_width=0, fillcolor="red", opacity=0.2,
                           annotation_text="hypertension 2", annotation_position="right")
        self.fig.add_hrect(row=2, col=1,
                           y0=df_limits.iloc[4]["diastolic"], y1=140,
                           line_width=0, fillcolor="black", opacity=0.2,
                           annotation_text="critical", annotation_position="right")

        self.fig.add_trace(
            go.Scatter(x=datetime, y=self.df_data["pulse"], name="Pulse"),
            row=3, col=1
        )

        self.fig.add_hrect(row=3, col=1,
                           y0=60, y1=100,
                           line_width=0, fillcolor="green", opacity=0.2,
                           annotation_text="normal", annotation_position="right")

        df_events = self.df_data[~self.df_data['event'].isnull()]
        datetime = pd.to_datetime(df_events['datetime'], format='%d.%m.%Y %H:%M')
        self.fig.add_trace(row=1, col=1, trace=go.Scatter(
            x=datetime,
            y=df_events["systolic"],
            mode="markers+text",
            name="Event",
            text=df_events["event"],
            textposition="bottom left",
            hoverinfo='text'
        ))
        self.fig.add_trace(row=2, col=1, trace=go.Scatter(
            x=datetime,
            y=df_events["diastolic"],
            mode="markers+text",
            name="Event",
            text=df_events["event"],
            textposition="bottom left",
            hoverinfo='text'
        ))
        self.fig.add_trace(row=3, col=1, trace=go.Scatter(
            x=datetime,
            y=df_events["pulse"],
            mode="markers+text",
            name="Event",
            text=df_events["event"],
            textposition="bottom left",
        ))

        # Add figure title
        self.fig.update_layout(
            title_text="Blood pressure",
            showlegend=False
        )

        # Set y-axes titles
        self.fig.update_yaxes(row=1, col=1, title_text="<b>Systolic</b>", secondary_y=False)
        self.fig.update_yaxes(row=2, col=1, title_text="<b>Diastolic</b>", secondary_y=False)
        self.fig.update_yaxes(row=3, col=1, title_text="<b>Pulse</b>", secondary_y=False)

        self.view.setHtml(self.fig.to_html(include_plotlyjs='cdn'))
