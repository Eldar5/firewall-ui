from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum
import ipaddress

class Protocol(Enum):
    TCP = "TCP"
    UDP = "UDP"
    ANY = "ANY"

class Action(Enum):
    ACCEPT = "ACCEPT"
    DROP = "DROP"

class Direction(Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

@dataclass
class Rule:
    """
    Firewall rule data model with support for IP and port ranges.
    """
    id: int
    source_address_start: str
    source_address_end: str
    source_port_start: Optional[int]
    source_port_end: Optional[int]
    destination_address_start: str
    destination_address_end: str
    destination_port_start: Optional[int]
    destination_port_end: Optional[int]
    protocol: Protocol
    action: Action
    direction: Direction
    enabled: bool = True
    description: str = ""

    def validate(self):
        """Validate rule fields including ranges"""
        try:
            # Validate IP address ranges
            src_start = ipaddress.ip_address(self.source_address_start)
            src_end = ipaddress.ip_address(self.source_address_end)
            dst_start = ipaddress.ip_address(self.destination_address_start)
            dst_end = ipaddress.ip_address(self.destination_address_end)
            
            # Ensure start IPs are less than or equal to end IPs
            if src_start > src_end:
                raise ValueError("Source IP start must be less than or equal to end")
            if dst_start > dst_end:
                raise ValueError("Destination IP start must be less than or equal to end")
            
            # Validate port ranges
            if self.source_port_start is not None and self.source_port_end is not None:
                if not (0 <= self.source_port_start <= 65535 and 0 <= self.source_port_end <= 65535):
                    raise ValueError("Port numbers must be between 0 and 65535")
                if self.source_port_start > self.source_port_end:
                    raise ValueError("Source port start must be less than or equal to end")
                    
            if self.destination_port_start is not None and self.destination_port_end is not None:
                if not (0 <= self.destination_port_start <= 65535 and 0 <= self.destination_port_end <= 65535):
                    raise ValueError("Port numbers must be between 0 and 65535")
                if self.destination_port_start > self.destination_port_end:
                    raise ValueError("Destination port start must be less than or equal to end")
                
            return True
        except Exception as e:
            raise ValueError(f"Invalid rule: {str(e)}")

    def to_dict(self):
        """Convert rule to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['protocol'] = self.protocol.value if isinstance(self.protocol, Enum) else self.protocol
        data['action'] = self.action.value if isinstance(self.action, Enum) else self.action
        data['direction'] = self.direction.value if isinstance(self.direction, Enum) else self.direction
        return data

    @staticmethod
    def from_single_values(
        id: int,
        source_address: str,
        source_port: Optional[int],
        destination_address: str,
        destination_port: Optional[int],
        protocol: Protocol,
        action: Action,
        direction: Direction,
        enabled: bool = True,
        description: str = ""
    ):
        """Create a Rule instance from single IP addresses and ports"""
        return Rule(
            id=id,
            source_address_start=source_address,
            source_address_end=source_address,
            source_port_start=source_port,
            source_port_end=source_port,
            destination_address_start=destination_address,
            destination_address_end=destination_address,
            destination_port_start=destination_port,
            destination_port_end=destination_port,
            protocol=protocol,
            action=action,
            direction=direction,
            enabled=enabled,
            description=description
        )