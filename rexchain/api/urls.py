# -*- encoding: utf-8 -*-
from django.conf.urls import url, include

# My views
from api.views import router
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
  url(r'^', include(router.urls)),
  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]