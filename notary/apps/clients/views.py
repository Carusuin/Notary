from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib.auth.decorators import login_required

@login_required
def client_list(request):
    query = request.GET.get('search', '')
    clients = Client.objects.all().order_by('-created_at')
    
    if query:
        clients = clients.filter(
            Q(nama_lengkap__icontains=query) | 
            Q(email__icontains=query) |
            Q(nomor_telepon__icontains=query) |
            Q(alamat_ktp__icontains=query)
        )
    
    # If search via HTMX
    if request.htmx and request.headers.get('HX-Target') == 'client-grid':
        return render(request, 'clients/client_card.html', {'clients': clients})
    
    # Navigation or full page load
    return render(request, 'clients/main.html', {'clients': clients})

#CREATE
@login_required
def add_client(request):
    if request.method == "POST":
        nama = request.POST.get('nama_lengkap')
        nik = request.POST.get('nik')
        telepon = request.POST.get('nomor_telepon')
        email = request.POST.get('email')
        alamat = request.POST.get('alamat_ktp')
        tgl_lahir = request.POST.get('tanggal_lahir')

        Client.objects.create(
            nama_lengkap=nama,
            nik=nik, 
            nomor_telepon=telepon,
            email=email,
            alamat_ktp=alamat,
            tanggal_lahir=tgl_lahir
        )
        
        clients = Client.objects.all().order_by('-created_at')
        return render(request, 'clients/client_card.html', {'clients': clients})
    
    return render(request, 'clients/client_form.html')

#UPDATE
@login_required
def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == "POST":
        # Update data dari form
        client.nama_lengkap = request.POST.get('nama_lengkap')
        client.nik = request.POST.get('nik')
        client.nomor_telepon = request.POST.get('nomor_telepon')
        client.email = request.POST.get('email')
        client.alamat_ktp = request.POST.get('alamat_ktp')
        client.tanggal_lahir = request.POST.get('tanggal_lahir')
        client.save()
        
        # Setelah simpan, refresh daftar kartu
        clients = Client.objects.all().order_by('-created_at')
        return render(request, 'clients/client_card.html', {'clients': clients})

    # Jika GET, tampilkan form yang sudah terisi data klien saat ini
    return render(request, 'clients/client_form.html', {'client': client})

#DELETE
@require_http_methods(["DELETE"])
@login_required
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    
    # Ambil data terbaru untuk me-refresh grid
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'clients/client_card.html', {'clients': clients})