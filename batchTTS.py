import random
import signal
import string
import sys
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QTextEdit, QLabel, QCheckBox, QPushButton, QHBoxLayout
from gtts import gTTS

IBM_API_KEY = ""


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        Path("./output").mkdir(parents=True, exist_ok=True)

        letters = string.ascii_lowercase
        self.current_subdir_index = ''.join(random.choice(letters) for i in range(4)) + "@" + datetime.today().strftime('%m-%d-%H:%M')
        Path("./output/" + self.current_subdir_index).mkdir(parents=True, exist_ok=True)

        self.layout = QGridLayout()
        self.resize(400, 200)
        self.setWindowTitle("BatchTTS")

        self.layout.addWidget(QLabel("Text"), 0, 0)
        self.textInput = QTextEdit()
        self.layout.addWidget(self.textInput, 1, 0)

        self.layout.addWidget(QLabel("Batch mode creates a sound file for every line in the textbox. When NOT wrapped in [ and ], the text will be TTSed through the IBM Cloud."), 2, 0)
        self.activateBatchMode = QCheckBox("Activate Batch Mode")
        self.layout.addWidget(self.activateBatchMode, 3, 0)

        self.buttonbox = QHBoxLayout()
        self.createBtn = QPushButton("Create")
        self.createBtn.clicked.connect(self.create_tts)
        self.closeBtn = QPushButton("Close")
        self.closeBtn.clicked.connect(self.close)
        self.buttonbox.addWidget(self.createBtn)
        self.buttonbox.addWidget(self.closeBtn)
        self.layout.addLayout(self.buttonbox, 4, 0)

        self.setLayout(self.layout)
        self.show()

        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def create_tts(self):
        if self.activateBatchMode.isChecked():
            for line in self.textInput.toPlainText().split("\n"):
                if line:
                    if line.startswith("[") and line.endswith("]"):
                        tts = gTTS(line, tld="as")  # using the TLD of american samoa so that we can get that neat murican accent even in europe
                        tts.save("./output/" + self.current_subdir_index + "/" + "".join(x for x in line if x.isalnum())[:15] + ".mp3")
                    else:
                        self.ibm_cloud_save(line)
        else:
            tts = gTTS(self.textInput.toPlainText(), tld="as")  # using the TLD of american samoa so that we can get that neat murican accent even in europe
            tts.save("./output/" + self.current_subdir_index + "/" + "".join(x for x in self.textInput.toPlainText() if x.isalnum())[:15] + ".mp3")

    def ibm_cloud_save(self, text):
        import requests

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'audio/wav',
        }

        data = '{"text":"' + text + '"}'

        response = requests.post(
            'https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/' + IBM_API_KEY + '/v1/synthesize',
            headers=headers, data=data, auth=('apikey', 'hE4FwLVFAo1aqpG2NdwZU-_fY5A-9MhpeM5a5jAKp_zd'))
        with open("./output/" + self.current_subdir_index + "/" + "".join(x for x in text if x.isalnum())[:15] + ".mp3", "wb") as f:
            f.write(response.content)


app = QApplication(sys.argv)
win = MainWindow()
sys.exit(app.exec_())
