from django.db import models
from decimal import Decimal

class Billing(models.Model):
    STATUS_CHOICES = [
        ('UNPAID', 'Belum Bayar'),
        ('PARTIAL', 'Cicil'),
        ('PAID', 'Lunas'),
    ]
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='billings')
    deed = models.OneToOneField('deeds.Deed', on_delete=models.CASCADE, null=True, blank=True, related_name='billing')
    
    # --- Rincian Jasa Notaris ---
    honorarium = models.DecimalField("Jasa Notaris", max_digits=15, decimal_places=2, default=0)
    ppn_jasa = models.DecimalField("PPN 11%", max_digits=15, decimal_places=2, default=0, editable=False)
    
    # --- Pajak Transaksi (Titipan Klien) ---
    pph = models.DecimalField("PPh (Penjual)", max_digits=15, decimal_places=2, default=0)
    bphtb = models.DecimalField("BPHTB (Pembeli)", max_digits=15, decimal_places=2, default=0)
    pnbp = models.DecimalField("PNBP/Biaya BPN", max_digits=15, decimal_places=2, default=0)
    
    # --- Biaya Lain-lain ---
    biaya_lain = models.DecimalField("Biaya Tambahan", max_digits=15, decimal_places=2, default=0)
    keterangan_biaya_lain = models.CharField(max_length=255, blank=True, null=True)

    # --- Validasi Status Pajak ---
    is_pph_valid = models.BooleanField("PPh Sudah Valid", default=False)
    is_bphtb_valid = models.BooleanField("BPHTB Sudah Valid", default=False)
    
    # --- Total & Pembayaran ---
    total_tagihan = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0)
    terbayar = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    jatuh_tempo = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Billing {self.deed} - {self.client.nama_lengkap}"

    def save(self, *args, **kwargs):
        # 1. Hitung PPN Jasa (11% dari Honorarium)
        self.ppn_jasa = self.honorarium * Decimal('0.11')
        
        # 2. Total Tagihan (Tambahkan PPh dan BPHTB jika kantor yang membayarkan/menerima uangnya)
        self.total_tagihan = (
            self.honorarium + 
            self.ppn_jasa + 
            self.pph + 
            self.bphtb + 
            self.pnbp + 
            self.biaya_lain
        )
        
        # 3. Update status otomatis
        if self.total_tagihan > 0 and self.terbayar >= self.total_tagihan:
            self.status = 'PAID'
        elif self.terbayar > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'UNPAID'
            
        super().save(*args, **kwargs)

    @property
    def sisa_tagihan(self):
        return self.total_tagihan - self.terbayar