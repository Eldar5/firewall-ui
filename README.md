# Firewall UI

This project implements a user interface for managing firewall rules on a Linux system. It allows users to add, edit, delete, and apply firewall rules through a graphical interface.

## Features

- Add, edit, and delete firewall rules
- Apply rules to the system's firewall
- View system logs
- User-friendly interface built with PyQt6

## Requirements

- Python 3.8+
- PyQt6
- python-iptables
- Linux system with iptables

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Eldar5/firewall-ui.git
   cd firewall-ui
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure you have the necessary permissions to modify firewall rules on your system.

2. Run the application:
   ```
   python src/main.py
   ```

3. Use the interface to add, edit, or delete firewall rules.

4. Click "Apply Rules" to send the rules to the kernel module.

5. View logs in the "Logs" tab.

## Development

### Project Structure

```
firewall-ui/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── rule_dialog.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       └── rule_table.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── rule.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── kernel_comm.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── logs/
├── tests/
│   └── __init__.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Running Tests

To run the unit tests:

```
python -m unittest discover tests
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - [your-email@example.com](mailto:your-email@example.com)

Project Link: [https://github.com/Eldar5/firewall-ui](https://github.com/Eldar5/firewall-ui)