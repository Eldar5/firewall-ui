import socket
import os
import struct
import json
from firewall_ui.utils.logger import FirewallLogger

class KernelCommunicator:
   NETLINK_TEST_FAMILY = 25
   SOCKET_TIMEOUT = 3.5
   
   MSG_GET_CONFIG = b'\x02'
   MSG_SEND_CONFIG = b'\x01'
   MSG_SEND_SUCCESS = b'\x04'
   MSG_SEND_FAIL = b'\x05'

   def __init__(self):
       self.logger = FirewallLogger().get_logger()
       self.socket = None
       self.initialize_socket()

   def initialize_socket(self):
       try:
           self.socket = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, self.NETLINK_TEST_FAMILY)
           self.socket.bind((os.getpid(), 0))
           self.socket.settimeout(self.SOCKET_TIMEOUT)
           self.logger.info("Netlink socket initialized successfully")
           return True
       except Exception as e:
           self.logger.error(f"Failed to initialize netlink socket: {str(e)}")
           return False

   def create_message(self, payload, msg_type):
       msg_len = len(payload) + 1 + 16
       header = struct.pack("=LHHLL",
           msg_len,
           0,
           0,
           0,
           os.getpid()
       )
       return header + msg_type + payload

   def get_current_config(self):
       if not self.socket:
           self.logger.error("Socket not initialized")
           return None, "Socket not initialized"

       try:
           message = self.create_message(b'', self.MSG_GET_CONFIG)
           self.socket.send(message)
           self.logger.debug("Sent config request to kernel module")

           response = self.socket.recv(1024 * 1024)
           if len(response) > 17:
               config_data = response[17:].lstrip(b'\x00').rstrip(b'\x00')
               try:
                   config = json.loads(config_data.decode('utf-8'))
                   self.logger.info("Successfully received config from kernel module")
                   return config, None
               except json.JSONDecodeError as e:
                   self.logger.error(f"Failed to parse config JSON: {str(e)}")
                   return None, "Invalid config format"
           else:
               self.logger.error("Received response too short")
               return None, "Invalid response from kernel"

       except socket.timeout:
           self.logger.error(f"Timeout waiting for kernel response after {self.SOCKET_TIMEOUT} seconds")
           return None, "Communication timeout"
       except Exception as e:
           self.logger.error(f"Error getting config: {str(e)}")
           return None, str(e)

   # kernel_comm.py
   def validate_applied_config(self, sent_config):
      try:
          received_config, error = self.get_current_config()
          if error:
              return False, f"Failed to get config for validation: {error}"
   
          sent_dicts = [rule.to_dict() for rule in sent_config]
          
          if len(sent_dicts) != len(received_config):
              return False, f"Config size mismatch: sent {len(sent_dicts)}, received {len(received_config)}"
   
          for sent_rule, received_rule in zip(sent_dicts, received_config):
              for key in sent_rule:
                  if sent_rule[key] != received_rule.get(key):
                      return False, f"Rule mismatch for field {key}: sent {sent_rule[key]}, received {received_rule.get(key)}"
   
          return True, None
   
      except Exception as e:
          return False, f"Validation error: {str(e)}"
   
   def send_config(self, config):
      if not self.socket:
          self.logger.error("Socket not initialized")
          return False, "Socket not initialized", None
   
      try:
          config_dicts = [rule.to_dict() for rule in config]
          config_json = json.dumps(config_dicts).encode('utf-8')
          message = self.create_message(config_json, self.MSG_SEND_CONFIG)
          self.socket.send(message)
          self.logger.debug(f"Sent config to kernel module: {config_dicts}")
   
          response = self.socket.recv(1024)
          if len(response) >= 20:
              status = response[16:20]
              if status == b'\x04\x00\x00\x00':
                  is_valid, validation_error = self.validate_applied_config(config)
                  if is_valid:
                      self.logger.info("Config successfully applied and validated")
                      return True, None, None
                  else:
                      self.logger.warning(f"Config validation failed: {validation_error}")
                      return True, None, validation_error
              else:
                  self.logger.error("Config processing failed")
                  return False, "Kernel rejected configuration", None
   
      except socket.timeout:
          self.logger.error(f"Timeout waiting for kernel response after {self.SOCKET_TIMEOUT} seconds")
          return False, "Communication timeout", None
      except Exception as e:
          self.logger.error(f"Error sending config: {str(e)}")
          return False, str(e), None