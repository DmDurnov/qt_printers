import gdb
import os
import sys

class Qt5PrintersSetupCommand(gdb.Command):
    def __init__(self):
        super(Qt5PrintersSetupCommand, self).__init__("setup-qt5-printers", gdb.COMMAND_USER)

    def invoke(self, argument, from_tty):
        printers_path = os.path.expanduser(f"~/.config/gdb/qt_printers/qt5printers")
        
        if not os.path.exists(printers_path):
            print(f"Error: Printers directory not found at {printers_path}")
            return
        
        # Add printers directory to Python path
        if printers_path not in sys.path:
            sys.path.insert(0, printers_path)
        
        # Import and register printers
        try:
            from .qt5printers import register_qt5_printers
            register_qt5_printers(None)
            print("Qt5 printers successfully registered")
        except Exception as e:
            print(f"Error registering Qt5 printers: {str(e)}")

class Qt6PrintersSetupCommand(gdb.Command):
    def __init__(self):
        super(Qt6PrintersSetupCommand, self).__init__("setup-qt6-printers", gdb.COMMAND_USER)

    def invoke(self, argument, from_tty):
        printers_path = os.path.expanduser(f"~/.config/gdb/qt_printers/qt6printers")
        
        if not os.path.exists(printers_path):
            print(f"Error: Printers directory not found at {printers_path}")
            return
        
        # Add printers directory to Python path
        if printers_path not in sys.path:
            sys.path.insert(0, printers_path)
        
        # Import and register printers
        try:
            from .qt6printers import register_qt6_printers
            register_qt6_printers(None)
            print("Qt6 printers successfully registered")
        except Exception as e:
            print(f"Error registering Qt6 printers: {str(e)}")


def register_qt_setup_commands():
    # Register the command
    Qt5PrintersSetupCommand()
    Qt6PrintersSetupCommand()
