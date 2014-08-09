# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Submission'
        db.delete_table('main_submission')

        # Deleting field 'SprayDay.submission'
        db.delete_column('main_sprayday', 'submission_id')


    def backwards(self, orm):
        # Adding model 'Submission'
        db.create_table('main_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('main', ['Submission'])

        # Adding field 'SprayDay.submission'
        db.add_column('main_sprayday', 'submission',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Submission'], default=-1),
                      keep_default=False)


    models = {
        'main.household': {
            'Meta': {'object_name': 'Household'},
            'bgeom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'blank': 'True', 'null': 'True'}),
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