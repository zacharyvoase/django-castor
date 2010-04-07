# -*- coding: utf-8 -*-

from django.db import models

from djcastor import CAStorage


class Upload(models.Model):
    
    file = models.FileField(upload_to='uploads', storage=CAStorage())
    created = models.DateTimeField(auto_now_add=True)
