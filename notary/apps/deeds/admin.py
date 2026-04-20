from django.contrib import admin
from .models import Deed, Shareholder, Management

class ShareholderInline(admin.TabularInline):
    model = Shareholder
    extra = 1 # Menampilkan 1 baris kosong tambahan

class ManagementInline(admin.TabularInline):
    model = Management
    extra = 1

@admin.register(Deed)
class DeedAdmin(admin.ModelAdmin):
    inlines = [ShareholderInline, ManagementInline]
    list_display = ('nomor_akta', 'jenis_akta', 'client', 'tanggal_buat')
    search_fields = ('nomor_akta', 'nama_perseroan')