from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QWidget, QFormLayout, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class WebEnumerationTool(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.initUI()

    def initUI(self):
        # Layout
        layout = QVBoxLayout()

        # URL input
        input_layout = QFormLayout()
        self.url_entry = QLineEdit(self)
        self.url_entry.setPalette(QPalette(Qt.white))
        input_layout.addRow(QLabel("Enter URL:"), self.url_entry)

        # Enumerate Button
        self.enum_button = QPushButton("Enumerate", self)
        self.enum_button.clicked.connect(self.start_enumeration)
        input_layout.addWidget(self.enum_button)

        # Save to file button
        self.save_button = QPushButton("Save to File", self)
        button_palette = QPalette()
        button_palette.setColor(QPalette.ButtonText, Qt.black)
        self.save_button.setPalette(button_palette)
        self.save_button.clicked.connect(self.save_to_file)
        input_layout.addWidget(self.save_button)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.setPalette(button_palette)
        self.quit_button.clicked.connect(self.close)
        input_layout.addWidget(self.quit_button)

        # Output
        output_layout = QVBoxLayout()

        self.page_title_output = QTextEdit(self)
        self.meta_desc_output = QTextEdit(self)
        self.links_output = QTextEdit(self)
        self.subdomains_output = QTextEdit(self)
        self.ports_output = QTextEdit(self)
        self.dns_output = QTextEdit(self)

        for output in [self.page_title_output, self.meta_desc_output,
                       self.links_output, self.subdomains_output,
                       self.ports_output, self.dns_output]:
            output.setReadOnly(True)
            output.setFont(QFont("Courier"))
            output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        output_layout.addWidget(QLabel("Page Title:"))
        output_layout.addWidget(self.page_title_output)

        output_layout.addWidget(QLabel("Meta Description:"))
        output_layout.addWidget(self.meta_desc_output)

        output_layout.addWidget(QLabel("Links:"))
        output_layout.addWidget(self.links_output)

        output_layout.addWidget(QLabel("Subdomains:"))
        output_layout.addWidget(self.subdomains_output)

        output_layout.addWidget(QLabel("DNS Records:"))
        output_layout.addWidget(self.dns_output)

        output_layout.addWidget(QLabel("Port Scanning:"))
        output_layout.addWidget(self.ports_output)

        # Combine layouts
        container = QWidget()
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Window Settings
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Web Enumerator')

        # Dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def start_enumeration(self):
        url = self.url_entry.text()
        # Perform enumeration and update the output fields
        # You can add your code here to perform the enumeration and update the UI accordingly
        # Example:
        # title, desc, links, subdomains, ports, dns = perform_enumeration(url)
        # self.page_title_output.setPlainText(title)
        # self.meta_desc_output.setPlainText(desc)
        # self.links_output.setPlainText(links)
        # self.subdomains_output.setPlainText(subdomains)
        # self.ports_output.setPlainText(ports)
        # self.dns_output.setPlainText(dns)

    def save_to_file(self):
        # Open a file dialog to choose the save location
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(f"Page Title:\n{self.page_title_output.toPlainText()}\n\n")
                file.write(f"Meta Description:\n{self.meta_desc_output.toPlainText()}\n\n")
                file.write(f"Links:\n{self.links_output.toPlainText()}\n\n")
                file.write(f"Subdomains:\n{self.subdomains_output.toPlainText()}\n\n")
                file.write(f"Ports:\n{self.ports_output.toPlainText()}\n\n")
                file.write(f"DNS Records:\n{self.dns_output.toPlainText()}\n\n")
