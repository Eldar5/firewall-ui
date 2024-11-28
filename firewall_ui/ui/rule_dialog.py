from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QSpinBox, QPushButton, QVBoxLayout, QDialogButtonBox, 
                             QMessageBox, QGridLayout, QLabel)
from firewall_ui.models.rule import Rule, Protocol, Action, Direction
import ipaddress

def is_valid_ip(ip_string):
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

class RuleDialog(QDialog):
    def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Rule")
        self.rule = rule
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QGridLayout()
        current_row = 0

        # Source IP Range
        form_layout.addWidget(QLabel("Source IP Range:"), current_row, 0)
        self.source_address_start = QLineEdit()
        self.source_address_end = QLineEdit()
        ip_range_btn = QPushButton("*")
        ip_range_btn.clicked.connect(lambda: self.fill_ip_range(
            self.source_address_start, self.source_address_end))
        form_layout.addWidget(self.source_address_start, current_row, 1)
        form_layout.addWidget(QLabel("to"), current_row, 2)
        form_layout.addWidget(self.source_address_end, current_row, 3)
        form_layout.addWidget(ip_range_btn, current_row, 4)
        current_row += 1

        # Source Port Range
        form_layout.addWidget(QLabel("Source Port Range:"), current_row, 0)
        self.source_port_start = QSpinBox()
        self.source_port_end = QSpinBox()
        self.source_port_start.setRange(0, 65535)
        self.source_port_end.setRange(0, 65535)
        port_range_btn = QPushButton("*")
        port_range_btn.clicked.connect(lambda: self.fill_port_range(
            self.source_port_start, self.source_port_end))
        form_layout.addWidget(self.source_port_start, current_row, 1)
        form_layout.addWidget(QLabel("to"), current_row, 2)
        form_layout.addWidget(self.source_port_end, current_row, 3)
        form_layout.addWidget(port_range_btn, current_row, 4)
        current_row += 1

        # Destination IP Range
        form_layout.addWidget(QLabel("Destination IP Range:"), current_row, 0)
        self.destination_address_start = QLineEdit()
        self.destination_address_end = QLineEdit()
        ip_range_btn2 = QPushButton("*")
        ip_range_btn2.clicked.connect(lambda: self.fill_ip_range(
            self.destination_address_start, self.destination_address_end))
        form_layout.addWidget(self.destination_address_start, current_row, 1)
        form_layout.addWidget(QLabel("to"), current_row, 2)
        form_layout.addWidget(self.destination_address_end, current_row, 3)
        form_layout.addWidget(ip_range_btn2, current_row, 4)
        current_row += 1

        # Destination Port Range
        form_layout.addWidget(QLabel("Destination Port Range:"), current_row, 0)
        self.destination_port_start = QSpinBox()
        self.destination_port_end = QSpinBox()
        self.destination_port_start.setRange(0, 65535)
        self.destination_port_end.setRange(0, 65535)
        port_range_btn2 = QPushButton("*")
        port_range_btn2.clicked.connect(lambda: self.fill_port_range(
            self.destination_port_start, self.destination_port_end))
        form_layout.addWidget(self.destination_port_start, current_row, 1)
        form_layout.addWidget(QLabel("to"), current_row, 2)
        form_layout.addWidget(self.destination_port_end, current_row, 3)
        form_layout.addWidget(port_range_btn2, current_row, 4)
        current_row += 1

        # Other fields
        self.protocol = QComboBox()
        self.protocol.addItems([p.value for p in Protocol])
        form_layout.addWidget(QLabel("Protocol:"), current_row, 0)
        form_layout.addWidget(self.protocol, current_row, 1, 1, 3)
        current_row += 1

        self.action = QComboBox()
        self.action.addItems([a.value for a in Action])
        form_layout.addWidget(QLabel("Action:"), current_row, 0)
        form_layout.addWidget(self.action, current_row, 1, 1, 3)
        current_row += 1

        self.direction = QComboBox()
        self.direction.addItems([d.value for d in Direction])
        form_layout.addWidget(QLabel("Direction:"), current_row, 0)
        form_layout.addWidget(self.direction, current_row, 1, 1, 3)
        current_row += 1

        self.description = QLineEdit()
        form_layout.addWidget(QLabel("Description:"), current_row, 0)
        form_layout.addWidget(self.description, current_row, 1, 1, 3)

        layout.addLayout(form_layout)

        # Connect validation signals
        for field in [self.source_address_start, self.source_address_end,
                     self.destination_address_start, self.destination_address_end]:
            field.editingFinished.connect(self.validate_ip_fields)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.rule:
            self.populate_fields()

    def fill_ip_range(self, start_field, end_field):
        start_field.setText("0.0.0.0")
        end_field.setText("255.255.255.255")

    def fill_port_range(self, start_field, end_field):
        start_field.setValue(0)
        end_field.setValue(65535)

    def populate_fields(self):
        if self.rule:
            self.source_address_start.setText(self.rule.source_address_start)
            self.source_address_end.setText(self.rule.source_address_end)
            self.source_port_start.setValue(self.rule.source_port_start or 0)
            self.source_port_end.setValue(self.rule.source_port_end or 0)
            
            self.destination_address_start.setText(self.rule.destination_address_start)
            self.destination_address_end.setText(self.rule.destination_address_end)
            self.destination_port_start.setValue(self.rule.destination_port_start or 0)
            self.destination_port_end.setValue(self.rule.destination_port_end or 0)
            
            self.protocol.setCurrentText(self.rule.protocol.value)
            self.action.setCurrentText(self.rule.action.value)
            self.direction.setCurrentText(self.rule.direction.value)
            self.description.setText(self.rule.description)

    def get_rule(self):
        return Rule(
            id=self.rule.id if self.rule else 0,
            source_address_start=self.source_address_start.text(),
            source_address_end=self.source_address_end.text(),
            source_port_start=self.source_port_start.value(),
            source_port_end=self.source_port_end.value(),
            destination_address_start=self.destination_address_start.text(),
            destination_address_end=self.destination_address_end.text(),
            destination_port_start=self.destination_port_start.value(),
            destination_port_end=self.destination_port_end.value(),
            protocol=Protocol(self.protocol.currentText()),
            action=Action(self.action.currentText()),
            direction=Direction(self.direction.currentText()),
            description=self.description.text()
        )
    
    def validate_ip_fields(self):
        sender = self.sender()
        if not is_valid_ip(sender.text()):
            QMessageBox.warning(self, "Invalid IP", f"Please enter a valid IP address: {sender.text()}")
            sender.setFocus()

    def accept(self):
        try:
            rule = self.get_rule()
            rule.validate()
            super().accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))