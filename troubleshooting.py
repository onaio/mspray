from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import SprayPoint


def sprayed(l):
    """All sprayed"""
    for s in l.location_set.all().order_by('name'):
        qs = SprayDay.objects.filter(location=s)
        print(s.name, qs.filter(was_sprayed=True).count())


def found(l):
    """Found: All sprayed + all unique not sprayed that are sprayable"""
    for s in l.location_set.all().order_by('name'):
        qs = SprayDay.objects.filter(location=s)
        print(s.name,
              qs.filter(was_sprayed=True).count() +
              qs.filter(was_sprayed=False, spraypoint__isnull=False,
                        data__contains={'sprayable_structure': 'yes'}
                        ).count()
              )


def duplicate_spraypoints():
    d = SprayPoint.objects.filter().values('sprayday').distinct().count()
    a = SprayPoint.objects.filter().values('sprayday').count()
    if d < a:
        m = list(SprayPoint.objects.values_list('sprayday', flat=True))
        n = set([i for i in m if m.count(i) > 1])
        assert len(n) == a - d
        for i in n:
            qs = SprayPoint.objects.filter(sprayday=i)
            if qs.count() > 1:
                qs.order_by('pk').first().delete()
