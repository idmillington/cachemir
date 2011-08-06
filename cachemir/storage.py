import os.path
import tempfile

# NB: cStringIO is faster but doesn't support unicode.
from StringIO import StringIO

class CacheStorage(object):
    """
    Subclasses of this are pluggable storage systems to allow cached
    data to be retained in a variety of media.
    """
    def has(self, data_hash):
        """
        Returns true if this storage has the given data hash string.
        """
        return False

    def get(self, data_hash):
        """
        Returns a file-like object for reading data associated with
        the given data hash string. Throws a KeyError if the hash
        isn't found.
        """
        pass

    def out(self, data_hash):
        """
        Returns a file-like object for writing data associated with
        the given data hash.
        """
        pass

class CacheLocalStorage(CacheStorage):
    """
    Implements a naive local dictionary based storage for data. This
    is highly sensitive to running out of memory, so is best used for
    smaller pieces of content.
    """
    def __init__(self, BufferClass=StringIO):
        self._data = {}
        self._BufferClass

    def has(self, data_hash):
        return data_hash in self._data

    def get(self, data_hash):
        return self._BufferClass(self._data[data_hash])

    def out(self, data_hash):
        # Create a new StringIO that tracks when it is closed and
        # only then stores the data.
        that = self
        class LocalCacheStringIO(self._BufferClass):
            def close(self, *args, **kws):
                # Store first, as closing destroys the buffer.
                that._data[data_hash] = self.getvalue()
                # Close as normal.
                super(LocalCacheStringIO, self).close(*args, **kws)
        return LocalCacheStringIO()

class CacheFileStorage(CacheStorage):
    """
    Stores the cached data in a directory on the hard-drive.
    """
    def __init__(self, directory=None):
        if directory is None:
            # Make a temporary directory.
            directory = tempfile.mkdtemp()
        self._directory = directory

    def get_path(self, data_hash):
        """
        Figures out where to store the cached data. Override this to
        change the way filenames are calculated.
        """
        return os.path.join(self._directory, data_hash[:2], data_hash)

    def has(self, data_hash):
        return os.path.exists(self.get_path(data_hash))

    def get(self, data_hash):
        try:
            return file(self.get_path(data_hash), 'rb')
        except IOError:
            return KeyError(data_hash)

    def out(self, data_hash):
        fn = self.get_path(data_hash)
        diry = os.path.dirname(fn)
        if not os.path.exists(diry):
            os.makedirs(diry)
        return file(fn, 'wb')

