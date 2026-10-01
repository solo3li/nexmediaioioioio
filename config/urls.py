from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

from apps.accounts import views as accounts_views
from apps.billing import views as billing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', views.set_language_view, name='set_language'),
    path('', views.home, name='home'),
    path('studio/', include('apps.tools.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('affiliate/', include('apps.affiliate.urls')),
    path('support/', include('apps.support.urls')),
    path('billing/', include('apps.billing.urls')),
    path('invoices/', billing_views.invoices_list_view, name='invoices_list'),
    path('invoices/<int:invoice_id>/', billing_views.invoice_detail_view, name='invoice_detail'),
    path('', include('apps.history.urls')),
]
