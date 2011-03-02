# `django-castor`

`django-castor` is a re-usable app for Django which provides a
**content-addressable storage backend**. The main class,
`djcastor.storage.CAStorage`, is a type of `FileSystemStorage` which saves files
under their SHA-1 digest.

*   No matter how many times the same file is uploaded, it will only ever be
    stored once, thus eliminating redundancy.

*   Filenames are pseudorandom and made up only of hexadecimal characters, so
    you don’t have to worry about filename collisions or sanitization.

*   `django-castor` shards files in the uploads directory based on their
    digests; this prevents filesystem issues when too many files are in a single
    directory.

For more information on the CAS concept, see the [wikipedia page][].

  [wikipedia page]: http://en.wikipedia.org/wiki/Content-addressable_storage


## Installation

    pip install django-castor  # or
    easy_install django-castor


## Usage

Basic usage is as follows:

    from django.db import models
    from djcastor import CAStorage

    class MyModel(models.Model):
        ...
        uploaded_file = models.FileField(storage=CAStorage(),
                                         upload_to='uploads')

At the moment, Django requires a non-empty value for the `upload_to` parameter.
Note that `CAStorage` will **not** use this value; if you need to customize the
destination for uploaded files, use the `location` parameter (see below).

For extended usage, there are several options you can pass to the `CAStorage`
constructor. The first two are inherited from the built-in `FileSystemStorage`:

*   `location`: The absolute path to the directory that will hold uploaded
    files. If omitted, this will be set to the value of the `MEDIA_ROOT`
    setting.

*   `base_url`: The URL that serves the files stored at this location. If
    omitted, this will be set to the value of the `MEDIA_URL` setting.

`CAStorage` also adds two custom options:

*   `keep_extension` (default `True`): Preserve the extension on uploaded files.
    This allows the webserver to guess their `Content-Type`.

*   `sharding` (default `(2, 2)`): The width and depth to use when sharding
    digests, expressed as a two-tuple. The following examples show how these
    parameters affect the sharding:

        >>> digest = '1f09d30c707d53f3d16c530dd73d70a6ce7596a9'

        >>> print shard(digest, width=2, depth=2)
        1f/09/1f09d30c707d53f3d16c530dd73d70a6ce7596a9

        >>> print shard(digest, width=2, depth=3)
        1f/09/d3/1f09d30c707d53f3d16c530dd73d70a6ce7596a9

        >>> print shard(digest, width=3, depth=2)
        1f0/9d3/1f09d30c707d53f3d16c530dd73d70a6ce7596a9


## Caveats

The first small caveat is that content-addressable storage is not suited to
rapidly-changing content. If your website modifies the contents of file fields
on a regular basis, it might be a better idea to use a UUID-based storage
backend for those fields.

The second, more important caveat with this approach is that if the parent model
of a file is deleted, the file will remain on disk. Because individual files may
be referred to by more than one model, and `django-castor` has no awareness of
these references, it leaves file deletion up to the developer.

For the most part, you can get away without deleting uploads. In fact,
content-addressable storage is often used for long-term archival systems, where
files are immutable and must be kept for future auditing (usually for compliance
with government regulations).

If disk space is at a premium and you need to delete uploads, there are two
approaches you might want to take:

*   Garbage collection: write a script that walks through the list of uploaded
    files and checks references to each one. If no references are found, delete
    the file.

*   Reference counting: denormalize the `FileField` into a separate model, and
    keep a count of all the models pointing to it. Once this count reaches zero,
    delete the file from the filesystem.


## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
software, either in source code form or as a compiled binary, for any purpose,
commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
