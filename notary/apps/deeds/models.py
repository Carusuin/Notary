import os
from django.db import models
from apps.clients.models import Client

def get_upload_path(instance, filename):
    return os.path.join('arsip_akta', instance.kategori.lower(), filename)

class Deed(models.Model):
    KATEGORI_CHOICES = [
        ('PPAT', 'Akta PPAT'),
        ('NOTARIS', 'Akta Notaris'),
    ]

    # Identitas Dasar Akta
    nomor_akta = models.CharField(max_length=100, unique=True) # Contoh: "66" [cite: 5, 11]
    jenis_akta = models.CharField(max_length=100) # Contoh: "Akta Pendirian PT" [cite: 5, 9]
    kategori = models.CharField(max_length=10, choices=KATEGORI_CHOICES)
    tanggal_buat = models.DateField() # Contoh: 16-03-2026 [cite: 5, 12]
    
    # Data Spesifik Perusahaan (Opsional tergantung jenis akta)
    nama_perseroan = models.CharField(max_length=255, blank=True, null=True) # [cite: 10]
    kedudukan = models.CharField(max_length=100, blank=True, null=True) # 
    
    # Finansial (Sesuai Pasal 4 Akta)
    modal_dasar = models.DecimalField(max_digits=20, decimal_places=2, default=0) # [cite: 89]
    modal_disetor = models.DecimalField(max_digits=20, decimal_places=2, default=0) # [cite: 91]
    nilai_transaksi = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0,
        help_text="Nilai transaksi untuk akta jual beli/PPAT"
    )

    # Relasi
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='deeds')
    
    # File & Metadata
    keterangan = models.TextField(blank=True, null=True)
    file_scan = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nomor_akta} - {self.nama_perseroan if self.nama_perseroan else self.jenis_akta}"
    
class Shareholder(models.Model):
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE, related_name='shareholders')
    nama = models.CharField(max_length=255) # Contoh: Tuan MOHAMED RAFI AMANULLAH [cite: 221, 404]
    nik = models.CharField(max_length=20) # Contoh: 3578090402840003 [cite: 229]
    jumlah_saham = models.IntegerField() # Contoh: 1.800 [cite: 405]
    total_nominal = models.DecimalField(max_digits=20, decimal_places=2) # Contoh: 180.000.000 [cite: 405]

    def __str__(self):
        return f"{self.nama} - {self.jumlah_saham} Saham"

class Management(models.Model):
    POSITION_CHOICES = [
        ('DIREKTUR_UTAMA', 'Direktur Utama'),
        ('DIREKTUR', 'Direktur'),
        ('KOMISARIS', 'Komisaris'),
    ]
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE, related_name='management')
    nama = models.CharField(max_length=255) # Tuan MOHAMED FARHAN [cite: 201]
    jabatan = models.CharField(max_length=50, choices=POSITION_CHOICES) # DIREKTUR [cite: 201]
    
    def __str__(self):
        return f"{self.nama} ({self.jabatan})"  