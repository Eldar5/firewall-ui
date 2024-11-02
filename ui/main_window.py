from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QTextEdit, QMessageBox,
                             QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from .widgets.rule_table import RuleTableWidget
from .rule_dialog import RuleDialog
from utils.logger import FirewallLogger
from utils.kernel_comm import KernelCommunicator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = FirewallLogger()
        self.kernel_comm = KernelCommunicator()
        self.setWindowTitle("Firewall Rules Manager")
        self.setGeometry(100, 100, 740, 600)

        self.logger_instance = self.logger.get_logger()
        self.qt_handler = self.logger.get_qt_handler()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create error banner (hidden by default)
        self.error_banner = QLabel()
        self.error_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_banner.setStyleSheet("""
            QLabel {
                background-color: #ffebee;
                color: #c62828;
                padding: 10px;
                border: 1px solid #ef9a9a;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.error_banner.hide()
        self.main_layout.addWidget(self.error_banner)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create Rules Tab
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)

        # Create rule table
        self.rule_table = RuleTableWidget()
        rules_layout.addWidget(self.rule_table)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Add Rule button
        self.add_button = QPushButton("Add Rule")
        self.add_button.clicked.connect(self.add_rule)
        button_layout.addWidget(self.add_button)

        # Edit Rule button
        self.edit_button = QPushButton("Edit Rule")
        self.edit_button.clicked.connect(self.edit_rule)
        button_layout.addWidget(self.edit_button)

        # Delete Rule button
        self.delete_button = QPushButton("Delete Rule")
        self.delete_button.clicked.connect(self.delete_rule)
        button_layout.addWidget(self.delete_button)

        # Apply Rules button
        self.apply_button = QPushButton("Apply Rules")
        self.apply_button.clicked.connect(self.apply_rules)
        button_layout.addWidget(self.apply_button)

        # Store all control buttons for easy access
        self.control_buttons = [
            self.add_button, 
            self.edit_button, 
            self.delete_button, 
            self.apply_button
        ]

        rules_layout.addLayout(button_layout)

        # Create Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(rules_tab, "Firewall Rules")
        self.tab_widget.addTab(logs_tab, "Logs")

        # Connect the custom handler to update logs
        qt_handler = self.logger.get_qt_handler()
        qt_handler.new_log.connect(self.update_logs)

        # Get the logger instance
        self.logger = self.logger.get_logger()

        # Initialize with kernel rules
        self.load_kernel_rules()

    def show_error_state(self, message):
        """Display error banner and disable UI controls"""
        self.error_banner.setText(message)
        self.error_banner.show()
        
        # Disable all controls
        self.rule_table.setEnabled(False)
        for button in self.control_buttons:
            button.setEnabled(False)
            
        self.logger.error(message)

    def load_kernel_rules(self):
        """Load existing rules from kernel when application starts"""
        try:
            kernel_rules = self.kernel_comm.get_current_rules()
            
            if kernel_rules is None:  # No response from kernel
                self.show_error_state("Failed to communicate with kernel module. Please check if the module is loaded and try again.")
                return
                
            # Clear existing rules in table
            self.rule_table.setRowCount(0)
            
            if kernel_rules:  # If we got rules (empty list is okay)
                # Add each rule from kernel to the table
                for rule_dict in kernel_rules:
                    self.rule_table.add_rule_from_dict(rule_dict)
                self.logger.info(f"Loaded {len(kernel_rules)} rules from kernel")
            else:
                self.logger.info("No existing rules found in kernel")
                
        except Exception as e:
            self.show_error_state(f"Failed to initialize kernel communication: {str(e)}")

    def add_rule(self):
        dialog = RuleDialog(self)
        if dialog.exec():
            new_rule = dialog.get_rule()
            self.rule_table.add_rule(new_rule)
            self.logger.info(f"Added new rule: {new_rule}")

    def edit_rule(self):
        selected_row = self.rule_table.currentRow()
        if selected_row >= 0:
            rule = self.rule_table.get_rule(selected_row)
            dialog = RuleDialog(self, rule)
            if dialog.exec():
                updated_rule = dialog.get_rule()
                self.rule_table.update_rule(selected_row, updated_rule)
                self.logger.info(f"Updated rule: {updated_rule}")
        else:
            self.logger.warning("No rule selected for editing")

    def delete_rule(self):
        selected_row = self.rule_table.currentRow()
        if selected_row >= 0:
            rule = self.rule_table.get_rule(selected_row)
            self.rule_table.removeRow(selected_row)
            self.logger.info(f"Deleted rule: {rule}")
        else:
            self.logger.warning("No rule selected for deletion")

    def apply_rules(self):
        rules = self.rule_table.get_all_rules()
        success = self.kernel_comm.send_rules(rules)
        if success:
            self.logger.info("Rules successfully applied to kernel module")
        else:
            self.logger.error("Failed to apply rules to kernel module")

    def update_logs(self, log_text):
        self.log_text.append(log_text)

    def closeEvent(self, event):
        """Handle cleanup before window closes"""
        try:
            # Remove Qt handler from logger
            if self.qt_handler in self.logger_instance.handlers:
                self.logger_instance.removeHandler(self.qt_handler)
            
            # Close the kernel communicator
            if hasattr(self, 'kernel_comm'):
                self.kernel_comm.__del__()

        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # Call parent's closeEvent
        super().closeEvent(event)