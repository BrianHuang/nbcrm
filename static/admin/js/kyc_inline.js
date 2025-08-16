// NBCRM KYC Inline JavaScript 
document.addEventListener('DOMContentLoaded', function() { 
    console.log('NBCRM KYC script loaded'); 
 
    // KYC 檔�?上傳?��? 
    const fileInputs = document.querySelectorAll('input[type="file"]'); 
    fileInputs.forEach(function(input) { 
        input.addEventListener('change', function(e) { 
            const file = e.target.files[0]; 
            if (file && file.size > 5 * 1024 * 1024) { 
                alert('檔�?大�?不能超�? 5MB'); 
                e.target.value = ''; 
            } 
        }); 
    }); 
}); 
