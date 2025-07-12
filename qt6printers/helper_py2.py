class Iterator(object):
    def next(self):
        return type(self).__next__(self)

unichr = unichr
