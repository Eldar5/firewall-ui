from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from firewall_ui.models.rule import Rule, Protocol, Action, Direction

class RuleTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def currentRow(self):
        """Get the currently selected row"""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            return -1
        return selected_rows[0].row()

    def removeRow(self, row):
        """Remove a row from the table"""
        self.table.removeRow(row)
        self.update_rule_ids()  # Update IDs after deletion

    def clone_rule(self, row):
        """Clone a rule at the specified row and add it as a new rule"""
        if row < 0 or row >= self.table.rowCount():
            return

        # Get the rule to clone
        original_rule = self.get_rule(row)

        # Create new rule with same data but new ID
        new_rule = Rule(
            id=self.table.rowCount() + 1,  # New ID will be set by add_rule
            source_address_start=original_rule.source_address_start,
            source_address_end=original_rule.source_address_end,
            source_port_start=original_rule.source_port_start,
            source_port_end=original_rule.source_port_end,
            destination_address_start=original_rule.destination_address_start,
            destination_address_end=original_rule.destination_address_end,
            destination_port_start=original_rule.destination_port_start,
            destination_port_end=original_rule.destination_port_end,
            protocol=original_rule.protocol,
            action=original_rule.action,
            direction=original_rule.direction,
            enabled=original_rule.enabled,
            description=f"{original_rule.description}"
        )

        # Add the cloned rule
        self.add_rule(new_rule)

    # Select the new rule
        self.table.selectRow(self.table.rowCount() - 1)

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Button container
        button_layout = QVBoxLayout()
        
        # Create up/down buttons
        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")
        self.up_button.clicked.connect(self.move_row_up)
        self.down_button.clicked.connect(self.move_row_down)
        
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addStretch()  # Pushes buttons to the top
        
        layout.addLayout(button_layout)
        
        # Create table
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
    def setup_table(self):
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Source", "Destination", "Protocol", 
            "Action", "Direction", "Enabled", "Description"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    
    def move_row_up(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            return
            
        current_row = selected_rows[0].row()
        if current_row <= 0:
            return
            
        self.swap_rows(current_row, current_row - 1)
        self.table.selectRow(current_row - 1)
    
    def move_row_down(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            return
            
        current_row = selected_rows[0].row()
        if current_row >= self.table.rowCount() - 1:
            return
            
        self.swap_rows(current_row, current_row + 1)
        self.table.selectRow(current_row + 1)
    
    def swap_rows(self, row1, row2):
        # Store data from both rows
        row1_data = []
        row2_data = []
        
        for col in range(self.table.columnCount()):
            # Save row1 data
            item1 = self.table.item(row1, col)
            if col == 6:  # Enabled column (checkbox)
                row1_data.append(item1.checkState())
            else:
                row1_data.append(item1.text() if item1 else "")
                
            # Save row2 data
            item2 = self.table.item(row2, col)
            if col == 6:  # Enabled column (checkbox)
                row2_data.append(item2.checkState())
            else:
                row2_data.append(item2.text() if item2 else "")
        
        # Swap the data
        for col in range(self.table.columnCount()):
            if col == 6:  # Enabled column (checkbox)
                item1 = QTableWidgetItem()
                item1.setCheckState(row2_data[col])
                item2 = QTableWidgetItem()
                item2.setCheckState(row1_data[col])
            else:
                item1 = QTableWidgetItem(row2_data[col])
                item2 = QTableWidgetItem(row1_data[col])
                
                if col == 0:  # ID column
                    item1.setFlags(item1.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item2.setFlags(item2.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
            self.table.setItem(row1, col, item1)
            self.table.setItem(row2, col, item2)
        
        self.update_rule_ids()
    
    def update_rule_ids(self):
        """Update rule IDs after row reordering"""
        for row in range(self.table.rowCount()):
            # Update ID in table
            id_item = QTableWidgetItem(str(row + 1))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, id_item)
    
    def load_rules(self, config):
        self.table.setRowCount(0)
        for rule_data in config:
            rule = Rule(
                id=rule_data.get('id', 0),
                source_address_start=rule_data.get('source_address_start'),
                source_address_end=rule_data.get('source_address_end'),
                source_port_start=rule_data.get('source_port_start'),
                source_port_end=rule_data.get('source_port_end'),
                destination_address_start=rule_data.get('destination_address_start'),
                destination_address_end=rule_data.get('destination_address_end'),
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
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Set ID
        id_item = QTableWidgetItem(str(row + 1))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, id_item)
        
        source_ip = (f"{rule.source_address_start}-{rule.source_address_end}" 
                    if rule.source_address_start != rule.source_address_end 
                    else rule.source_address_start)
        source_port = (f"{rule.source_port_start}-{rule.source_port_end}"
                      if rule.source_port_start != rule.source_port_end and rule.source_port_start is not None
                      else str(rule.source_port_start) if rule.source_port_start is not None else "")
        source = f"{source_ip}:{source_port}" if source_port else source_ip
        self.table.setItem(row, 1, QTableWidgetItem(source))
        
        dest_ip = (f"{rule.destination_address_start}-{rule.destination_address_end}"
                  if rule.destination_address_start != rule.destination_address_end
                  else rule.destination_address_start)
        dest_port = (f"{rule.destination_port_start}-{rule.destination_port_end}"
                    if rule.destination_port_start != rule.destination_port_end and rule.destination_port_start is not None
                    else str(rule.destination_port_start) if rule.destination_port_start is not None else "")
        dest = f"{dest_ip}:{dest_port}" if dest_port else dest_ip
        self.table.setItem(row, 2, QTableWidgetItem(dest))
        
        self.table.setItem(row, 3, QTableWidgetItem(rule.protocol.value))
        self.table.setItem(row, 4, QTableWidgetItem(rule.action.value))
        self.table.setItem(row, 5, QTableWidgetItem(rule.direction.value))
        
        enabled_item = QTableWidgetItem()
        enabled_item.setCheckState(Qt.CheckState.Checked if rule.enabled else Qt.CheckState.Unchecked)
        self.table.setItem(row, 6, enabled_item)
        
        self.table.setItem(row, 7, QTableWidgetItem(rule.description))

    def get_rule(self, row):
        source = self.table.item(row, 1).text()
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
        
        dest = self.table.item(row, 2).text()
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
            id=int(self.table.item(row, 0).text()),
            source_address_start=source_address_start,
            source_address_end=source_address_end,
            source_port_start=source_port_start,
            source_port_end=source_port_end,
            destination_address_start=dest_address_start,
            destination_address_end=dest_address_end,
            destination_port_start=dest_port_start,
            destination_port_end=dest_port_end,
            protocol=Protocol(self.table.item(row, 3).text()),
            action=Action(self.table.item(row, 4).text()),
            direction=Direction(self.table.item(row, 5).text()),
            enabled=self.table.item(row, 6).checkState() == Qt.CheckState.Checked,
            description=self.table.item(row, 7).text()
        )

    def get_all_rules(self):
        return [self.get_rule(row) for row in range(self.table.rowCount())]

    def update_rule(self, row, rule):
        id_item = QTableWidgetItem(str(row + 1))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, id_item)
        
        source_ip = (f"{rule.source_address_start}-{rule.source_address_end}"
                    if rule.source_address_start != rule.source_address_end
                    else rule.source_address_start)
        source_port = (f"{rule.source_port_start}-{rule.source_port_end}"
                      if rule.source_port_start != rule.source_port_end and rule.source_port_start is not None
                      else str(rule.source_port_start) if rule.source_port_start is not None else "")
        source = f"{source_ip}:{source_port}" if source_port else source_ip
        self.table.setItem(row, 1, QTableWidgetItem(source))
        
        dest_ip = (f"{rule.destination_address_start}-{rule.destination_address_end}"
                  if rule.destination_address_start != rule.destination_address_end
                  else rule.destination_address_start)
        dest_port = (f"{rule.destination_port_start}-{rule.destination_port_end}"
                    if rule.destination_port_start != rule.destination_port_end and rule.destination_port_start is not None
                    else str(rule.destination_port_start) if rule.destination_port_start is not None else "")
        dest = f"{dest_ip}:{dest_port}" if dest_port else dest_ip
        self.table.setItem(row, 2, QTableWidgetItem(dest))
        
        self.table.setItem(row, 3, QTableWidgetItem(rule.protocol.value))
        self.table.setItem(row, 4, QTableWidgetItem(rule.action.value))
        self.table.setItem(row, 5, QTableWidgetItem(rule.direction.value))
        enabled_item = QTableWidgetItem()
        enabled_item.setCheckState(Qt.CheckState.Checked if rule.enabled else Qt.CheckState.Unchecked)
        self.table.setItem(row, 6, enabled_item)
        self.table.setItem(row, 7, QTableWidgetItem(rule.description))
