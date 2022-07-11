from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)

from .perimissions import IsAdminOrReadOnly

from .filters import ProductFilter
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSerializer,
    CreateOrderSerializer,
    CustomerSerializer,
    OrderSerializer,
    ProductSerialzer,
    ReviewSerializer,
    UpdateCartItemSerializer,
    UpdateOrderSerializer,
)
from .models import (
    CartItem,
    Collection,
    Customer,
    Order,
    Product,
    OrderItem,
    Review,
    Cart,
)
from .pagination import DefaultProductPagination


class ProductViewSet(ModelViewSet):

    serializer_class = ProductSerialzer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    pagination_class = DefaultProductPagination
    permission_classes = (IsAdminOrReadOnly,)

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
    permission_classes = (IsAdminOrReadOnly,)

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


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAdminUser,)

    @action(detail=False, methods=["GET", "PUT"], permission_classes=(IsAuthenticated,))
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "POST":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return (IsAdminUser(),)
        return (IsAuthenticated(),)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only("id").get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def get_serializer_class(self):

        if self.request.method == "POST":
            return CreateOrderSerializer
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer
