import gdb.printing
import itertools
import sys
from enum import Enum
from datetime import datetime

"""Qt6Core pretty printer for GDB."""

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    from helper_py3 import Iterator
    from helper_py3 import unichr
else:
    from helper_py2 import Iterator
    from helper_py2 import unichr

def has_field(val, name):
    """Check whether @p val (gdb.Value) has a field named @p name"""
    try:
        val[name]
        return True
    except Exception:
        return False

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
        return 'string'

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

class QListPrinter:
    """Print a Qt6 QList"""
    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.d_ptr = self.val['d']
        self.size = int(self.d_ptr['size'])
        self.template_type = self.val.type.template_argument(0)

    class QListIterator(Iterator):
        def __init__(self, _nodetype : gdb.Type, _d_ptr : gdb.Value):
            self.nodetype = _nodetype
            self.d_ptr = _d_ptr
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            size = int(self.d_ptr['size'])

            if self.index >= size:
                raise StopIteration
            index = self.index
            value = self.d_ptr['ptr'] + index
            self.index = self.index + 1
            return ((f'[{index}]'), value.cast(self.nodetype.pointer()).dereference())

    def children(self):
        return self.QListIterator(self.template_type, self.d_ptr)

    def num_children(self):
        return self.size

    def to_string(self):
        if self.size == 0:
            return f'QList<{self.template_type}> is empty'
        return f'QList<{self.template_type}> with size = {self.size}'

class QStringListPrinter(QListPrinter):
    """Print a Qt6 QStringList"""
    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def to_string(self):
        if self.size == 0:
            return 'QStringList is empty'
        return f'QStringList with size = {self.size}'

class QQueuePrinter(QListPrinter):
    """Print a Qt6 QQueue"""
    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def to_string(self):
        if self.size == 0:
            return f'QQueue<{self.template_type}> is empty'
        return f'QQueue<{self.template_type}> with size = {self.size}'

class QVectorPrinter(QListPrinter):
    """Print a Qt6 QVector"""
    """QVector is alias for QList"""
    
    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def to_string(self):
        if self.size == 0:
            return f'QVector<{self.template_type}> is empty'
        return f'QVector<{self.template_type}> with size = {self.size}'

class QStackPrinter(QListPrinter):
    """Print a Qt6 QStack"""
    
    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def to_string(self):
        if self.size == 0:
            return f'QStack<{self.template_type}> is empty'
        return f'QStack<{self.template_type}> with size = {self.size}'

class QMapPrinter:
    """Print a Qt6 QMap"""

    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.qt6StdMapPrinter = None
        if has_field(self.val['d']['d'], 'ptr'):
            ptr = self.val['d']['d']['ptr']
            self.qt6StdMapPrinter = gdb.default_visualizer(ptr['m'])
        else:
            ptr = self.val['d']['d']
            self.qt6StdMapPrinter = gdb.default_visualizer(ptr['m'])

    def children(self):
        if self.qt6StdMapPrinter != None:
            if hasattr(self.qt6StdMapPrinter, 'children'):
                return self.qt6StdMapPrinter.children() # type: ignore
            return []
        else:
            return []

    def to_string(self):
        num_children = self.num_children()
        if num_children is None:
            return f'QMap<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = ?'
        return f'QMap<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = {int(num_children)}'

    def num_children(self):
        if self.qt6StdMapPrinter:
            if hasattr(self.qt6StdMapPrinter, 'num_children'):
                return self.qt6StdMapPrinter.num_children() #type: ignore

        return None

    def display_hint(self):
        return None

class QMultiMapPrinter(QMapPrinter):
    """Print a Qt6 QMultiMap"""

    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def to_string(self):
        num_children = self.num_children()
        if num_children is None:
            return f'QMultiMap<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = ?'
        return f'QMultiMap<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = {int(num_children)}'

class QHashPrinter:
    """Print a Qt6 QHash"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    class QHashIterator(Iterator):
        """
        Representation Invariants:
            - self.currentNode is valid if self.d is not 0
            - self.chain is valid if self.currentNode is valid and self.isMulti is True
        """
        def __init__(self, _val : gdb.Value, _isMultiMap : bool):
            self.val = _val
            self.d_ptr = self.val['d']
            self.bucket = 0
            self.count = 0
            self.isMulti = _isMultiMap

            keyType = self.val.type.template_argument(0)
            valueType = self.val.type.template_argument(1)
            nodeStruct = 'MultiNode' if self.isMulti else 'Node'
            self.nodeType = f'QHashPrivate::{nodeStruct}<{keyType}, {valueType}>'

            self.firstNode()

        def __iter__(self):
            return self

        def span(self):
            "Python port of iterator::span()"
            return self.bucket >> 7 # SpanConstants::SpanShift

        def index(self):
            "Python port of iterator::index()"
            return self.bucket & 127 # SpanConstants::LocalBucketMask

        def isUnused (self):
            "Python port of iterator::isUnused()"
            # return !d->spans[span()].hasNode(index());
            # where hasNode is return (offsets[i] != SpanConstants::UnusedEntry);
            return self.d_ptr['spans'][self.span()]['offsets'][self.index()] == 0xff # SpanConstants::UnusedEntry

        def computeCurrentNode (self):
            "Return the node pointed by the iterator, python port of iterator::node()"
            # return &d->spans[span()].at(index());
            span_index = self.span()
            span = self.d_ptr['spans'][span_index]
            # where at() is return entries[offsets[i]].node();
            offset = span['offsets'][self.index()]

            if offset == 0xff: # UnusedEntry, can't happen
                print("Offset points to an unused entry.")
                return None

            entry = span['entries'][int(offset)]

            # where node() is return *reinterpret_cast<Node *>(&storage);
            # where Node is QHashPrivate::(Multi|)Node<Key, T>
            storage_pointer = entry['storage'].address
            return storage_pointer.cast(gdb.lookup_type(self.nodeType).pointer())

        def updateCurrentNode (self):
            "Compute the current node and update the QMultiHash chain"
            self.currentNode = self.computeCurrentNode()
            if self.isMulti:
                # Python port of any of the following two lines in QMultiHash::iterator:
                # e = &it.node()->value;
                # e = i.atEnd() ? nullptr : &i.node()->value;
                # Note that self.currentNode must be valid (not at end) here.
                assert(self.currentNode)
                self.chain = self.currentNode['value']

        def firstNode (self):
            "Go the first node, See Data::begin()."
            self.bucket = 0
            if self.isUnused():
                self.nextNode() # calls self.updateCurrentNode() if not empty
            else:
                self.updateCurrentNode()

        def nextNode (self):
            "Go to the next node, see iterator::operator++()."
            numBuckets = self.d_ptr['numBuckets']
            while True:
                self.bucket += 1
                if self.bucket == numBuckets:
                    self.d_ptr = gdb.Value(0)
                    self.bucket = 0
                    return
                if not self.isUnused():
                    self.updateCurrentNode()
                    return

        def __next__(self):
            "GDB iteration, first call returns key, second value and then jumps to the next chain or hash node."
            if not self.d_ptr:
                raise StopIteration

            index = self.count
            self.count = self.count + 1
            item = None
            if not self.isMulti:
                item = self.currentNode
                self.nextNode()
            else:
                item = self.chain
                self.chain = self.chain['next']
                if not self.chain:
                    self.nextNode()

            assert(item)
            result = (f'[{index}]', item.dereference())
            return result

    def children(self):
        d = self.val['d']
        if not d:
            return []
        return self.QHashIterator(self.val, False)

    def num_children(self):
        size = 0
        if has_field(self.val, 'm_size'):
            size = self.val['m_size']
        else:
            d = self.val['d']
            size = d['size'] if d else 0
        return int(size)

    def to_string(self):
        return f'QHash<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = {self.num_children()}'

    def display_hint(self):
        return None

class QMultiHash(QHashPrinter):
    """Print a Qt6 QMultiHash"""
    def __init__(self, _val : gdb.Value):
        super().__init__(_val)

    def children(self):
        d = self.val['d']
        if not d:
            return []
        return self.QHashIterator(self.val, True)

    def to_string(self):
        return f'QMultiHash<{self.val.type.template_argument(0)}, {self.val.type.template_argument(1)}> with size = {self.num_children()}'

class QSetPrinter:
    """Print a Qt6 QSet"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    class QSetIterator(Iterator):
        def __init__(self, _hashIterator):
            self.hash_iterator = _hashIterator
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if not self.hash_iterator.d_ptr:
                raise StopIteration

            item = self.hash_iterator.currentNode['key']
            self.hash_iterator.nextNode()

            index = self.index
            self.index = self.index + 1
            return (f'[{index}]', item)

    def children(self):
        qhash = self.val['q_hash']
        d = qhash['d']
        if not d:
            return []

        hashPrinter = QHashPrinter(qhash)
        hashIterator = hashPrinter.children()
        return self.QSetIterator(hashIterator)

    def num_children(self):
        d = self.val['q_hash']['d']
        return d['size'] if d else 0

    def to_string(self):
        return f'QSet<{self.val.type.template_argument(0)}> with size = {self.num_children()}'

class QVariantPrinter:
    """Print a Qt6 QVariant"""

    def __init__(self, _val : gdb.Value):
        self.val = _val
        self.d_ptr = self.val['d']
        self.is_null = self.d_ptr['is_null']

    def to_string(self):
        if self.is_null:
            return 'QVariant(empty)'

        data_type = self.d_ptr['packedType'] << 2
        metatype_interface = data_type.cast(gdb.lookup_type('QtPrivate::QMetaTypeInterface').pointer())
        type_str = ''
        try:
            typeAsCharPointer = metatype_interface['name']
            if typeAsCharPointer:
                type_str = typeAsCharPointer.string(encoding = 'utf-8')
        except Exception:
            pass

        data = self.d_ptr['data']
        is_shared = self.d_ptr['is_shared']
        value_str = None
        if is_shared:
            private_shared = data['shared'].dereference()
            private_shared_hex = hex(private_shared['data'])
            value_str = f'PrivateShared({private_shared_hex})'
        else:
            if type_str.endswith('*'):
                value_ptr = data['data'].reinterpret_cast(gdb.lookup_type('void').pointer().pointer())
                value_str = str(value_ptr.dereference())
            else:
                type_obj = None
                try:
                    type_obj = gdb.lookup_type(type_str)
                except Exception:
                    value_str = str(data['data'])

                if type_obj:
                    value_ptr = data['data'].reinterpret_cast(type_obj.pointer())
                    value_str = str(value_ptr.dereference())

        return f'QVariant(type = "{type_str}", value = {value_str})'

class QDatePrinter:
    """Print a Qt6 QDate"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        julianDay = self.val['jd']

        if julianDay == 0:
            return "invalid QDate"

        # Copied from Qt sources
        if julianDay >= 2299161:
            # Gregorian calendar starting from October 15, 1582
            # This algorithm is from Henry F. Fliegel and Thomas C. Van Flandern
            ell = julianDay + 68569;
            n = (4 * ell) / 146097;
            ell = ell - (146097 * n + 3) / 4;
            i = (4000 * (ell + 1)) / 1461001;
            ell = ell - (1461 * i) / 4 + 31;
            j = (80 * ell) / 2447;
            d = ell - (2447 * j) / 80;
            ell = j / 11;
            m = j + 2 - (12 * ell);
            y = 100 * (n - 49) + i + ell;
        else:
            # Julian calendar until October 4, 1582
            # Algorithm from Frequently Asked Questions about Calendars by Claus Toendering
            julianDay += 32082;
            dd = (4 * julianDay + 3) / 1461;
            ee = julianDay - (1461 * dd) / 4;
            mm = ((5 * ee) + 2) / 153;
            d = ee - (153 * mm + 2) / 5 + 1;
            m = mm + 3 - 12 * (mm / 10);
            y = int(dd - 4800 + (mm / 10));
            if y <= 0:
                y = y - 1;
        return "%d-%02d-%02d" % (y, m, d)

class QTimePrinter:
    """Print a Qt6 QTime"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        ds = self.val['mds']

        if ds == -1:
            return "invalid QTime"

        MSECS_PER_HOUR = 3600000
        SECS_PER_MIN = 60
        MSECS_PER_MIN = 60000

        hour = ds / MSECS_PER_HOUR
        minute = (ds % MSECS_PER_HOUR) / MSECS_PER_MIN
        second = (ds / 1000)%SECS_PER_MIN
        msec = ds % 1000
        return "%02d:%02d:%02d.%03d" % (hour, minute, second, msec)


class TimeSpec(Enum): # enum Qt::TimeSpec
    LocalTime = 0
    UTC = 1
    OffsetFromUTC = 2
    TimeZone = 3

