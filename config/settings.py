# Application settings

# Logging
LOG_FILE = "logs/firewall.log"
LOG_LEVEL = "DEBUG"

# Kernel communication
NETLINK_GROUP = 17  # Example group number, adjust as needed

# UI settings
WINDOW_TITLE = "Firewall Rules Manager"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Rule table columns
RULE_TABLE_COLUMNS = [
    "Source", "Destination", "Protocol", 
    "Action", "Direction", "Enabled", "Description"
]

# Default values
DEFAULT_PROTOCOL = "TCP"
DEFAULT_ACTION = "DROP"
DEFAULT_DIRECTION = "INBOUND"