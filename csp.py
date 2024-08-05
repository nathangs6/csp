from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog
)
import inspect
import os
import configparser
from CustomWidgets import create_practice_layout


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "config.ini")


def _get_file_with_extensions(file_list, exts):
    for file in file_list:
        for ext in exts:
            if ext in file:
                return file
    return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chinese Story Practice")
        self.setWindowIcon(QIcon('logo.jpg'))

        open_lesson = QAction("&Open lesson", self)
        open_lesson.setStatusTip("Open a lesson folder")
        open_lesson.triggered.connect(self.open_lesson)
        set_home_dir = QAction("&Set Home Directory", self)
        set_home_dir.setStatusTip("Set a home directory to always open to")
        set_home_dir.triggered.connect(self.set_home_directory)
        menu = self.menuBar()
        menu = menu.addMenu("&File")
        menu.addAction(open_lesson)
        menu.addAction(set_home_dir)

        main_layout, widgets = create_practice_layout()
        self.widgets = widgets
        self.widgets["directory_explorer"].tree_view.doubleClicked.connect(self.open_lesson_from_button)
        self.widgets["directory_explorer"].open_lesson_button.clicked.connect(self.open_lesson_from_button)
        self.widgets["directory_explorer"].make_lesson_button.clicked.connect(self.make_lesson_from_button)

        self.load_config()

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        home_dir = config.get("General", "home_directory")
        try:
            self.widgets["directory_explorer"].set_root_directory(home_dir)
        except:
            print("Invalid home directory!")

    def set_home_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Home Directory")
        if folder:
            self.widgets["directory_explorer"].set_root_directory(folder)
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            general = config["General"]
            general["home_directory"] = folder
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        else:
            print("No folder selected!")

    def open_lesson(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Lesson")
        if folder:
            self.fill_layout(folder)
        else:
            print("No folder selected!")

    def open_lesson_from_button(self):
        lesson = self.widgets["directory_explorer"].get_folder_selection()
        if lesson and ".lesson" in os.listdir(lesson):
            self.fill_layout(lesson)
        else:
            print("No folder selected!")

    def make_lesson_from_button(self):
        lesson = self.widgets["directory_explorer"].get_folder_selection()
        if lesson:
            file_path = os.path.join(lesson, ".lesson")
            with open(file_path, 'w') as file:
                file.write("")


    def fill_layout(self, folder):
        files = os.listdir(folder)
        # Get files
        audio_file = _get_file_with_extensions(files, [".m4a", ".mp3"])
        if audio_file:
            audio_file = os.path.abspath(os.path.join(folder, audio_file))
            self.widgets["audio_player"].open_file(QUrl.fromLocalFile(audio_file))
        else:
            return None
        
        pdf_file = _get_file_with_extensions(files, [".pdf"])
        if pdf_file:
            pdf_file = os.path.abspath(os.path.join(folder, pdf_file))
            self.widgets["pdf_reader"].open_file(pdf_file)

        story_file = os.path.abspath(os.path.join(folder, "story.txt"))
        if "story.txt" not in files:
            file = open(story_file, 'w')
            file.write("# Story")
            file.close()
        self.widgets["story_text"].open_file(story_file)

        homework_file = os.path.abspath(os.path.join(folder, "homework.txt"))
        if "homework.txt" not in files:
            file = open(homework_file, 'w')
            file.write("# Homework")
            file.close()
        self.widgets["homework_text"].open_file(homework_file)

        log_file = os.path.abspath(os.path.join(folder, "log.txt"))
        if "log.txt" not in files:
            file = open(log_file, 'w')
            file.write("")
            file.close()
        self.widgets["timer"].open_file(log_file)
        self.widgets["timer"].reset()

        
def create_config():
    config = configparser.ConfigParser()

    config["General"] = {
        "home_directory": os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    }
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


code_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if "config.ini" not in os.listdir(code_dir):
    create_config()


app = QApplication([])

window = MainWindow()
window.showMaximized()
app.exec()