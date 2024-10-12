from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from models.rule import Rule

class RuleTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "ID", "Source", "Destination", "Protocol", 
            "Action", "Direction", "Enabled", "Description"
        ])
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def add_rule(self, rule):
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.set_rule_data(row_position, rule)

    def update_rule(self, row, rule):
        self.set_rule_data(row, rule)

    def set_rule_data(self, row, rule):
        self.setItem(row, 0, QTableWidgetItem(str(rule.id)))
        self.setItem(row, 1, QTableWidgetItem(f"{rule.source_address}:{rule.source_port}"))
        self.setItem(row, 2, QTableWidgetItem(f"{rule.destination_address}:{rule.destination_port}"))
        self.setItem(row, 3, QTableWidgetItem(rule.protocol.value))
        self.setItem(row, 4, QTableWidgetItem(rule.action.value))
        self.setItem(row, 5, QTableWidgetItem(rule.direction.value))
        self.setItem(row, 6, QTableWidgetItem("Yes" if rule.enabled else "No"))
        self.setItem(row, 7, QTableWidgetItem(rule.description))

    def get_rule(self, row):
        return Rule(
            id=int(self.item(row, 0).text()),
            source_address=self.item(row, 1).text().split(":")[0],
            source_port=int(self.item(row, 1).text().split(":")[1]),
            destination_address=self.item(row, 2).text().split(":")[0],
            destination_port=int(self.item(row, 2).text().split(":")[1]),
            protocol=self.item(row, 3).text(),
            action=self.item(row, 4).text(),
            direction=self.item(row, 5).text(),
            enabled=self.item(row, 6).text() == "Yes",
            description=self.item(row, 7).text()
        )

    def get_all_rules(self):
        return [self.get_rule(row) for row in range(self.rowCount())]