# -*- coding: utf-8 -*-

import os

from django.core.exceptions import SuspiciousOperation
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str

from djcastor import utils


class CAStorage(FileSystemStorage):
    
    """
    A content-addressable storage backend for Django.
    
    Basic Usage
    -----------
    
        from django.db import models
        from djcastor import CAStorage
        
        class MyModel(models.Model):
            ...
            uploaded_file = models.FileField(storage=CAStorage())
    
    Extended Usage
    --------------
    
    There are several options you can pass to the `CAStorage` constructor. The
    first two are inherited from `django.core.files.storage.FileSystemStorage`:
    
    *   `location`: The absolute path to the directory that will hold uploaded
        files. If omitted, this will be set to the value of the `MEDIA_ROOT`
        setting.
    
    *   `base_url`: The URL that serves the files stored at this location. If
        omitted, this will be set to the value of the `MEDIA_URL` setting.
    
    `CAStorage` also adds two custom options:
    
    *   `keep_extension` (default `True`): Preserve the extension on uploaded
        files. This allows the webserver to guess their `Content-Type`.
    
    *   `sharding` (default `(2, 2)`): The width and depth to use when sharding
        digests, expressed as a two-tuple. `django-castor` shards files in the
        uploads directory based on their digests; this prevents filesystem
        issues when too many files are in a single directory. Sharding is based
        on two parameters: *width* and *depth*. The following examples show how
        these affect the sharding:
        
            >>> digest = '1f09d30c707d53f3d16c530dd73d70a6ce7596a9'
            
            >>> print shard(digest, width=2, depth=2)
            1f/09/1f09d30c707d53f3d16c530dd73d70a6ce7596a9
            
            >>> print shard(digest, width=2, depth=3)
            1f/09/d3/1f09d30c707d53f3d16c530dd73d70a6ce7596a9
            
            >>> print shard(digest, width=3, depth=2)
            1f0/9d3/1f09d30c707d53f3d16c530dd73d70a6ce7596a9
    
    """
    
    def __init__(self, location=None, base_url=None, keep_extension=True,
                 sharding=(2, 2)):
        super(CAStorage, self).__init__(location=location, base_url=base_url)
        
        self.shard_width, self.shard_depth = sharding
        self.keep_extension = keep_extension
    
    @staticmethod
    def get_available_name(name):
        """Return the name as-is; in CAS, given names are ignored anyway."""
        
        return name
    
    def digest(self, content):
        if hasattr(content, 'temporary_file_path'):
            return utils.hash_filename(content.temporary_file_path())
        digest = utils.hash_chunks(content.chunks())
        content.seek(0)
        return digest
    
    def shard(self, hexdigest):
        return list(utils.shard(hexdigest, self.shard_width, self.shard_depth,
                                rest_only=False))
    
    def path(self, hexdigest):
        shards = self.shard(hexdigest)
        
        try:
            path = safe_join(self.location, *shards)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." %
                                      ('/'.join(shards),))
        
        return smart_str(os.path.normpath(path))
    
    def url(self, name):
        return super(CAStorage, self).url('/'.join(self.shard(name)))
    
    def delete(self, name):
        # Ignore deletions; we don't know how many different records point to
        # one file.
        pass
    
    def _save(self, name, content):
        digest = self.digest(content)
        if self.keep_extension:
            digest += os.path.splitext(name)[1]
        path = self.path(digest)
        if os.path.exists(path):
            return digest
        return super(CAStorage, self)._save(digest, content)
