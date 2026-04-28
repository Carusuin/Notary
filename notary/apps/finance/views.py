from django.shortcuts import render, get_object_or_404, redirect
from .models import Billing
from decimal import Decimal # Tambahkan ini supaya baris 23 tidak error
from django.contrib.auth.decorators import login_required

@login_required
def billing_list(request):
    # Ambil semua data billing, urutkan dari yang terbaru
    billings = Billing.objects.all().order_by('-created_at')
    
    # Hitung total piutang
    total_piutang = sum(b.sisa_tagihan for b in billings if b.status != 'PAID')
    
    return render(request, 'finance/billing_list.html', {
        'billings': billings,
        'total_piutang': total_piutang
    })

@login_required
def billing_detail(request, pk):
    # Sekarang get_object_or_404 sudah benar namanya
    billing = get_object_or_404(Billing, pk=pk)
    
    if request.method == 'POST':
        jumlah_bayar = request.POST.get('jumlah_bayar')
        if jumlah_bayar:
            # Decimal sekarang sudah di-import di atas
            billing.terbayar += Decimal(jumlah_bayar)
            billing.save() 
            return redirect('finance:billing_detail', pk=pk)

    return render(request, 'finance/billing_detail.html', {'billing': billing})