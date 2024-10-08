"""RexChain URL Configuration
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import static
# Our Models
from .views import home, humans_txt, robots_txt
from blockchain.views import (
    tx_detail, block_detail,
    glossary, ValidateRxView
)

from nom151.views import validate_certificate

urlpatterns = [
    path('django-rq/', include('django_rq.urls')),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    re_path(r'^admin/', admin.site.urls),
    # API
    path('api/v1/', include('api.urls')),
    # Explorer
    path('', home, name='home'),
    path('hash/', tx_detail, name="tx_search"),
    re_path(r'^hash/(?P<hash_id>\w+)/$', tx_detail, name="tx_detail"),
    path('block/', block_detail, name="block_search"),
    re_path(r'^block/(?P<block_hash>\w+)/$', block_detail, name="block_detail"),
    # Attest to certificado NOM151
    re_path(r'^validate/(?P<hash_id>\w+)/$', ValidateRxView.as_view(), name="validate"),
    re_path(r'^validate_certificate/(?P<merkleroot>\w+)/$', validate_certificate, name="validate_certificate"),
    # Static content
    path('glosario/', glossary, name="glosario"),
    re_path(r'^humans.txt$', humans_txt, name="humans_txt"),
    re_path(r'^robots.txt$', robots_txt, name="robots_txt"),
]

# Show images stored local in dev
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
