from rest_framework import serializers
from rest_framework import generics
from models import Annotation


class AnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Annotation
        fields = ('id', 'quote', 'ranges', 'text', 'uri')


class AnnotationC(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


class AnnotationRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
