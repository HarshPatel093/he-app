from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'gender', 'date_of_birth', 'date_joined')
    search_fields = ('name', 'user__email', 'role', 'gender')
    list_filter = ('role', 'gender')

    def email(self, obj):
        return obj.user.email  

    def date_joined(self, obj):
        return obj.user.date_joined.strftime("%Y-%m-%d %H:%M")  
