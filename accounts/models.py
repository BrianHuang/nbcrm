from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理員'),
        ('cs', '客服'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cs', verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    
    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
