from cgitb import lookup
from django.urls import path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)

product_router = routers.NestedDefaultRouter(router, "products", lookup="product")
product_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

urlpatterns = router.urls + product_router.urls