def timeZoneId(spec, offsetFromUtc):
    if spec == TimeSpec.LocalTime.value:
        return 'Local'
    if spec == TimeSpec.UTC.value:
        return 'UTC'
    if spec == TimeSpec.OffsetFromUTC.value:
        offsetFromUtc = int(offsetFromUtc)
        sign = '-' if offsetFromUtc < 0 else '+'
        hours = abs(offsetFromUtc) // 3600
        minutes = (abs(offsetFromUtc) % 3600) // 60
        return f"UTC{sign}{hours:02}:{minutes:02}"
    # ShortData(Qt::TimeZone) has mode == 0, in which case Data is *not* short (and Data::d is nullptr).
    # But QDateTimePrinter.to_string() may perhaps pass TimeSpec.TimeZone as the spec in an invalid case.
    if spec == TimeSpec.TimeZone.value:
        return QTimeZonePrinter.INVALID
    return f'<error: unhandled time spec {spec}>'

class QTimeZonePrinter:
    """Print a Qt6 QTimeZone"""
    INVALID = "<invalid>"

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        d = self.val['d'] # QTimeZone::Data
        isShort = d.cast(gdb.lookup_type('long long')) & 3 # QTimeZone::Data::isShort (Qt6-only)
        if isShort:
            mode = d['s']['mode']
            spec = (mode + 3) & 3 # QTimeZone::ShortData::spec()
            offsetFromUtc = d['s']['offset']
            return timeZoneId(spec, offsetFromUtc)
        else:
            # QTimeZonePrivate contains:
            # - QSharedData (int) (plus 4 bytes of padding in case of a 64-bit architecture)
            # - vtable for QTimeZonePrivate
            # - QByteArray m_id
            qByteArrayPointerType = gdb.lookup_type('QByteArray').pointer()
            address = d.cast(qByteArrayPointerType.pointer()) # address of QTimeZonePrivate as QByteArray**
            if address == 0:
                # QTimeZone::isValid(), if not short, returns d.d && d->isValid()
                return QTimeZonePrinter.INVALID
            address += 2 # skip the first two hidden, pointer-sized data members

            tzId = QByteArrayPrinter(address.cast(qByteArrayPointerType).dereference()).to_string()
            # QTimeZonePrivate::isValid() returns !m_id.isEmpty()
            return tzId if tzId else QTimeZonePrinter.INVALID

def extractTimeSpec(_status):
    return (_status & QDateTimePrinter.TimeSpecMask) >> QDateTimePrinter.TimeSpecShift

