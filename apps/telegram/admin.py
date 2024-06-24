from django.contrib import admin
from apps.telegram.models import UserBusiness, Business, UserCklient, Cklient
# Register your models here.

@admin.register(UserBusiness)
class UserBusinessAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_id')

@admin.register(UserCklient)
class UserClient(admin.ModelAdmin):
    list_display = ('username', 'user_id')


@admin.register(Business)
class BussinesAdmin(admin.ModelAdmin):
    list_display = ('region','user', 'pansionat', 'is_active')
    
admin.site.register(Cklient)
