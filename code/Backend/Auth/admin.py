from django.contrib import admin
from .models import Team, UserProfile
# Register your models here.

class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',) 

admin.site.register(Team,TeamAdmin)
admin.site.register(UserProfile)
