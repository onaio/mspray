# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Household.bgeom'
        db.add_column('main_household', 'bgeom',
                      self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Household.bgeom'
        db.delete_column('main_household', 'bgeom')


    models = {
        'main.household': {
            'Meta': {'object_name': 'Household'},
            'bgeom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPointField', [], {}),
            'hh_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.sprayday': {
            'Meta': {'object_name': 'SprayDay'},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.targetarea': {
            'Meta': {'object_name': 'TargetArea'},
            'area_id': ('django.db.models.fields.IntegerField', [], {}),
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['main']