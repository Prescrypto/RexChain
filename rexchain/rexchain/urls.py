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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.views.generic.base import RedirectView
# Our Models
from .views import home, humans_txt, robots_txt, landing_page
from blockchain.views import (
    tx_detail, block_detail,
    poe, ValidateRxView
)

urlpatterns = [
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', admin.site.urls),
    # API
    url(r'^api/v1/', include('api.urls')),
    # Explorer
    url(r'^$', home, name='home'),
    url(r'^hash/$', tx_detail, name="tx_search"),
    url(r'^hash/(?P<hash_id>\w+)/$', tx_detail, name="tx_detail"),
    url(r'^block/$', block_detail, name="block_search"),
    url(r'^block/(?P<block_hash>\w+)/$', block_detail, name="block_detail"),
    # Attest PoE
    url(r'^validate/(?P<hash_id>\w+)/$', ValidateRxView.as_view(), name="validate"),
    # Static content
    url(r'^proof-of-existence/$', poe, name="proof-of-existence"),
    url(r'^humans.txt$', humans_txt, name="humans_txt"),
    url(r'^robots.txt$', robots_txt, name="robots_txt"),
    url(r'^battlefield$', RedirectView.as_view(pattern_name='landing_page', permanent=False)),
    url(r'^demoday$', landing_page, name="landing_page"),

]

# Show images stored local in dev
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