class QDateTimePrinter:
    """Print a Qt6 QDateTime"""

    TimeSpecShift = 4
    TimeSpecMask  = 0x30

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        d = self.val['d'] # QDateTime::Data
        isShort = d.cast(gdb.lookup_type('long long')) & 1 # QDateTime::Data::isShort
        if isShort:
            msecs = d['data']['msecs']
            status = d['data']['status']
            offsetFromUtc = 0

            spec = extractTimeSpec(status)

            timeZone = timeZoneId(spec, offsetFromUtc)
        else:
            # QDateTimePrivate contains:
            # - QSharedData (int)
            # - (int) StatusFlags m_status
            # - qint64 m_msecs
            # - int m_offsetFromUtc (plus 4 bytes of padding in case of a 64-bit architecture)
            # - QTimeZone m_timeZone
            intType = gdb.lookup_type('int')
            intPointerType = intType.pointer()
            address = d.cast(intPointerType) # address of QDateTimePrivate as int*
            address += 1 # skip QSharedData
            status = address.dereference()
            address += 1 # skip m_status

            int64Type = gdb.lookup_type('long long')
            msecs = address.cast(int64Type.pointer()).dereference()
            address += int64Type.sizeof // intType.sizeof # skip m_msecs
            offsetFromUtc = address.dereference()

            spec = extractTimeSpec(status)

            if spec == TimeSpec.TimeZone.value:
                address += intPointerType.sizeof // intType.sizeof
                # skip m_offsetFromUtc and possible padding assuming that QTimeZone is pointer-aligned
                # print m_timeZone
                timeZone = QTimeZonePrinter(address.cast(gdb.lookup_type('QTimeZone').pointer()).dereference()).to_string()
            else:
                timeZone = timeZoneId(spec, offsetFromUtc)

        return datetime.utcfromtimestamp(int(msecs) / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' ' + timeZone


class QPersistentModelIndexPrinter:
    """Print a Qt6 QPersistentModelIndex"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        modelIndex = gdb.parse_and_eval(f"reinterpret_cast<const QPersistentModelIndex*>({self.val.address})->operator QModelIndex()")
        return str(modelIndex)

class QUrlPrinter:
    """Print a Qt6 QUrl"""

    def __init__(self, _val : gdb.Value):
        self.val = _val

    def to_string(self):
        try:
            int_type = gdb.lookup_type('int')
            string_type = gdb.lookup_type('QString')
            string_pointer = string_type.pointer()

            addr = self.val['d'].cast(gdb.lookup_type('char').pointer())
            if not addr:
                return '<invalid>'

            # skip QAtomicInt ref
            addr += int_type.sizeof
            # handle int port
            port = addr.cast(int_type.pointer()).dereference()
            addr += int_type.sizeof
            # handle QString scheme
            scheme = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()
            addr += string_type.sizeof
            # handle QString username
            username = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()
            addr += string_type.sizeof
            # skip QString password
            addr += string_type.sizeof
            # handle QString host
            host = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()
            addr += string_type.sizeof
            # handle QString path
            path = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()
            addr += string_type.sizeof
            # handle QString query
            query = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()
            addr += string_type.sizeof
            # handle QString fragment
            fragment = QStringPrinter(addr.cast(string_pointer).dereference()).to_string()

            url = ''
            if len(scheme) > 0:
                # TODO: always adding // is apparently not compliant in all cases
                url += scheme + '://'
            if len(host) > 0:
                if len(username) > 0:
                    url += username + '@'
                url += host
                if port != -1:
                    url += ':' + str(port)
            url += path
            if len(query) > 0:
                url += '?' + query
            if len(fragment) > 0:
                url += '#' + fragment

            return url
        except:
            pass
        # then try to print directly, but that might lead to issues (see http://sourceware-org.1504.n7.nabble.com/help-Calling-malloc-from-a-Python-pretty-printer-td284031.html)
        try:
            res = gdb.parse_and_eval(f'reinterpret_cast<const QUrl*>({self.val.address})->toString((QUrl::FormattingOptions)QUrl::PrettyDecoded)')
            return str(res)
        except:
            pass

        return '<uninitialized>'


def build_pretty_printer():
    pp = gdb.printing.RegexpCollectionPrettyPrinter('Qt6Core')
    pp.add_printer('QByteArray', '^QByteArray$', QByteArrayPrinter)
    pp.add_printer('QChar', '^QChar$', QCharPrinter)
    pp.add_printer('QDate', '^QDate$', QDatePrinter)
    pp.add_printer('QDateTime', '^QDateTime$', QDateTimePrinter)
    pp.add_printer('QHash', '^QHash<.*>$', QHashPrinter)
    pp.add_printer('QLatin1String', '^QLatin1String$', QLatin1StringPrinter)
    pp.add_printer('QList', '^QList<.*>$', QListPrinter)
    pp.add_printer('QMap', '^QMap<.*>$', QMapPrinter)
    pp.add_printer('QMultiHash', '^QMultiHash<.*>$', QHashPrinter)
    pp.add_printer('QMultiMap', '^QMultiMap<.*>$', QMultiMapPrinter)
    pp.add_printer('QPersistentModelIndex', '^QPersistentModelIndex$', QPersistentModelIndexPrinter)
    pp.add_printer('QQueue', '^QQueue<.*>$', QQueuePrinter)
    pp.add_printer('QSet', '^QSet<.*>$', QSetPrinter)
    pp.add_printer('QStack', '^QStack<.*>$', QStackPrinter)
    pp.add_printer('QString', '^QString$', QStringPrinter)
    pp.add_printer('QStringList', '^QStringList<.*>$', QStringListPrinter)
    pp.add_printer('QStringView', '^QStringView$', QStringViewPrinter)
    pp.add_printer('QTime', '^QTime$', QTimePrinter)
    pp.add_printer('QTimeZone', '^QTimeZone$', QTimeZonePrinter)
    pp.add_printer('QUrl', '^QUrl$', QUrlPrinter)
    pp.add_printer('QUtf8StringView', '^QUtf8StringView$', QUtf8StringViewPrinter)
    pp.add_printer('QVariant', '^QVariant$', QVariantPrinter)
    pp.add_printer('QVector', '^QVector<.*>$', QVectorPrinter)
    return pp

printer = build_pretty_printer()
