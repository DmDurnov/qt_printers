import gdb.printing
import itertools
import sys

"""Qt6Core pretty printer for GDB."""

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    from helper_py3 import Iterator
    from helper_py3 import unichr
else:
    from helper_py2 import Iterator
    from helper_py2 import unichr

class QByteArrayPrinter:
    """Print a Qt6 QByteArray"""

    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.d_ptr = self.val['d']
        self.size = int(self.d_ptr['size'])

    class QByteArrayIterator(Iterator):
        def __init__(self, _data, _size : int):
            self.data = _data
            self.size = _size
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.index >= self.size:
                raise StopIteration
            index = self.index
            self.index = self.index + 1
            return ((f'[{index}]'), self.data[index])

    def _stringData(self):
        return self.d_ptr['ptr'].cast(gdb.lookup_type('char').pointer())

    def children(self):
        return self.QByteArrayIterator(self._stringData(), self.size)

    def num_children(self):
        return self.size

    def to_string(self):
        data = self._stringData()
        try:
            return data.string(length = self.size)
        except:
            return data.string(length = self.size, encoding = 'latin1')

    def display_hint(self):
        return "string"

class QCharPrinter:
    """Print a Qt6 QChar"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        return unichr(int(self.val['ucs']))

    def display_hint(self):
        return 'string'

class QLatin1StringPrinter:
    """Print a Qt6 QLatin1String"""

    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.bytes_per_char = 1
        self.encoding = 'latin1'

    def to_string(self):
        result = ''
        try:
            size = int(self.val['m_size'])
            if size == 0:
                return result
            data = self.val['m_data'].cast(gdb.lookup_type('char').pointer())
            size = size * self.bytes_per_char
            result = data.string(encoding = self.encoding, length = size)
        except Exception:
            pass
        return result

    def display_hint(self):
        return 'string'

class QStringViewPrinter:
    """Print a Qt6 QStringView"""

    def __init__(self, _val):
        self.val = _val
        self.bytes_per_char = 2
        self.encoding = 'utf-16'

    def to_string(self):
        result = ''
        try:
            size = int(self.val['m_size'])
            if size == 0:
                return result
            data = self.val['m_data'].cast(gdb.lookup_type('char').pointer())
            size = size * self.bytes_per_char
            result = data.string(encoding = self.encoding, length = size)
        except Exception:
            pass
        return result

    def display_hint(self):
        return 'string'

class QStringPrinter:
    """Print a Qt6 QString"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        result = ''
        try:
            d_ptr = self.val['d']
            size = int(self.val['d']['size'])
            if size == 0:
                return result
            data = d_ptr['ptr'].cast(gdb.lookup_type('char').pointer())
            result = data.string(encoding = 'utf-16', length = size * 2)
        except Exception:
            pass
        return result

    def num_children(self):
        return self.val['d']['size']

    def display_hint(self):
        return 'string'

class QUtf8StringViewPrinter:
    """Print a Qt6 QUtf8StringView"""

    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.bytes_per_char = 1
        self.encoding = 'utf-8'

    def to_string(self):
        result = ''
        try:
            d_ptr = self.val['d']
            size = int(self.val['d']['size'])
            if size == 0:
                return result
            data = d_ptr['ptr'].cast(gdb.lookup_type('char').pointer())
            result = data.string(encoding = 'utf-16', length = size * 2)
        except Exception:
            pass
        return result

    def display_hint(self):
        return 'string'

def build_pretty_printer():
    pp = gdb.printing.RegexpCollectionPrettyPrinter('Qt6Core')
    pp.add_printer('QByteArray', '^QByteArray$', QByteArrayPrinter)
    pp.add_printer('QChar', '^QChar$', QCharPrinter)
    pp.add_printer('QLatin1String', '^QLatin1String$', QLatin1StringPrinter)
    pp.add_printer('QString', '^QString$', QStringPrinter)
    pp.add_printer('QStringView', '^QStringView$', QStringViewPrinter)
    pp.add_printer('QUtf8StringView', '^QUtf8StringView$', QUtf8StringViewPrinter)
    return pp

printer = build_pretty_printer()
