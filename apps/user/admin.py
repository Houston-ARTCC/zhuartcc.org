from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('cid', 'first_name', 'last_name', 'email', 'rating', 'user_is_active', 'main_role', 'staff_role',
                    'training_role', 'home_facility')

    def user_is_active(self, obj):
        return obj.status < 2

    user_is_active.boolean = True
