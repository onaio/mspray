# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TargetArea'
        db.create_table('main_targetarea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('folder', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('main', ['TargetArea'])


    def backwards(self, orm):
        # Deleting model 'TargetArea'
        db.delete_table('main_targetarea')


    models = {
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