from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Goal,Progress,CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets+(
        ('Tier Info',{'fields':('tier',)}),

    )
    add_fieldsets=UserAdmin.add_fieldsets+(
        ('Tier Info',{'fields':('tier',)}),
    )
    list_display=['username','email','tier']




admin.site.register(Progress)
admin.site.register(Goal)
