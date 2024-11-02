import socket
import struct
import json
import logging
from utils.logger import FirewallLogger
from pathlib import Path

class KernelCommunicator:
    RULE_REQUEST_CMD = 1  # Command code for requesting rules
    RULE_SEND_CMD = 2    # Command code for sending rules

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Create netlink socket
        self.sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_USERSOCK)
        self.sock.bind((0, 0))  # Bind to auto-assigned PID
        
    def get_current_rules(self):
        """
        Request and retrieve current firewall rules from kernel module.
        Returns:
            list: List of rule dictionaries if successful, None otherwise
        """
        try:
            # Prepare rule request message
            request_cmd = struct.pack("=IHHII", 16, self.RULE_REQUEST_CMD, 0, 0, 0)
            self.sock.send(request_cmd)
            self.logger.info("Sent rule request to kernel module")
            
            # Receive response
            response = self.receive_response()
            if not response:
                self.logger.info("No rules found in kernel module")
                return None
                
            try:
                rules = json.loads(response)
                self.logger.info(f"Successfully retrieved {len(rules)} rules from kernel")
                return rules
            except json.JSONDecodeError:
                self.logger.error("Failed to parse rules response as JSON")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get rules from kernel: {str(e)}")
            return None

    def send_rules(self, rules):
        """
        Send rules to kernel module using netlink socket.
        Rules are sent in JSON format for easy parsing in kernel space.
        """
        try:
            # Print the rules to the console
            print("Rules to send:", [rule.to_dict() for rule in rules])  # Print as dictionaries for clarity
            # Convert Rule objects to dictionaries
            rules_dicts = [rule.to_dict() for rule in rules]  # Convert each Rule instance to dict
            # Convert rules to JSON format
            rules_json = json.dumps(rules_dicts)  # Now this will work since rules_dicts is a list of dicts
            # Add necessary netlink headers
            message = struct.pack("=IHHII", len(rules_json) + 16, self.RULE_SEND_CMD, 0, 0, 0)
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