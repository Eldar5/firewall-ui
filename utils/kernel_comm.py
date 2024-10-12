import socket
import struct
import json
import logging
from pathlib import Path

class KernelCommunicator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Create netlink socket
        self.sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_USERSOCK)
        self.sock.bind((0, 0))  # Bind to auto-assigned PID
        
    def send_rules(self, rules):
        """
        Send rules to kernel module using netlink socket.
        Rules are sent in JSON format for easy parsing in kernel space.
        """
        try:
            # Convert rules to JSON format
            rules_json = json.dumps(rules)
            # Add necessary netlink headers
            message = struct.pack("=IHHII", len(rules_json) + 16, 0, 0, 0, 0)
            message += rules_json.encode()
            
            self.sock.send(message)
            self.logger.info(f"Rules sent to kernel module: {rules_json}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send rules to kernel: {str(e)}")
            return False
    
    def receive_response(self):
        """
        Receive response from kernel module
        """
        try:
            data = self.sock.recv(8192)
            # Skip netlink header
            response = data[16:].decode('utf-8')
            self.logger.info(f"Received response from kernel: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to receive kernel response: {str(e)}")
            return None

    def __del__(self):
        self.sock.close()