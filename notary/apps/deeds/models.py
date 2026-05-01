import os
from django.db import models
from apps.clients.models import Client

def get_upload_path(instance, filename):
    # Menggunakan kategori dari instance (karena DeedPT mewarisi kategori dari Deed)
    return os.path.join('arsip_akta', instance.kategori.lower(), filename)

class Deed(models.Model):
    KATEGORI_CHOICES = [
        ('PPAT', 'Akta PPAT'),
        ('NOTARIS', 'Akta Notaris'),
    ]

    # Identitas Dasar Akta (Header PDF)
    nomor_akta = models.CharField(max_length=100, unique=True)
    jenis_akta = models.CharField(max_length=100) 
    kategori = models.CharField(max_length=10, choices=KATEGORI_CHOICES)
    tanggal_buat = models.DateField()
    jam_buat = models.TimeField(null=True) # Wajib untuk kalimat "Pukul 14.00 WIB"
    
    # Data Umum Entitas (Muncul di Cover)
    nama_entitas = models.CharField(max_length=255, null=True) 
    kedudukan = models.CharField(max_length=100, blank=True, null=True) 
    
    # Nilai Transaksi umum (tetap di parent untuk keperluan billing/statistik global)
    nilai_transaksi = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='deeds')
    keterangan = models.TextField(blank=True, null=True)
    file_scan = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nomor_akta} - {self.nama_entitas}"

class DeedPT(Deed):
    modal_dasar = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    modal_ditempatkan = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    modal_disetor = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nilai_par_saham = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Akta PT"
        verbose_name_plural = "Akta PT"

class Shareholder(models.Model):
    # Relasi ke Deed (Parent) agar bisa dipakai semua jenis akta
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE, related_name='shareholders')
    nama = models.CharField(max_length=255)
    nik = models.CharField(max_length=20)
    jumlah_saham = models.IntegerField()
    total_nominal = models.DecimalField(max_digits=20, decimal_places=2)
    persentase = models.FloatField(editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Logika otomatis hitung persentase sebelum simpan
        # Mencoba akses ke data DeedPT jika ada
        try:
            if hasattr(self.deed, 'deedpt'):
                modal_disetor = self.deed.deedpt.modal_disetor
                if modal_disetor > 0:
                    self.persentase = (float(self.total_nominal) / float(modal_disetor)) * 100
        except:
            pass
        super().save(*args, **kwargs)

class Management(models.Model):
    POSITION_CHOICES = [
        ('DIREKTUR_UTAMA', 'Direktur Utama'),
        ('DIREKTUR', 'Direktur'),
        ('KOMISARIS_UTAMA', 'Komisaris Utama'),
        ('KOMISARIS', 'Komisaris'),
    ]
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE, related_name='management')
    nama = models.CharField(max_length=255)
    jabatan = models.CharField(max_length=50, choices=POSITION_CHOICES)