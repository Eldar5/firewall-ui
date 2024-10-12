from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QSpinBox, QPushButton, QVBoxLayout, QDialogButtonBox)
from models.rule import Rule, Protocol, Action, Direction

class RuleDialog(QDialog):
    def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Rule")
        self.rule = rule
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.source_address = QLineEdit()
        form_layout.addRow("Source Address:", self.source_address)

        self.source_port = QSpinBox()
        self.source_port.setRange(0, 65535)
        form_layout.addRow("Source Port:", self.source_port)

        self.destination_address = QLineEdit()
        form_layout.addRow("Destination Address:", self.destination_address)

        self.destination_port = QSpinBox()
        self.destination_port.setRange(0, 65535)
        form_layout.addRow("Destination Port:", self.destination_port)

        self.protocol = QComboBox()
        self.protocol.addItems([p.value for p in Protocol])
        form_layout.addRow("Protocol:", self.protocol)

        self.action = QComboBox()
        self.action.addItems([a.value for a in Action])
        form_layout.addRow("Action:", self.action)

        self.direction = QComboBox()
        self.direction.addItems([d.value for d in Direction])
        form_layout.addRow("Direction:", self.direction)

        self.description = QLineEdit()
        form_layout.addRow("Description:", self.description)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        if self.rule:
            self.populate_fields()

    def populate_fields(self):
        self.source_address.setText(self.rule.source_address)
        self.source_port.setValue(self.rule.source_port or 0)
        self.destination_address.setText(self.rule.destination_address)
        self.destination_port.setValue(self.rule.destination_port or 0)
        self.protocol.setCurrentText(self.rule.protocol.value)
        self.action.setCurrentText(self.rule.action.value)
        self.direction.setCurrentText(self.rule.direction.value)
        self.description.setText(self.rule.description)

    def get_rule(self):
        return Rule(
            id=self.rule.id if self.rule else 0,
            source_address=self.source_address.text(),
            source_port=self.source_port.value(),
            destination_address=self.destination_address.text(),
            destination_port=self.destination_port.value(),
            protocol=Protocol(self.protocol.currentText()),
            action=Action(self.action.currentText()),
            direction=Direction(self.direction.currentText()),
            description=self.description.text()
        )