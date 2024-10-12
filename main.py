import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import FirewallLogger

def main():
    # Initialize logger
    logger = FirewallLogger().get_logger()
    logger.info("Starting Firewall UI application")

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()