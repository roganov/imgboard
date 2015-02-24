from django.contrib import admin

# Register your models here.
from .models import Board, Thread, Post
admin.site.register([Board, Thread, Post])
