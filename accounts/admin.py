from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('額外資訊', {'fields': ('role', 'created_at')}),
    )
    
    readonly_fields = ('created_at',)
    
    list_display = ('get_display_name', 'username', 'email', 'role', 'is_active', 'created_at')
    list_filter = BaseUserAdmin.list_filter + ('role',)
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = '顯示名稱'
    get_display_name.admin_order_field = 'first_name'
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets + (
                ('角色設定', {'fields': ('role',)}),
                ('個人資訊', {'fields': ('first_name', 'last_name')}),
            )
        return super().get_fieldsets(request, obj)