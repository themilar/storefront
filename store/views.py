from django.db.models.aggregates import Count
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .serializers import CollectionSerializer, ProductSerialzer, ReviewSerializer
from .models import Collection, Product, OrderItem, Review


class ProductViewSet(ModelViewSet):

    serializer_class = ProductSerialzer

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
                }
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
