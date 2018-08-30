"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from tastypie.api import Api
from hs_library.api.resources import UserResource, BookResource, WannaBookResource, MetaDataResource, \
    AuthorResource, SearchWannaBookResource, TagResource, TranslatorResource, SeriesResource, AppliedBookResource, \
    UnReturnedBookResource, FinishedBookResource, UncommentedBookResource, ReviewResource, LoanHistoryResource, BookRatingResource, \
    BookAnnotationResource

from django.views.generic import RedirectView
from .settings import SERVER_URL

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(AuthorResource())
v1_api.register(BookRatingResource())
v1_api.register(TagResource())
v1_api.register(TranslatorResource())
v1_api.register(SeriesResource())
v1_api.register(BookResource())
v1_api.register(MetaDataResource())
v1_api.register(WannaBookResource())
#v1_api.register(SearchBookResource())
v1_api.register(BookAnnotationResource())
v1_api.register(ReviewResource())

v1_api.register(SearchWannaBookResource())
#v1_api.register(NewBookResource())
v1_api.register(AppliedBookResource())
v1_api.register(UnReturnedBookResource())
v1_api.register(FinishedBookResource())
v1_api.register(UncommentedBookResource())
v1_api.register(LoanHistoryResource())


urlpatterns = [
    url(r'^admin/hs_library/book/uploads/<str:year>/<str:month>/<str:day>/<str:name>/',
         RedirectView.as_view(url='%s%s' % (SERVER_URL, 'static/uploads/%(year)s/%(month)s/%(day)s/%(name)s'))),
    url(r'^admin/', xadmin.site.urls),
    url(r'^hs_library/', include('hs_library.urls')),
    url(r'api/', include(v1_api.urls)),
]
