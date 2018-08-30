from django.conf.urls import url
from . import views


app_name = 'hs_library'

urlpatterns = [
    url('', views.LoginOutView.as_view(template_name='hs_library/index.html'), name='index'),

]