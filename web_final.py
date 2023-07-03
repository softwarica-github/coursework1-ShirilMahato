import sys
import socket
import requests
import dns.resolver
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout, QWidget, QFormLayout, QSizePolicy,
    QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class EnumerationThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, url):
        QThread.__init__(self)
        self.url = url

    def run(self):
        results = {'links': [], 'subdomains': [], 'ports': [],
                   'page_title': '', 'meta_desc': '', 'dns_records': []}

        # Extract links
        try:
            response = requests.get(self.url, timeout=5)
        except requests.exceptions.RequestException as e:
            self.signal.emit({'error': f"Error: Failed to connect to {self.url}.\n{str(e)}\n"})
            return
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract page title
        page_title = soup.title.string if soup.title else 'No title found'
        results['page_title'] = page_title

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        results['meta_desc'] = meta_desc['content'] if meta_desc else 'No meta description found'

        # Extract links
        links = soup.find_all('a')
        for link in links:
            results['links'].append(link.get('href'))

        # Subdomain enumeration
        subdomains = ['www', 'mail', 'ftp', 'webmail', 'admin']
        domain = self.url.split('//')[-1].split('/')[0]
        for subdomain in subdomains:
            full_url = f"http://{subdomain}.{domain}"
            try:
                requests.get(full_url, timeout=3)
                results['subdomains'].append(full_url)
            except requests.exceptions.RequestException:
                pass

        # DNS enumeration
        try:
            answers = dns.resolver.resolve(domain, 'A')
            for rdata in answers:
                results['dns_records'].append(f"A record: {rdata.address}")
        except dns.resolver.NoAnswer:
            results['dns_records'].append('No A records found')
        except Exception as e:
            results['dns_records'].append(str(e))

        # Simple port scanning
        target = domain.split(':')[0]
        for port in range(1, 1024):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(0.1)
            result = s.connect_ex((target, port))
            if result == 0:
                results['ports'].append(port)
            s.close()

        self.signal.emit(results)


class WebEnumerationTool(QMainWindow):
    def __init__(self):
        super().__init__()
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
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def start_enumeration(self):
        url = self.url_entry.text()
        self.enum_thread = EnumerationThread(url)
        self.enum_thread.signal.connect(self.display_output)
        self.enum_thread.start()

    def display_output(self, results):
        if 'error' in results:
            self.links_output.setPlainText(results['error'])
        else:
            self.page_title_output.setPlainText(results['page_title'])
            self.meta_desc_output.setPlainText(results['meta_desc'])
            self.links_output.setPlainText("\n".join(results['links']))
            self.subdomains_output.setPlainText("\n".join(results['subdomains']))
            self.dns_output.setPlainText("\n".join(results['dns_records']))
            self.ports_output.setPlainText("\n".join([str(p) for p in results['ports']]))

    def save_to_file(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filePath:
            with open(filePath, 'w') as file:
                file.write(f"Page Title:\n{self.page_title_output.toPlainText()}\n")
                file.write(f"Meta Description:\n{self.meta_desc_output.toPlainText()}\n")
                file.write(f"Links:\n{self.links_output.toPlainText()}\n")
                file.write(f"Subdomains:\n{self.subdomains_output.toPlainText()}\n")
                file.write(f"DNS Records:\n{self.dns_output.toPlainText()}\n")
                file.write(f"Port Scanning:\n{self.ports_output.toPlainText()}\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = WebEnumerationTool()
    mainWin.show()
    sys.exit(app.exec_())
