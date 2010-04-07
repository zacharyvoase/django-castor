# -*- coding: utf-8 -*-

import hashlib

from django.core.files import File
from django.core.files.uploadedfile import UploadedFile


def hash_filename(filename, digestmod=hashlib.sha1,
                  chunk_size=UploadedFile.DEFAULT_CHUNK_SIZE):
    
    """
    Return the hash of the contents of a filename, using chunks.
    
        >>> import os.path as p
        >>> filename = p.join(p.abspath(p.dirname(__file__)), 'models.py')
        >>> hash_filename(filename)
        'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    
    """
    
    fileobj = File(open(filename))
    try:
        return hash_chunks(fileobj.chunks(chunk_size=chunk_size))
    finally:
        fileobj.close()


def hash_chunks(iterator, digestmod=hashlib.sha1):
    
    """
    Hash the contents of a string-yielding iterator.
    
        >>> import hashlib
        >>> digest = hashlib.sha1('abc').hexdigest()
        >>> strings = iter(['a', 'b', 'c'])
        >>> hash_chunks(strings, digestmod=hashlib.sha1) == digest
        True
    
    """
    
    digest = digestmod()
    for chunk in iterator:
        digest.update(chunk)
    return digest.hexdigest()


def shard(string, width, depth, rest_only=False):
    
    """
    Shard the given string by a width and depth. Returns a generator.
    
    A width and depth of 2 indicates that there should be 2 shards of length 2.
        
        >>> digest = '1f09d30c707d53f3d16c530dd73d70a6ce7596a9'
        >>> list(shard(digest, 2, 2))
        ['1f', '09', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
    
    A width of 5 and depth of 1 will result in only one shard of length 5.
    
        >>> list(shard(digest, 5, 1))
        ['1f09d', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
    
    A width of 1 and depth of 5 will give 5 shards of length 1.
    
        >>> list(shard(digest, 1, 5))
        ['1', 'f', '0', '9', 'd', '1f09d30c707d53f3d16c530dd73d70a6ce7596a9']
    
    If the `rest_only` parameter is true, only the remainder of the sharded
    string will be used as the last element:
    
        >>> list(shard(digest, 2, 2, rest_only=True))
        ['1f', '09', 'd30c707d53f3d16c530dd73d70a6ce7596a9']
    
    """
    
    for i in xrange(depth):
        yield string[(width * i):(width * (i + 1))]
    
    if rest_only:
        yield string[(width * depth):]
    else:
        yield string
