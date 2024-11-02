import logging
import logging.handlers
from pathlib import Path
import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class QTextEditHandler(QObject, logging.Handler):
    new_log = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.flushOnClose = False  # Prevent flush attempts during shutdown

    def emit(self, record):
        msg = self.format(record)
        self.new_log.emit(msg)

    def close(self):
        """Clean up resources used by the handler."""
        try:
            super().close()
        except:
            pass

class FirewallLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("FirewallUI")
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler for all logs
        all_logs = logging.handlers.RotatingFileHandler(
            log_dir / "firewall.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        all_logs.setFormatter(file_formatter)
        all_logs.setLevel(logging.DEBUG)
        
        # File handler for error logs
        error_logs = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        error_logs.setFormatter(file_formatter)
        error_logs.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # QTextEdit handler
        self.qt_handler = QTextEditHandler()
        self.qt_handler.setFormatter(file_formatter)
        self.qt_handler.setLevel(logging.DEBUG)
        
        # Add handlers to logger
        self.logger.addHandler(all_logs)
        self.logger.addHandler(error_logs)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(self.qt_handler)
    
    def get_logger(self):
        return self.logger

    def get_qt_handler(self):
        return self.qt_handler

    def cleanup(self):
        """Clean up logger resources"""
        try:
            if self.qt_handler in self.logger.handlers:
                self.logger.removeHandler(self.qt_handler)
                self.qt_handler.close()
        except Exception as e:
            print(f"Error during logger cleanup: {e}")