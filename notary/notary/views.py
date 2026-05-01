from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils import timezone
from apps.clients.models import Client
from apps.deeds.models import Deed
from apps.finance.models import Billing

@login_required
def index(request):
    # 1. Total Penghadap (Klien)
    total_clients = Client.objects.count()
    
    # 2. Akta Bulan Ini
    now = timezone.now()
    deeds_this_month = Deed.objects.filter(
        tanggal_buat__month=now.month, 
        tanggal_buat__year=now.year
    ).count()
    
    # 3. Menunggu Tanda Tangan (Asumsi: Belum ada file scan)
    waiting_signature = Deed.objects.filter(file_scan='').count()
    
    # 4. Tagihan Outstanding (Sisa Tagihan)
    billings = Billing.objects.exclude(status='PAID')
    outstanding_total = sum(b.sisa_tagihan for b in billings)
    
    # Aktivitas Terakhir
    recent_clients = Client.objects.all()[:2]
    recent_deeds = Deed.objects.all()[:2]
    
    context = {
        'total_clients': total_clients,
        'deeds_this_month': deeds_this_month,
        'waiting_signature': waiting_signature,
        'outstanding_total': outstanding_total,
        'recent_clients': recent_clients,
        'recent_deeds': recent_deeds,
    }
    
    return render(request, 'index.html', context)