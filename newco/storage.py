import os
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage
from django.core.files.base import File


class ForgivingFile(File):

    def _get_size(self):
        if not hasattr(self, '_size'):
            if hasattr(self.file, 'size'):
                self._size = self.file.size
            elif hasattr(self.file, 'name') and os.path.exists(self.file.name):
                self._size = os.path.getsize(self.file.name)
            elif hasattr(self.file, 'tell') and hasattr(self.file, 'seek'):
                pos = self.file.tell()
                self.file.seek(0, os.SEEK_END)
                self._size = self.file.tell()
                self.file.seek(pos)
            else:
                raise AttributeError("Unable to determine the file's size.")
        return self._size

    def _set_size(self, size):
        self._size = size

    size = property(_get_size, _set_size)

    def chunks(self, chunk_size=None):
        """
        Read the file and yield chucks of ``chunk_size`` bytes (defaults to
        ``UploadedFile.DEFAULT_CHUNK_SIZE``).
        """
        if not chunk_size:
            chunk_size = self.DEFAULT_CHUNK_SIZE

        if hasattr(self, 'seek'):
            self.seek(0)

        while True:
            data = self.read(chunk_size)
            if not data:
                break
            yield data


class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        content = ForgivingFile(content)
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
