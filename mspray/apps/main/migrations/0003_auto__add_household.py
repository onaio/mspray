# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Household'
        db.create_table('main_household', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hh_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('folder', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPointField')()),
        ))
        db.send_create_signal('main', ['Household'])


    def backwards(self, orm):
        # Deleting model 'Household'
        db.delete_table('main_household')


    models = {
        'main.household': {
            'Meta': {'object_name': 'Household'},
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPointField', [], {}),
            'hh_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
