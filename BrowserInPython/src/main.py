import os
import sys
import venv
import subprocess


def install_package(package_name):
    """Instala um pacote usando pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def is_module_installed(module_name):
    """Verifica se um módulo pode ser importado."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def create_virtualenv(env_name="myenv"):
    """Cria um ambiente virtual se ele não existir."""
    if not os.path.exists(env_name):
        venv.create(env_name, with_pip=True)
        print(f"Ambiente virtual '{env_name}' criado.")
    else:
        print(f"Ambiente virtual '{env_name}' já existe.")


def get_venv_python(env_name="myenv"):
    """Retorna o caminho do executável Python do ambiente virtual."""
    if os.name == "nt":
        return os.path.join(env_name, "Scripts", "python.exe")
    return os.path.join(env_name, "bin", "python")


def ensure_packages_in_venv(env_name="myenv"):
    """Instala os pacotes necessários dentro do ambiente virtual."""
    venv_python = get_venv_python(env_name)

    if not os.path.exists(venv_python):
        raise FileNotFoundError(f"Python do ambiente virtual não encontrado em: {venv_python}")

    required_packages = [
        ("PyQt5", "PyQt5"),
        ("PyQtWebEngine", "PyQt5.QtWebEngineWidgets"),
    ]

    for package_name, module_name in required_packages:
        try:
            subprocess.check_call([venv_python, "-c", f"import {module_name}"])
            print(f"{package_name} já está instalado.")
        except subprocess.CalledProcessError:
            print(f"{package_name} não encontrado. Instalando...")
            subprocess.check_call([venv_python, "-m", "pip", "install", package_name])


class WebBrowser:
    pass


def run_browser():
    """Executa o navegador PyQt."""
    try:
        from PyQt5.QtWidgets import (
            QApplication,
            QMainWindow,
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QPushButton,
            QLineEdit,
        )
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtCore import QUrl, Qt
        from PyQt5.QtGui import QFont
    except ImportError as e:
        print(f"Falha ao importar módulos do PyQt: {e}")
        sys.exit(1)

    class WebBrowser(QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.setWindowTitle("Web Browser")
            self.setGeometry(200, 100, 1200, 800)

            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl("https://www.google.com"))
            self.browser.setZoomFactor(1.25)

            self.url_bar = QLineEdit()
            self.url_bar.setMaximumHeight(40)
            self.url_bar.setFont(QFont("Roboto", 12))
            self.url_bar.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 8px;
                    background: #f5f5f5;
                }
                QLineEdit:focus {
                    border: 1px solid #6200ea;
                    background: #ffffff;
                }
            """)
            self.url_bar.returnPressed.connect(self.navigate_to_url)

            self.go_btn = QPushButton("Go")
            self.go_btn.setMaximumHeight(40)
            self.go_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.go_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6200ea;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #3700b3;
                }
            """)
            self.go_btn.clicked.connect(self.navigate_to_url)

            self.back_btn = QPushButton("<")
            self.back_btn.setMaximumHeight(40)
            self.back_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.back_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #6200ea;
                    color: #6200ea;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.back_btn.clicked.connect(self.browser.back)

            self.forward_btn = QPushButton(">")
            self.forward_btn.setMaximumHeight(40)
            self.forward_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.forward_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #6200ea;
                    color: #6200ea;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.forward_btn.clicked.connect(self.browser.forward)

            self.reload_btn = QPushButton("Reload")
            self.reload_btn.setMaximumHeight(40)
            self.reload_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.reload_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #6200ea;
                    color: #6200ea;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.reload_btn.clicked.connect(self.browser.reload)

            self.zoom_in_btn = QPushButton("+")
            self.zoom_in_btn.setMaximumHeight(40)
            self.zoom_in_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.zoom_in_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #6200ea;
                    color: #6200ea;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.zoom_in_btn.clicked.connect(self.zoom_in)

            self.zoom_out_btn = QPushButton("-")
            self.zoom_out_btn.setMaximumHeight(40)
            self.zoom_out_btn.setFont(QFont("Roboto", 12, QFont.Bold))
            self.zoom_out_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #6200ea;
                    color: #6200ea;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            self.zoom_out_btn.clicked.connect(self.zoom_out)

            self.layout = QVBoxLayout()
            self.horizontal_layout = QHBoxLayout()
            self.horizontal_layout.setSpacing(10)

            self.horizontal_layout.addWidget(self.url_bar)
            self.horizontal_layout.addWidget(self.go_btn)
            self.horizontal_layout.addWidget(self.back_btn)
            self.horizontal_layout.addWidget(self.forward_btn)
            self.horizontal_layout.addWidget(self.reload_btn)
            self.horizontal_layout.addWidget(self.zoom_in_btn)
            self.horizontal_layout.addWidget(self.zoom_out_btn)

            self.layout.addLayout(self.horizontal_layout)
            self.layout.addWidget(self.browser)

            container = QWidget()
            container.setLayout(self.layout)
            self.setCentralWidget(container)

        def navigate_to_url(self):
            url = self.url_bar.text().strip()
            if not url:
                return
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            self.browser.setUrl(QUrl(url))

        def zoom_in(self):
            current_zoom = self.browser.zoomFactor()
            self.browser.setZoomFactor(current_zoom + 0.1)

        def zoom_out(self):
            current_zoom = self.browser.zoomFactor()
            self.browser.setZoomFactor(max(0.1, current_zoom - 0.1))

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_F11:
                self.toggle_fullscreen()
            else:
                super().keyPressEvent(event)

        def toggle_fullscreen(self):
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    app = QApplication(sys.argv)
    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())


def main():
    env_name = "myenv"
    create_virtualenv(env_name)
    ensure_packages_in_venv(env_name)

    print("\nPacotes instalados no ambiente virtual.")
    print("Para executar corretamente, rode este script usando o Python do venv.")
    print(f"Exemplo: {get_venv_python(env_name)} {os.path.basename(__file__)}\n")

    if is_module_installed("PyQt5") and is_module_installed("PyQt5.QtWebEngineWidgets"):
        run_browser()
    else:
        print("Os módulos PyQt não estão disponíveis no interpretador atual.")
        print("Ative o ambiente virtual e execute o script novamente.")


if __name__ == "__main__":
    main()


