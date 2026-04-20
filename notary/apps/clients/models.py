from django.db import models
import os

class Client(models.Model):
    # Identitas Utama
    nik = models.CharField(max_length=16, unique=True, verbose_name="NIK KTP")
    nama_lengkap = models.CharField(max_length=255)
    tempat_lahir = models.CharField(max_length=100)
    tanggal_lahir = models.DateField(null=True, blank=True)
    # Detail Personal
    pekerjaan = models.CharField(max_length=100, blank=True, null=True)
    alamat_ktp = models.TextField()
    nomor_telepon = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    # Status Hukum
    is_perusahaan = models.BooleanField(default=False, verbose_name="Mewakili Badan Hukum?")
    nama_perusahaan = models.CharField(max_length=255, blank=True, null=True)
    # File & Metadata
    foto_ktp = models.ImageField(upload_to='ktp_scans/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Penghadap"
        verbose_name_plural = "Daftar Penghadap"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nik} - {self.nama_lengkap}"

class ClientInteraction(models.Model):
    """Untuk mencatat riwayat interaksi atau catatan khusus tiap klien"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    catatan = models.TextField()
    tanggal_kontak = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Catatan untuk {self.client.nama_lengkap} pada {self.tanggal_kontak.date()}"