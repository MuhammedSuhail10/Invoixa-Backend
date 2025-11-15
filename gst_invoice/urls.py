from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from .utils.auth import AsyncJWTAuth
from user.views import user_api
from company.views import company_api
from customer.views import customer_api
from product.views import product_api
from order.views import order_api

api = NinjaAPI(auth=AsyncJWTAuth())
api.add_router("/user/", user_api)
api.add_router("/company/", company_api)
api.add_router("/product/", product_api)
api.add_router("/customer/", customer_api)
api.add_router("/order/", order_api)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)