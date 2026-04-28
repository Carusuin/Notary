from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import resolve_url

class HtmxLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Jika request datang dari HTMX
        if hasattr(request, 'htmx') and request.htmx:
            # Jika response adalah redirect (302)
            if response.status_code == 302:
                login_url = resolve_url(settings.LOGIN_URL)
                # Cek apakah target redirect adalah halaman login
                if response.url.startswith(login_url) or response.url.startswith(request.build_absolute_uri(login_url)):
                    # Kirim header HX-Redirect agar HTMX melakukan redirect satu halaman penuh ke login
                    # Kita gunakan status 204 (No Content) agar HTMX tidak mencoba swap konten apapun
                    return HttpResponse(status=204, headers={'HX-Redirect': response.url})
        
        return response
