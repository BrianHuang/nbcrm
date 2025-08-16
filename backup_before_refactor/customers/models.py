from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    line_nickname = models.CharField(max_length=100, blank=True, verbose_name='Line 暱稱')
    n8_nickname = models.CharField(max_length=100, blank=True, verbose_name='N8 暱稱')
    n8_phone = models.CharField(max_length=20, blank=True, verbose_name='N8 電話')
    n8_email = models.EmailField(blank=True, verbose_name='N8 信箱')
    notes = models.TextField(blank=True, verbose_name='備註')
    verified_accounts = models.TextField(blank=True, verbose_name='驗證過的帳戶')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')
    
    class Meta:
        verbose_name = '客戶'
        verbose_name_plural = '客戶'
        ordering = ['-updated_at']
    
    def __str__(self):
        """預設顯示格式：姓名(N8暱稱)"""
        if self.n8_nickname:
            return f"{self.name}({self.n8_nickname})"
        else:
            return f"{self.name}(無N8暱稱)"
    
    def get_display_name(self):
        """返回完整的顯示名稱用於下拉選單"""
        if self.n8_nickname:
            return f"{self.name}({self.n8_nickname})"
        else:
            return f"{self.name}(無N8暱稱)"