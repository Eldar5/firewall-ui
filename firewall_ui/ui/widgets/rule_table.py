from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from firewall_ui.models.rule import Rule, Protocol, Action, Direction

class RuleTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setup_table()
        
    def setup_table(self):
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "ID", "Source", "Destination", "Protocol", 
            "Action", "Direction", "Enabled", "Description"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        
    def load_rules(self, config):
        self.setRowCount(0)
        for rule_data in config:
            rule = Rule(
                id=rule_data.get('id', 0),
                source_address_start=rule_data['source_address_start'],
                source_address_end=rule_data['source_address_end'],
                source_port_start=rule_data.get('source_port_start'),
                source_port_end=rule_data.get('source_port_end'),
                destination_address_start=rule_data['destination_address_start'],
                destination_address_end=rule_data['destination_address_end'],
                destination_port_start=rule_data.get('destination_port_start'),
                destination_port_end=rule_data.get('destination_port_end'),
                protocol=Protocol(rule_data['protocol']),
                action=Action(rule_data['action']),
                direction=Direction(rule_data['direction']),
                enabled=rule_data.get('enabled', True),
                description=rule_data.get('description', '')
            )
            self.add_rule(rule)

    def add_rule(self, rule):
        row = self.rowCount()
        self.insertRow(row)
        
        # Set ID
        id_item = QTableWidgetItem(str(rule.id))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(row, 0, id_item)
        
        # Set source with ranges
        source_ip = (f"{rule.source_address_start}-{rule.source_address_end}" 
                    if rule.source_address_start != rule.source_address_end 
                    else rule.source_address_start)
        source_port = (f"{rule.source_port_start}-{rule.source_port_end}"
                      if rule.source_port_start != rule.source_port_end and rule.source_port_start is not None
                      else str(rule.source_port_start) if rule.source_port_start is not None else "")
        source = f"{source_ip}:{source_port}" if source_port else source_ip
        self.setItem(row, 1, QTableWidgetItem(source))
        
        # Set destination with ranges
        dest_ip = (f"{rule.destination_address_start}-{rule.destination_address_end}"
                  if rule.destination_address_start != rule.destination_address_end
                  else rule.destination_address_start)
        dest_port = (f"{rule.destination_port_start}-{rule.destination_port_end}"
                    if rule.destination_port_start != rule.destination_port_end and rule.destination_port_start is not None
                    else str(rule.destination_port_start) if rule.destination_port_start is not None else "")
        dest = f"{dest_ip}:{dest_port}" if dest_port else dest_ip
        self.setItem(row, 2, QTableWidgetItem(dest))
        
        # Set other fields
        self.setItem(row, 3, QTableWidgetItem(rule.protocol.value))
        self.setItem(row, 4, QTableWidgetItem(rule.action.value))
        self.setItem(row, 5, QTableWidgetItem(rule.direction.value))
        
        enabled_item = QTableWidgetItem()
        enabled_item.setCheckState(Qt.CheckState.Checked if rule.enabled else Qt.CheckState.Unchecked)
        self.setItem(row, 6, enabled_item)
        
        self.setItem(row, 7, QTableWidgetItem(rule.description))

    def get_rule(self, row):
        # Parse source IP and port ranges
        source = self.item(row, 1).text()
        source_parts = source.split(':')
        source_ip_range = source_parts[0].split('-')
        source_address_start = source_ip_range[0]
        source_address_end = source_ip_range[1] if len(source_ip_range) > 1 else source_ip_range[0]
        
        source_port_start = None
        source_port_end = None
        if len(source_parts) > 1:
            port_range = source_parts[1].split('-')
            source_port_start = int(port_range[0]) if port_range[0] else None
            source_port_end = int(port_range[1]) if len(port_range) > 1 else source_port_start
        
        # Parse destination IP and port ranges
        dest = self.item(row, 2).text()
        dest_parts = dest.split(':')
        dest_ip_range = dest_parts[0].split('-')
        dest_address_start = dest_ip_range[0]
        dest_address_end = dest_ip_range[1] if len(dest_ip_range) > 1 else dest_ip_range[0]
        
        dest_port_start = None
        dest_port_end = None
        if len(dest_parts) > 1:
            port_range = dest_parts[1].split('-')
            dest_port_start = int(port_range[0]) if port_range[0] else None
            dest_port_end = int(port_range[1]) if len(port_range) > 1 else dest_port_start
        
        return Rule(
            id=int(self.item(row, 0).text()),
            source_address_start=source_address_start,
            source_address_end=source_address_end,
            source_port_start=source_port_start,
            source_port_end=source_port_end,
            destination_address_start=dest_address_start,
            destination_address_end=dest_address_end,
            destination_port_start=dest_port_start,
            destination_port_end=dest_port_end,
            protocol=Protocol(self.item(row, 3).text()),
            action=Action(self.item(row, 4).text()),
            direction=Direction(self.item(row, 5).text()),
            enabled=self.item(row, 6).checkState() == Qt.CheckState.Checked,
            description=self.item(row, 7).text()
        )

    def get_all_rules(self):
        return [self.get_rule(row) for row in range(self.rowCount())]

    def update_rule(self, row, rule):
        self.setItem(row, 0, QTableWidgetItem(str(rule.id)))
        
        # Update source with ranges
        source_ip = (f"{rule.source_address_start}-{rule.source_address_end}"
                    if rule.source_address_start != rule.source_address_end
                    else rule.source_address_start)
        source_port = (f"{rule.source_port_start}-{rule.source_port_end}"
                      if rule.source_port_start != rule.source_port_end and rule.source_port_start is not None
                      else str(rule.source_port_start) if rule.source_port_start is not None else "")
        source = f"{source_ip}:{source_port}" if source_port else source_ip
        self.setItem(row, 1, QTableWidgetItem(source))
        
        # Update destination with ranges
        dest_ip = (f"{rule.destination_address_start}-{rule.destination_address_end}"
                  if rule.destination_address_start != rule.destination_address_end
                  else rule.destination_address_start)
        dest_port = (f"{rule.destination_port_start}-{rule.destination_port_end}"
                    if rule.destination_port_start != rule.destination_port_end and rule.destination_port_start is not None
                    else str(rule.destination_port_start) if rule.destination_port_start is not None else "")
        dest = f"{dest_ip}:{dest_port}" if dest_port else dest_ip
        self.setItem(row, 2, QTableWidgetItem(dest))
        
        # Update other fields
        self.setItem(row, 3, QTableWidgetItem(rule.protocol.value))
        self.setItem(row, 4, QTableWidgetItem(rule.action.value))
        self.setItem(row, 5, QTableWidgetItem(rule.direction.value))
        enabled_item = QTableWidgetItem()
        enabled_item.setCheckState(Qt.CheckState.Checked if rule.enabled else Qt.CheckState.Unchecked)
        self.setItem(row, 6, enabled_item)
        self.setItem(row, 7, QTableWidgetItem(rule.description))