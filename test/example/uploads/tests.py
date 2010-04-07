# -*- coding: utf-8 -*-

from StringIO import StringIO
import hashlib
import os
import shutil

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.conf import settings
from django.test import TestCase

from uploads.models import Upload


class ReadTest(TestCase):
    
    fixtures = ['testing']
    
    def test(self):
        upload = Upload.objects.get(pk=1)
        self.assertEqual(upload.file.read(), "Hello, World!\n")


class MemoryWriteTest(TestCase):
    
    def test(self):
        text = "Spam Spam Spam.\n"
        digest = hashlib.sha1(text).hexdigest()
        io = StringIO(text)
        
        new_upload = Upload(file=InMemoryUploadedFile(
            io, 'file', 'spam.txt', 'text/plain', len(text), 'utf-8'))
        new_upload.save()
        
        # Upload has been saved to the database.
        self.assert_(new_upload.pk)
        
        # Upload contains correct content.
        self.assertEqual(new_upload.file.read(), text)
        
        # Filename is the hash of the file contents.
        self.assert_(new_upload.file.name.startswith(digest))
    
    def tearDown(self):
        # Remove the upload in `MEDIA_ROOT`.
        directory = os.path.join(settings.MEDIA_ROOT, '8f')
        if os.path.exists(directory):
            shutil.rmtree(directory)


class FileWriteTest(TestCase):
    
    def setUp(self):
        self.text = "Spam Spam Spam Spam.\n"
        self.digest = hashlib.sha1(self.text).hexdigest()
        self.tempfile = TemporaryUploadedFile('spam4.txt', 'text/plain',
                                              len(self.text), 'utf-8')
        self.tempfile.file.write(self.text)
        self.tempfile.file.seek(0)
    
    def test(self):
        new_upload = Upload(file=self.tempfile)
        new_upload.save()
        
        # Upload has been saved to the database.
        self.assert_(new_upload.pk)
        
        # Upload contains correct content.
        self.assertEqual(new_upload.file.read(), self.text)
        
        # Filename is the hash of the file contents.
        self.assert_(new_upload.file.name.startswith(self.digest))
    
    def tearDown(self):
        self.tempfile.close()  # Also deletes the temp file.
        
        # Remove the upload in `MEDIA_ROOT`.
        directory = os.path.join(settings.MEDIA_ROOT, '24')
        if os.path.exists(directory):
            shutil.rmtree(directory)
