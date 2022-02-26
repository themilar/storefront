from importlib.util import set_loader
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CollectionSerializer, ProductSerialzer
from .models import Collection, Product
from store import serializers


class ProductList(ListCreateAPIView):

    queryset = Product.objects.select_related('collection').all()
    serializer_class = ProductSerialzer

    def get_serializer_context(self):
        return {'request': self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerialzer

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count > 0:
            return Response({"error": "Product cannot be deleted because there are orders associated with it"})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        product_count=Count('products')).all()
    serializer_class = CollectionSerializer


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(
        product_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def delete(self, reuqest, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it contains one or more products'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
