# kyc/models.py
import os
from django.db import models
from django.contrib.auth import get_user_model
from customers.models import Customer
from django.core.validators import RegexValidator

User = get_user_model()

def kyc_upload_path(instance, filename):
    return f'kyc/{instance.customer.id}/{filename}'

class KYCRecord(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='kyc_records', 
        verbose_name='客戶'
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='kyc_uploads', 
        verbose_name='上傳客服'
    )
    bank_code = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{3}$', message='請填入3位數字的銀行代碼')],
        verbose_name='銀行代碼',
        help_text='請填入3位數字的銀行代碼（選填）'
    )
    verification_account = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d+$', message='只能填入數字')],
        verbose_name='驗證帳戶',
        help_text='請填入數字帳號（選填）'
    )
    file = models.FileField(
        upload_to=kyc_upload_path, 
        verbose_name='檔案',
        blank=True,
        null=True,
        help_text='支援圖片和影片檔案，檔案大小不超過10MB（選填）'
    )
    file_description = models.TextField(
        blank=True,
        verbose_name='檔案說明',
        help_text='對此檔案的說明或備註（選填）'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='上傳時間'
    )
    
    class Meta:
        verbose_name = 'KYC 記錄'
        verbose_name_plural = 'KYC 記錄'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        bank_info = f"({self.bank_code})" if self.bank_code else ""
        account_info = f" - {self.verification_account}" if self.verification_account else ""
        file_info = " [有檔案]" if self.file else " [無檔案]"
        return f"{self.customer.name}{account_info}{bank_info}{file_info}"
    
    def get_file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ""
    
    def is_image(self):
        if not self.file:
            return False
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return self.get_file_extension() in image_extensions
    
    def is_video(self):
        if not self.file:
            return False
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
        return self.get_file_extension() in video_extensions
    
    def get_file_size_display(self):
        """返回易讀的檔案大小"""
        if self.file:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "無檔案"
