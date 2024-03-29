
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget
from PyQt5.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QPushButton, QLabel, QGridLayout,QListWidgetItem
from openai import OpenAI
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QIcon, QTextCursor, QPixmap
from PyQt5.QtCore import Qt,pyqtSignal
from openai import OpenAI
from gmail import getGmail

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Section")
        self.resize(800, 300)
        self.layout = QVBoxLayout(self)

        self.titleInput = QLineEdit(self)
        self.titleInput.setPlaceholderText("Section")
        self.layout.addWidget(self.titleInput)
        # Store inputs as a dictionary
        self.inputs = {}

        # Dynamically create input fields
        self.inputFields = []
        for _ in range(5):
            keyInput = QLineEdit(self)
            keyInput.setPlaceholderText("Name of the input")
            valueInput = QLineEdit(self)
            valueInput.setPlaceholderText("Value")
            self.inputFields.append((keyInput, valueInput))
            self.layout.addWidget(keyInput)
            self.layout.addWidget(valueInput)

        # Save button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.saveInputs)
        self.layout.addWidget(self.saveButton)

    def setTitle(self, title):
        self.titleInput.setText(title)

    def saveInputs(self):
        self.title = self.titleInput.text().strip()  # Store the section title
        for keyField, valueField in self.inputFields:
            key = keyField.text().strip()
            value = valueField.text().strip()
            if key:  # Only add non-empty keys
                self.inputs[key] = value
        self.accept()  # Close the dialog

    def getValues(self):
        return self.title, self.inputs

class AIAssistantGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initHomepage()
        self.client = OpenAI(api_key=os.environ['API_KEY'])  # Replace with your actual API key
        self.sectionInputs = {}  # Dictionary to track sections nd their inputs
        self.sentInputs = {}  # Dictionary to track if inputs have been sent

    def initHomepage(self):
        self.setWindowTitle('AI Assistant Hugo AI')
        self.setGeometry(100, 100, 2400, 1200)  # Window size
        self.setWindowIcon(QIcon('C:/Users/zorer/Downloads/hugoai.png'))  # Set the window icon to your logo

        # Main layout
        mainLayout = QHBoxLayout()
        self.sidebar = QListWidget()

        # Sidebar
        icons = ['C:/Users/zorer/Downloads/house.png', 'C:/Users/zorer/Downloads/pie-chart.png', 'C:/Users/zorer/Downloads/edit.png',
                 'C:/Users/zorer/Downloads/settings.png']
        for i, item_text in enumerate([" Home", " Integrations", " Create", " Settings"]):
            item = QListWidgetItem(item_text)
            item.setIcon(QIcon(icons[i]))
            # Add the item to the sidebar
            self.sidebar.addItem(item)

        self.sidebar.itemClicked.connect(self.onSidebarItemClicked)
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: rgba(240,240,240,255);
                border: none;
            }
            QListWidget::item {
                color: rgb(277,277,277);
                padding-top:220px;
                font-size:30px;
                font-family: 'Helvetica'; 
                font-weight: bold; 
    }
        """)

        # Existing layout for text edit and button
        layout = QVBoxLayout()

        self.textEdit = QTextEdit()
        ekin_initial_html = f"""
           <p><img src="C:/Users/zorer/Downloads/ekin.png" height="100" width="100"> <b>Ekin:</b></p>
           """
        self.textEdit.setHtml(ekin_initial_html)
        self.textEdit.installEventFilter(self)

        self.sendButton = QPushButton('Ask Hugo')
        self.sendButton.clicked.connect(self.send_query)

        layout.addWidget(self.textEdit)
        layout.addWidget(self.sendButton)

        mainLayout.addWidget(self.sidebar)
        mainLayout.addLayout(layout, 1)

        # Set the main layout as the central widget's layout
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def prependUserPrefix(self):
      currentText = self.textEdit.toPlainText()
      # Define the HTML content for "Ekin:" with the logo
      ekin_input_html = f"""
      <p><img src="C:/Users/zorer/Downloads/ekin.png" height="100" width="100"> <b>Ekin:</b></p>
      """
      # Check if the current text does not start with "Ekin: " and prepend the HTML content
      if not currentText.startswith("Ekin: "):
        self.textEdit.blockSignals(True)  # Block signals to prevent recursive calls
        # Prepend the HTML content for "Ekin:" with the logo
        self.textEdit.setHtml(ekin_input_html + self.textEdit.toHtml())
        self.textEdit.blockSignals(False)
      self.lastText = currentText

    def onSidebarItemClicked(self, item):
        if item.text() == " Create":
            self.createNew()
        elif item.text() in self.sectionInputs:
            self.editSection(item.text())
        if item.text() == " Integrations":
            self.integrationsWindow = Integrations(self)
            self.integrationsWindow.show()
            self.hide()
        if item.text() == " Home":
            self.homeWindow = AIAssistantGUI()
            self.homeWindow.show()
            self.hide()

    def editSection(self, sectionName):
        inputs = self.sectionInputs.get(sectionName, {})
        dialog = InputDialog(self)
        dialog.setWindowTitle("Edit Section")

        # Pre-fill the dialog with existing inputs
        dialog.setTitle(sectionName)  # You'll need to implement setTitle in InputDialog
        for i, (key, value) in enumerate(inputs.items()):
            if i < len(dialog.inputFields):
                keyField, valueField = dialog.inputFields[i]
                keyField.setText(key)
                valueField.setText(value)

        # Show the dialog to edit inputs
        if dialog.exec_() == QDialog.Accepted:
            title, newInputs = dialog.getValues()
            if title:
                self.sectionInputs[title] = newInputs

    def getIntegrations(self):
        ex = Integrations()
        ex.show()

    def createNew(self):
        dialog = InputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, inputs = dialog.getValues()
            if title:
                self.sidebar.addItem(title)
                self.sectionInputs[title] = inputs

    def eventFilter(self, source, event):
          # Make the Enter key function like the "Ask Hugo" button
          if (event.type() == QEvent.KeyRelease and
                  (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and
                  source is self.textEdit):
            # Prevents the new line from being added to the QTextEdit
            self.textEdit.textCursor().deletePreviousChar()
            self.send_query()
            return True
          return super(AIAssistantGUI, self).eventFilter(source, event)

    def send_query(self):
        userQuery = self.textEdit.toPlainText().replace("Ekin: ", "", 1)  # Remove the "Ekin: " prefix
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "getGmail",
                    "description": "Use this function to list the users most recent emails.",
                     "parameters": {
                        "type": "object",
                            "properties": {
                            # No properties needed since there are no parameters
                        },
                }
            }
                }
        ]
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": userQuery}
            ],
            tools=tools
        )

        ai_response = response.choices[0].message.content  # AI's response
        ai_response = ai_response.replace("Hugo AI:", "").strip()

        ai_response_html = f"""
              <p><img src="C:/Users/zorer/Downloads/hugoai.png" height="100" width="100"> <b>Hugo AI:</b> {ai_response}</p>
              """
          # Append the AI's response
        self.textEdit.append(ai_response_html)

          # Prepare for the next user input with "Ekin:" logo
        ekin_input_html = f"""
          <p><img src="C:/Users/zorer/Downloads/ekin.png" height="100" width="100"> <b>Ekin:</b> </p>
          """
        self.textEdit.append(ekin_input_html)
        self.textEdit.moveCursor(QTextCursor.End)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # Define a new signal called 'clicked'

    def __init__(self, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)  # Change cursor to pointing hand

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # Emit the 'clicked' signal when the label is clicked
        super(ClickableLabel, self).mousePressEvent(event)


class Integrations(QMainWindow):
    def __init__(self, parent=None):  # Add parent=None to accept an optional parent parameter
        super().__init__(parent)  # Pass the parent to the superclass __init__
        self.initIntegrations()

    def initIntegrations(self):
        self.setWindowTitle('AI Assistant Hugo AI')
        self.setGeometry(100, 100, 2400, 1200)

        # Sidebar
        self.sidebar = QListWidget()

        # Sidebar
        icons = ['C:/Users/zorer/Downloads/house.png', 'C:/Users/zorer/Downloads/pie-chart.png',
                 'C:/Users/zorer/Downloads/edit.png',
                 'C:/Users/zorer/Downloads/settings.png']
        for i, item_text in enumerate([" Home", " Integrations", " Create", " Settings"]):
            item = QListWidgetItem(item_text)
            item.setIcon(QIcon(icons[i]))
            # Add the item to the sidebar
            self.sidebar.addItem(item)

        self.sidebar.itemClicked.connect(self.onSidebarItemClicked)
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("""
                    QListWidget {
                        background-color: rgba(240,240,240,255);
                        border: none;
                    }
                    QListWidget::item {
                        color: rgb(277,277,277);
                        padding-top:220px;
                        font-size:30px;
                        font-family: 'Helvetica'; 
                        font-weight: bold; 
            }
                """)

        # Grid layout for labels
        gridLayout = QGridLayout()
        logos = ["C:/Users/zorer/Downloads/gmail.png", "C:/Users/zorer/Downloads/chase.png", "C:/Users/zorer/Downloads/googlecal.png",
                 "C:/Users/zorer/Downloads/united.png",
                 "C:/Users/zorer/Downloads/coned.png", "C:/Users/zorer/Downloads/amex.png"]
        for i, logo_path in enumerate(logos):
            if i == 0:  # For the first label, use the clickable subclass
                label = ClickableLabel()
                label.clicked.connect(getGmail)  # Connect the click event to the getGmail method
            else:
                label = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)  # Resize to 100x100 while keeping aspect ratio
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 1px solid black;")  # Optional: Adds a border to each label
            row, col = divmod(i, 3)
            gridLayout.addWidget(label, row, col)

        # Main layout
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.sidebar)
        mainLayout.addLayout(gridLayout)  # Add the grid layout to the main layout

        # Set the main layout as the central widget's layout
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def onSidebarItemClicked(self, item):
        if item.text() == " Create":
            self.createNew()
        # elif item.text() in self.sectionInputs:
        #     self.editSection(item.text())
        if item.text() == " Integrations":
            self.integrationsWindow = Integrations()
            self.integrationsWindow.show()
            self.hide()
        if item.text() == " Home":
            self.hide()  # Hide the current window
            self.parent().show()

def main():
    app = QApplication(sys.argv)
    ex = AIAssistantGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
