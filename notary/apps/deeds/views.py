from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from django.db import transaction
from django.conf import settings
from django.db.models import Q
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from .models import Deed, DeedPT, Shareholder, Management
from apps.clients.models import Client

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
        
    if request.headers.get('HX-Request') and request.headers.get('HX-Target') == 'deed-table-body':
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})
    
    return render(request, 'deeds/index.html', {'deeds': deeds})

@login_required
def add_deed(request):
    if request.method == "POST":
        with transaction.atomic():
            client_id = request.POST.get('client')
            client_obj = get_object_or_404(Client, id=client_id)
            kategori = request.POST.get('kategori')
            
            # Helper untuk membersihkan format ribuan
            def clean_money(val):
                return val.replace('.', '') if val else '0'

            # Tentukan apakah ini Akta PT atau Akta Biasa
            if kategori == 'NOTARIS':
                deed = DeedPT.objects.create(
                    nomor_akta=request.POST.get('nomor_akta'),
                    jenis_akta=request.POST.get('jenis_akta'),
                    kategori=kategori,
                    tanggal_buat=request.POST.get('tanggal_buat'),
                    jam_buat=request.POST.get('jam_buat') or None,
                    nama_entitas=request.POST.get('nama_entitas'),
                    kedudukan=request.POST.get('kedudukan'),
                    nilai_transaksi=clean_money(request.POST.get('nilai_transaksi')),
                    client=client_obj,
                    keterangan=request.POST.get('keterangan', ''),
                    file_scan=request.FILES.get('file_scan'),
                    # Field khusus PT
                    modal_dasar=clean_money(request.POST.get('modal_dasar')),
                    modal_ditempatkan=clean_money(request.POST.get('modal_ditempatkan')),
                    modal_disetor=clean_money(request.POST.get('modal_disetor')),
                    nilai_par_saham=clean_money(request.POST.get('nilai_par_saham', '0'))
                )
            else:
                deed = Deed.objects.create(
                    nomor_akta=request.POST.get('nomor_akta'),
                    jenis_akta=request.POST.get('jenis_akta'),
                    kategori=kategori,
                    tanggal_buat=request.POST.get('tanggal_buat'),
                    jam_buat=request.POST.get('jam_buat') or None,
                    nama_entitas=request.POST.get('nama_entitas'),
                    kedudukan=request.POST.get('kedudukan'),
                    nilai_transaksi=clean_money(request.POST.get('nilai_transaksi')),
                    client=client_obj,
                    keterangan=request.POST.get('keterangan', ''),
                    file_scan=request.FILES.get('file_scan')
                )

            # 2. Simpan Data Pemegang Saham
            sh_namas = request.POST.getlist('sh_nama[]')
            sh_niks = request.POST.getlist('sh_nik[]')
            sh_jumlahs = request.POST.getlist('sh_jumlah[]')
            sh_nominals = request.POST.getlist('sh_nominal[]')
            
            for i in range(len(sh_namas)):
                if sh_namas[i]: 
                    Shareholder.objects.create(
                        deed=deed,
                        nama=sh_namas[i],
                        nik=sh_niks[i] if i < len(sh_niks) else '',
                        jumlah_saham=sh_jumlahs[i] or 0,
                        total_nominal=clean_money(sh_nominals[i]) if i < len(sh_nominals) else 0
                    )

            # 3. Simpan Data Pengurus
            mg_namas = request.POST.getlist('mg_nama[]')
            mg_jabatans = request.POST.getlist('mg_jabatan[]')
            
            for i in range(len(mg_namas)):
                if mg_namas[i]:
                    Management.objects.create(
                        deed=deed,
                        nama=mg_namas[i],
                        jabatan=mg_jabatans[i]
                    )

        deeds = Deed.objects.all().order_by('-tanggal_buat')
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})
    
    clients = Client.objects.all().order_by('nama_lengkap')
    return render(request, 'deeds/deed_form.html', {'clients': clients})

@login_required
def edit_deed(request, pk):
    deed = get_object_or_404(Deed, pk=pk)
    # Cek apakah ini DeedPT
    is_pt = hasattr(deed, 'deedpt')
    if is_pt:
        deed = deed.deedpt
    
    if request.method == "POST":
        with transaction.atomic():
            client_id = request.POST.get('client')
            client_obj = get_object_or_404(Client, id=client_id)
            
            def clean_money(val):
                return val.replace('.', '') if val else '0'

            # Update data dasar
            deed.nomor_akta = request.POST.get('nomor_akta')
            deed.jenis_akta = request.POST.get('jenis_akta')
            deed.kategori = request.POST.get('kategori')
            deed.tanggal_buat = request.POST.get('tanggal_buat')
            deed.jam_buat = request.POST.get('jam_buat') or None
            deed.nama_entitas = request.POST.get('nama_entitas')
            deed.kedudukan = request.POST.get('kedudukan')
            deed.nilai_transaksi = clean_money(request.POST.get('nilai_transaksi'))
            deed.client = client_obj
            deed.keterangan = request.POST.get('keterangan', '')
            
            if request.FILES.get('file_scan'):
                deed.file_scan = request.FILES.get('file_scan')
            
            # Update field khusus PT jika objeknya DeedPT
            if is_pt:
                deed.modal_dasar = clean_money(request.POST.get('modal_dasar'))
                deed.modal_ditempatkan = clean_money(request.POST.get('modal_ditempatkan'))
                deed.modal_disetor = clean_money(request.POST.get('modal_disetor'))
                deed.nilai_par_saham = clean_money(request.POST.get('nilai_par_saham'))
            
            deed.save()

            # Refresh Relasi (Hapus & Buat Baru untuk kesederhanaan)
            deed.shareholders.all().delete()
            sh_namas = request.POST.getlist('sh_nama[]')
            sh_niks = request.POST.getlist('sh_nik[]')
            sh_jumlahs = request.POST.getlist('sh_jumlah[]')
            sh_nominals = request.POST.getlist('sh_nominal[]')
            for i in range(len(sh_namas)):
                if sh_namas[i]:
                    Shareholder.objects.create(
                        deed=deed,
                        nama=sh_namas[i],
                        nik=sh_niks[i],
                        jumlah_saham=sh_jumlahs[i] or 0,
                        total_nominal=clean_money(sh_nominals[i])
                    )

            deed.management.all().delete()
            mg_namas = request.POST.getlist('mg_nama[]')
            mg_jabatans = request.POST.getlist('mg_jabatan[]')
            for i in range(len(mg_namas)):
                if mg_namas[i]:
                    Management.objects.create(
                        deed=deed,
                        nama=mg_namas[i],
                        jabatan=mg_jabatans[i]
                    )
        
        deeds = Deed.objects.all().order_by('-tanggal_buat')
        return render(request, 'deeds/deed_table.html', {'deeds': deeds})

    clients = Client.objects.all().order_by('nama_lengkap')
    return render(request, 'deeds/deed_form.html', {
        'deed': deed, 
        'clients': clients,
        'is_pt': is_pt
    })

@require_http_methods(["DELETE"])
@login_required
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

@login_required
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