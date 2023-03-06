from django.contrib.admin import site

from .models import User

site.register(User)
