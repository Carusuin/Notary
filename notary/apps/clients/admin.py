from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    # 1. Kolom yang tampil di halaman daftar (tabel utama)
    list_display = ('nik', 'nama_lengkap', 'nomor_telepon', 'is_perusahaan', 'created_at')
    
    # 2. Fitur pencarian (Sangat berguna jika klien sudah ribuan)
    # Anda bisa mencari berdasarkan Nama atau NIK sekaligus
    search_fields = ('nama_lengkap', 'nik')
    
    # 3. Filter di sebelah kanan (Mempermudah sortir data)
    list_filter = ('is_perusahaan', 'created_at')
    
    # 4. Urutan data (Data terbaru muncul di paling atas)
    ordering = ('-created_at',)
    
    # 5. Pengelompokan field saat kita menambah/edit data
    fieldsets = (
        ('Identitas Utama', {
            'fields': ('nik', 'nama_lengkap', 'foto_ktp')
        }),
        ('Informasi Kontak', {
            'fields': ('nomor_telepon', 'email', 'pekerjaan', 'alamat_ktp')
        }),
        ('Kategori Hukum', {
            'fields': ('is_perusahaan', 'nama_perusahaan'),
            'description': 'Centang jika penghadap bertindak atas nama PT atau CV.'
        }),
    )

    # 6. Menjadikan NIK sebagai link untuk klik detail
    list_display_links = ('nik', 'nama_lengkap')