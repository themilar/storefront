from importlib.util import set_loader
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .serializers import CollectionSerializer, ProductSerialzer
from .models import Collection, Product, OrderItem


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    serializer_class = ProductSerialzer

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
