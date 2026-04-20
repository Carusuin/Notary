from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.db.models import Q
from xhtml2pdf import pisa
from .models import Deed, Shareholder
from apps.clients.models import Client
import os
from django.contrib.auth.decorators import login_required

@login_required
def index_deeds(request):
    deeds = Deed.objects.all().order_by('-tanggal_buat')
    search_query = request.GET.get('search', '')
    kategori_filter = request.GET.get('kategori', '')

    if kategori_filter:
        deeds = deeds.filter(kategori=kategori_filter)

    if search_query:
        deeds = deeds.filter(
            Q(nomor_akta__icontains=search_query) | 
            Q(jenis_akta__icontains=search_query) |
            Q(client__nama_lengkap__icontains=search_query)
        )
        
    if request.headers.get('HX-Request'):
        # Kirim HANYA potongan tabel, agar tidak terjadi tumpukan UI
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})
    
    # Kirim HALAMAN UTUH saat pertama kali dibuka atau di-refresh
    return render(request, 'deeds/index.html', {'deeds': deeds})

def add_deed(request):
    if request.method == "POST":
        with transaction.atomic(): # Memastikan data tersimpan sepaket
            client_id = request.POST.get('client')
            client_obj = get_object_or_404(Client, id=client_id)
            
            # 1. Simpan Data Utama Akta
            deed = Deed.objects.create(
                nomor_akta=request.POST.get('nomor_akta'),
                jenis_akta=request.POST.get('jenis_akta'),
                nama_perseroan=request.POST.get('nama_perseroan'), # PT. Nusantara Tani Makmur
                modal_dasar=request.POST.get('modal_dasar', 0),
                modal_disetor=request.POST.get('modal_disetor', 0),
                tanggal_buat=request.POST.get('tanggal_buat'),
                client=client_obj,
                keterangan=request.POST.get('keterangan', ''),
                file_scan=request.FILES.get('file_scan')
            )

            # 2. Ambil List Data Pemegang Saham dari Form
            # Asumsikan di HTML inputnya bernama: name="shareholder_nama[]"
            namas = request.POST.getlist('sh_nama[]')
            sahams = request.POST.getlist('sh_jumlah[]')
            nominals = request.POST.getlist('sh_nominal[]')
            
            for i in range(len(namas)):
                if namas[i]: # Hanya simpan jika nama diisi
                    Shareholder.objects.create(
                        deed=deed,
                        nama=namas[i],
                        jumlah_saham=sahams[i] or 0,
                        total_nominal=nominals[i].replace('.', '') or 0
                    )

        # Setelah sukses, tampilkan tabel terbaru (logic HTMX Anda)
        deeds = Deed.objects.all().order_by('-tanggal_buat')
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})

def edit_deed(request, pk):
    # Ambil data akta yang mau diedit, kalau tidak ada munculkan 404
    deed = get_object_or_404(Deed, pk=pk)
    
    if request.method == "POST":
        # Ambil ID klien dari dropdown
        client_id = request.POST.get('client')
        client_obj = get_object_or_404(Client, id=client_id)
        
        # Update data akta
        deed.nomor_akta = request.POST.get('nomor_akta')
        deed.jenis_akta = request.POST.get('jenis_akta')
        deed.kategori = request.POST.get('kategori')
        deed.tanggal_buat = request.POST.get('tanggal_buat')
        deed.client = client_obj
        deed.keterangan = request.POST.get('keterangan', '')
        if request.FILES.get('file_scan'):
            deed.file_scan = request.FILES.get('file_scan')
        deed.save()
        
        
        # Kirim balik potongan tabel agar data di layar langsung terupdate
        deeds = Deed.objects.all().order_by('-tanggal_buat')
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})

    # Jika GET: Tampilkan modal form dengan data yang sudah terisi
    clients = Client.objects.all().order_by('nama_lengkap')
    return render(request, 'deeds/deed_form.html', {
        'deed': deed, 
        'clients': clients
    })

@require_http_methods(["DELETE"])
def delete_deed(request, pk):
    deed = get_object_or_404(Deed, pk=pk)
    deed.delete()
    
    # Refresh daftar tabel setelah dihapus
    deeds = Deed.objects.all().order_by('-tanggal_buat')
    return render(request, 'deeds/deed_table.html', {'deeds': deeds})

def link_callback(uri, rel):
    """
    Hardcode URI Django (seperti /media/) absolut path sistem file.
    """
    # Menggunakan settings.MEDIA_URL dan settings.MEDIA_ROOT
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri

    # Pastikan file-nya ada
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (settings.MEDIA_URL, settings.STATIC_URL)
        )
    return path

def export_deed_pdf(request, pk):
    deed = get_object_or_404(Deed, pk=pk)
    template_path = 'deeds/pdf_template.html'
    
    # Masukkan path logo ke context
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_kantor.png') # SESUAIKAN NAMA FILE
    context = {
        'deed': deed,
        'logo_path': logo_path, # Kirim path logo ke template
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Tanda_Terima_{deed.nomor_akta}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # TAMBAHKAN link_callback DI SINI:
    pisa_status = pisa.CreatePDF(
       html, dest=response,
       link_callback=link_callback # Gunakan fungsi bantuan
    )
    
    if pisa_status.err:
        return HttpResponse('Terjadi error saat cetak PDF', status=400)
    return response