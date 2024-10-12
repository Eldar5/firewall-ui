from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum
import ipaddress

class Protocol(Enum):
    TCP = "TCP"
    UDP = "UDP"

class Action(Enum):
    ACCEPT = "ACCEPT"
    DROP = "DROP"

class Direction(Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

@dataclass
class Rule:
    """
    Firewall rule data model.
    Using dataclass for automatic JSON serialization and validation.
    """
    id: int  # Unique identifier for the rule
    source_address: str
    source_port: Optional[int]
    destination_address: str
    destination_port: Optional[int]
    protocol: Protocol
    action: Action
    direction: Direction
    enabled: bool = True
    description: str = ""

    def validate(self):
        """Validate rule fields"""
        try:
            # Validate IP addresses
            ipaddress.ip_network(self.source_address)
            ipaddress.ip_network(self.destination_address)
            
            # Validate ports
            if self.source_port is not None:
                assert 0 <= self.source_port <= 65535
            if self.destination_port is not None:
                assert 0 <= self.destination_port <= 65535
                
            return True
        except Exception as e:
            raise ValueError(f"Invalid rule: {str(e)}")

    def to_dict(self):
        """Convert rule to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['protocol'] = self.protocol.value
        data['action'] = self.action.value
        data['direction'] = self.direction.value
        return data