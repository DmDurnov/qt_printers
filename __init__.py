import gdb
import os
import sys

class QtPrintersSetupCommand(gdb.Command):
    def __init__(self):
        super(QtPrintersSetupCommand, self).__init__("setup-qt-printers", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) != 1 or args[0] not in ['5', '6']:
            print("Usage: setup-qt-printers 5|6")
            return
        
        version = args[0]
        printers_path = os.path.expanduser(f"~/.config/gdb/qt_printers/qt{version}printers")
        
        if not os.path.exists(printers_path):
            print(f"Error: Printers directory not found at {printers_path}")
            return
        
        # Add printers directory to Python path
        if printers_path not in sys.path:
            sys.path.insert(0, printers_path)
        
        # Import and register printers
        try:
            if version == '5':
                from .qt5printers import register_qt5_printers
                register_qt5_printers(None)
                print("Qt5 printers successfully registered")
            # elif version == '6':
                # from .qt6printers import register_qt6_printers
                # register_qt6_printers(None)
                # print("Qt6 printers successfully registered")
        except Exception as e:
            print(f"Error registering Qt{version} printers: {str(e)}")


def register_qt_setup_commands():
    # Register the command
    QtPrintersSetupCommand()
