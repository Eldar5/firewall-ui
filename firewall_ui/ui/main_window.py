from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from firewall_ui.ui.rule_dialog import RuleDialog
from firewall_ui.ui.widgets.rule_table import RuleTableWidget
from firewall_ui.utils.logger import FirewallLogger
from firewall_ui.utils.kernel_comm import KernelCommunicator
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger_manager = FirewallLogger()
        self.logger = self.logger_manager.get_logger()
        self.kernel_comm = KernelCommunicator()
        self.setWindowTitle("Firewall Rules Manager")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create Rules Tab
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)

        # Create rule table
        self.rule_table = RuleTableWidget()
        rules_layout.addWidget(self.rule_table)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Add Rule button
        add_button = QPushButton("Add Rule")
        add_button.clicked.connect(self.add_rule)
        button_layout.addWidget(add_button)

        # Edit Rule button
        edit_button = QPushButton("Edit Rule")
        edit_button.clicked.connect(self.edit_rule)
        button_layout.addWidget(edit_button)

        # Delete Rule button
        delete_button = QPushButton("Delete Rule")
        delete_button.clicked.connect(self.delete_rule)
        button_layout.addWidget(delete_button)

        # Apply Rules button
        apply_button = QPushButton("Apply Rules")
        apply_button.clicked.connect(self.apply_rules)
        button_layout.addWidget(apply_button)

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
        qt_handler = self.logger_manager.get_qt_handler()
        qt_handler.new_log.connect(self.update_logs)

        # Load initial configuration
        self.load_initial_config()

    def load_initial_config(self):
        config, error = self.kernel_comm.get_current_config()
        if error:
            self.logger.error(f"Failed to load initial config: {error}")
            QMessageBox.warning(self, "Communication Error",
                              f"Failed to load configuration from kernel module: {error}\n"
                              "The application will start with empty configuration.")
        else:
            self.rule_table.load_rules(config)
            self.logger.info("Successfully loaded configuration from kernel module")

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
       success, error, validation_error = self.kernel_comm.send_config(rules)
       if success:
           if validation_error:
               self.logger.warning(f"Rules applied but validation failed: {validation_error}")
               QMessageBox.warning(self, "Warning", 
                                 f"Rules were applied but validation failed:\n{validation_error}")
           else:
               self.logger.info("Rules successfully applied and validated")
               QMessageBox.information(self, "Success", 
                                     "Rules successfully applied and validated")
       else:
           self.logger.error(f"Failed to apply rules: {error}")
           QMessageBox.critical(self, "Error", f"Failed to apply rules: {error}")
    
    def update_logs(self, log_text):
        self.log_text.append(log_text)