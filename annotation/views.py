from rest_framework import serializers
from rest_framework import generics
from models import Annotation
from rest_framework.response import Response


class AnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Annotation
        fields = ('id', 'quote', 'ranges', 'text', 'uri')


class AnnotationC(generics.CreateAPIView):
    serializer_class = AnnotationSerializer


class AnnotationRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


class AnnotationSearch(generics.ListAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request, *args, **kwargs):
        # Clean up the dictionary of query parameters
        params = dict(request.query_params)
        for k, v in params.items():
            if type(v) == list and len(v) == 1:
                params[k] = v[0]
        if 'format' in params:
            del params['format']

        # Filter the queryset
        queryset = self.queryset.filter(**params)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
