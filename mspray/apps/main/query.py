from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, OuterRef, Subquery, Value
from django.db.models import IntegerField, PositiveIntegerField, Count

from mspray.apps.main.models.spray_day import SprayDay,\
    SprayDayHealthCenterLocation


def get_location_qs(qs, level=None):
    if level == 'RHC':
        sprays = SprayDayHealthCenterLocation.objects.filter(
            location=OuterRef('pk'),
            content_object__data__has_key='osmstructure:node:id'
        ).order_by().values('location')
        new_structure_count = sprays.annotate(c=Count('location')).values('c')
        qs = qs.annotate(
            num_new_structures=Coalesce(Subquery(
                queryset=new_structure_count,
                output_field=IntegerField()), Value(0))
        ).annotate(
            total_structures=ExpressionWrapper(
                F('num_new_structures') + F('structures'),
                output_field=IntegerField()
            )
        )
    else:
        sprays = SprayDay.objects.filter(
            location=OuterRef('pk'),
            data__has_key='osmstructure:node:id').order_by().values('location')
        new_structure_count = sprays.annotate(c=Count('location')).values('c')
        qs = qs.annotate(
            num_new_structures=Coalesce(Subquery(
                queryset=new_structure_count,
                output_field=PositiveIntegerField()), Value(0))
        ).annotate(
            total_structures=ExpressionWrapper(
                F('num_new_structures') + F('structures'),
                output_field=PositiveIntegerField()
            )
        )

    return qs
