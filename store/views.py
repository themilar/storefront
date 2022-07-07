from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)

from .filters import ProductFilter
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    ProductSerialzer,
    ReviewSerializer,
    UpdateCartItemSerializer,
)
from .models import CartItem, Collection, Product, OrderItem, Review, Cart
from .pagination import DefaultProductPagination


class ProductViewSet(ModelViewSet):

    serializer_class = ProductSerialzer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    pagination_class = DefaultProductPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        collection_id = self.request.query_params.get("collection_id")
        if collection_id:
            queryset = queryset.filter(
                collection_id=self.request.query_params.get("collection_id")
            )
        return queryset

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):

        if OrderItem.objects.filter(product_id=kwargs.get("pk")):
            return Response(
                {
                    "error": "Product cannot be deleted because there are orders associated with it"
                }
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.annotate(product_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs.get("pk")):
            return Response(
                {
                    "error": "Collection cannot be deleted because it contains one or more products"
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):

    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs.get("product_pk"))

    def get_serializer_context(self):
        return {"product_id": self.kwargs.get("product_pk")}

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Cannot create a review for a product that doesn't exist"}
            )
        return super().perform_create(request, *args, **kwargs)


class CartViewSet(
    GenericViewSet, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        serializer_dict = {
            "POST": AddCartItemSerializer,
            "PATCH": UpdateCartItemSerializer,
            "DEFAULT": CartItemSerializer,
        }
        return serializer_dict.get(self.request.method, serializer_dict["DEFAULT"])

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )

    def get_serializer_context(self):
        return {"cart_id": self.kwargs.get("cart_pk")}
