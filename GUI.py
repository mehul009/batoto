# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 17:27:14 2024

@author: mehul
"""

import sys
from PyQt5.QtWidgets import QApplication, QInputDialog, QFileDialog, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QCheckBox, QListWidget, QComboBox


def show_warning(warning_text):
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    msg.setText(warning_text)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

#URL asker
def get_user_input(lbl, lbl2="input"):
    app = QApplication(sys.argv)
    
    # Create a QLineEdit for user input
    input_field = QLineEdit()
    
    # Open a dialog box to get user input
    input_text, ok = QInputDialog.getText(None, lbl, lbl2, QLineEdit.EchoMode.Normal, input_field.text())
    
    if ok:
        # Return the user input
        return input_text
    else:
        # If user cancels, return None
        return None

#output folder selector
def select_folder():
    app = QApplication(sys.argv)
    folder_path = QFileDialog.getExistingDirectory()
    return folder_path

#Chapter selector window start
class ChapterSelectorWindow(QWidget):
    def __init__(self, chapters):
        super().__init__()
        self.chapters = chapters
        self.initUI()
        self.result = None
    def initUI(self):
        self.setWindowTitle('Chapter Selector')
        layout = QVBoxLayout()
        self.all_checkbox = QCheckBox('Include all chapters')
        layout.addWidget(self.all_checkbox)
        self.start_label = QLabel('Start chapter:')
        layout.addWidget(self.start_label)
        self.start_combo = QComboBox()
        self.start_combo.addItems([str(i) for i in self.chapters])
        layout.addWidget(self.start_combo)
        self.end_label = QLabel('End chapter:')
        layout.addWidget(self.end_label)
        self.end_combo = QComboBox()
        self.end_combo.addItems([str(i) for i in self.chapters])
        layout.addWidget(self.end_combo)
        self.selected_chapters_label = QLabel('Selected Chapters:')
        layout.addWidget(self.selected_chapters_label)
        self.selected_chapters_list = QListWidget()
        layout.addWidget(self.selected_chapters_list)
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
    def submit(self):
        all_chapters = self.all_checkbox.isChecked()
        start_chapter = self.start_combo.currentText()
        end_chapter = self.end_combo.currentText()
        self.result = [all_chapters, start_chapter, end_chapter]
        self.close()

def chapter_selector(chapters):
    app = QApplication(sys.argv)
    window = ChapterSelectorWindow(chapters)
    window.show()
    app.exec()        
    return [window.result[0], chapters.index(window.result[1]), chapters.index(window.result[2])]
#Chapter selector window end

