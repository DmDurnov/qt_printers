import gdb.printing
from . import core

def register_qt6_printers(obj):
    """Registers all known Qt6 pretty-printers."""
    gdb.printing.register_pretty_printer(obj, core.printer)
