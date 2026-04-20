from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal, InvalidOperation
from apps.deeds.models import Deed 
from .models import Billing

@receiver(post_save, sender=Deed)
def create_billing_automatically(sender, instance, created, **kwargs):
    if created:
        try:
            raw_transaksi = instance.nilai_transaksi if instance.nilai_transaksi else 0
            transaksi = Decimal(str(raw_transaksi))

            honor = transaksi * Decimal('0.01')   # 1% Honorarium
            pph = transaksi * Decimal('0.025')    # 2.5% PPh
            bphtb = transaksi * Decimal('0.05')   # 5% BPHTB
            
            # 3. Buat Billing-nya
            Billing.objects.create(
                deed=instance,
                client=instance.client,
                honorarium=honor,
                pph=pph,
                bphtb=bphtb,
                pnbp=Decimal('50000'),
                keterangan_biaya_lain=f"Tagihan otomatis Akta No: {instance.nomor_akta}"
            )
        except (InvalidOperation, TypeError, ValueError) as e:
            print(f"Error saat membuat billing otomatis: {e}")