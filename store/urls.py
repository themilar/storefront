from cgitb import lookup
from django.urls import path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet)
router.register("customers", views.CustomerViewSet)
router.register("orders", views.OrderViewSet, basename="orders")

cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

product_router = routers.NestedDefaultRouter(router, "products", lookup="product")
product_router.register("reviews", views.ReviewViewSet, basename="product-reviews")
image_upload_router = [path("images", views.ImageUploadView.as_view())]
urlpatterns = router.urls + product_router.urls + cart_router.urls + image_upload_router
