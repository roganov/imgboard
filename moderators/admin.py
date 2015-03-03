from django.contrib import admin
from .models import ModeratorAction, Ban

admin.site.register([ModeratorAction, Ban])
