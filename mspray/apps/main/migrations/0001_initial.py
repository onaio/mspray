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
            ('hh_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('type_1', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('comment_1', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('descr', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('orig_fid', self.gf('django.db.models.fields.IntegerField')()),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPointField')()),
            ('bgeom', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['Household'])

        # Adding model 'TargetArea'
        db.create_table('main_targetarea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('houses', self.gf('django.db.models.fields.FloatField')()),
            ('targetid', self.gf('django.db.models.fields.FloatField')()),
            ('predicted', self.gf('django.db.models.fields.FloatField')()),
            ('predinc', self.gf('django.db.models.fields.FloatField')()),
            ('ranks', self.gf('django.db.models.fields.FloatField')()),
            ('houseranks', self.gf('django.db.models.fields.FloatField')()),
            ('targeted', self.gf('django.db.models.fields.FloatField')()),
            ('district_name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('main', ['TargetArea'])

        # Adding model 'HouseholdsBuffer'
        db.create_table('main_householdsbuffer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target_area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.TargetArea'])),
            ('num_households', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
        ))
        db.send_create_signal('main', ['HouseholdsBuffer'])

        # Adding model 'SprayDay'
        db.create_table('main_sprayday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spray_date', self.gf('django.db.models.fields.DateField')()),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('main', ['SprayDay'])


    def backwards(self, orm):
        # Deleting model 'Household'
        db.delete_table('main_household')

        # Deleting model 'TargetArea'
        db.delete_table('main_targetarea')

        # Deleting model 'HouseholdsBuffer'
        db.delete_table('main_householdsbuffer')

        # Deleting model 'SprayDay'
        db.delete_table('main_sprayday')


    models = {
        'main.household': {
            'Meta': {'object_name': 'Household'},
            'bgeom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'comment_1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'descr': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPointField', [], {}),
            'hh_id': ('django.db.models.fields.IntegerField', [], {}),
            'hh_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'orig_fid': ('django.db.models.fields.IntegerField', [], {}),
            'type_1': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'main.householdsbuffer': {
            'Meta': {'object_name': 'HouseholdsBuffer'},
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_households': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TargetArea']"})
        },
        'main.sprayday': {
            'Meta': {'object_name': 'SprayDay'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spray_date': ('django.db.models.fields.DateField', [], {})
        },
        'main.targetarea': {
            'Meta': {'object_name': 'TargetArea'},
            'district_name': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'houseranks': ('django.db.models.fields.FloatField', [], {}),
            'houses': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'predicted': ('django.db.models.fields.FloatField', [], {}),
            'predinc': ('django.db.models.fields.FloatField', [], {}),
            'ranks': ('django.db.models.fields.FloatField', [], {}),
            'targeted': ('django.db.models.fields.FloatField', [], {}),
            'targetid': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['main']