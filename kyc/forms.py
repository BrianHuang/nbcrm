# kyc/forms.py
from django import forms
from .models import KYCRecord

class KYCRecordForm(forms.ModelForm):
    class Meta:
        model = KYCRecord
        fields = ['customer', 'bank_code', 'verification_account', 'file', 'file_description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 自定義客戶選項顯示格式
        from customers.models import Customer
        customers = Customer.objects.all().order_by('name')
        customer_choices = [('', '請選擇客戶')]
        for customer in customers:
            customer_choices.append((customer.id, customer.get_display_name()))
        
        self.fields['customer'] = forms.ModelChoiceField(
            queryset=Customer.objects.all().order_by('name'),
            empty_label='請選擇客戶',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        
        # 重新設置客戶選項的顯示文字
        self.fields['customer'].label_from_instance = lambda obj: obj.get_display_name()
        
        # 設置CSS類別
        for field_name, field in self.fields.items():
            if field_name == 'file_description':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3
            elif field_name == 'customer':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # 設置欄位屬性
        self.fields['bank_code'].widget.attrs.update({
            'placeholder': '例如：004、012、822（選填）',
            'pattern': '[0-9]{3}',
            'maxlength': '3',
            'title': '請填入3位數字的銀行代碼'
        })
        
        self.fields['verification_account'].widget.attrs.update({
            'placeholder': '請填入數字帳號（選填）',
            'pattern': '[0-9]+',
            'title': '只能填入數字'
        })
        
        self.fields['file_description'].widget.attrs.update({
            'placeholder': '對此檔案的說明或備註（選填）'
        })
        
        # 設置欄位標籤和說明
        self.fields['customer'].label = '客戶'
        self.fields['customer'].help_text = '請選擇客戶'
        
        self.fields['bank_code'].label = '銀行代碼'
        self.fields['bank_code'].help_text = '請填入3位數字的銀行代碼（選填）'
        self.fields['bank_code'].required = False
        
        self.fields['verification_account'].label = '驗證帳戶'
        self.fields['verification_account'].help_text = '請填入數字帳號（選填）'
        self.fields['verification_account'].required = False
        
        self.fields['file'].label = 'KYC檔案'
        self.fields['file'].help_text = '支援圖片和影片檔案，檔案大小不超過10MB'
        
        self.fields['file_description'].label = '檔案說明'
        self.fields['file_description'].help_text = '對此檔案的說明或備註（選填）'
        self.fields['file_description'].required = False
    
    def clean_bank_code(self):
        bank_code = self.cleaned_data.get('bank_code')
        if bank_code and bank_code.strip() == '':
            return None
        return bank_code
    
    def clean_verification_account(self):
        verification_account = self.cleaned_data.get('verification_account')
        if verification_account and verification_account.strip() == '':
            return None
        return verification_account
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 檢查檔案大小 (10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('檔案大小不能超過 10MB')
            
            # 檢查檔案類型
            allowed_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # 圖片
                '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'   # 影片
            ]
            file_ext = '.' + file.name.lower().split('.')[-1]
            if file_ext not in allowed_extensions:
                raise forms.ValidationError(
                    '不支援的檔案格式。請上傳圖片或影片檔案。'
                )
        
        return file