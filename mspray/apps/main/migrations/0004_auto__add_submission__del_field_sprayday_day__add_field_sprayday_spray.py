# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Submission'
        db.create_table('main_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('main', ['Submission'])

        # Deleting field 'SprayDay.day'
        db.delete_column('main_sprayday', 'day')

        # Adding field 'SprayDay.spray_date'
        db.add_column('main_sprayday', 'spray_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 8, 8, 0, 0)),
                      keep_default=False)

        # Adding field 'SprayDay.submission'
        db.add_column('main_sprayday', 'submission',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=-1, to=orm['main.Submission']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Submission'
        db.delete_table('main_submission')

        # Adding field 'SprayDay.day'
        db.add_column('main_sprayday', 'day',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'SprayDay.spray_date'
        db.delete_column('main_sprayday', 'spray_date')

        # Deleting field 'SprayDay.submission'
        db.delete_column('main_sprayday', 'submission_id')


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
            'spray_date': ('django.db.models.fields.DateField', [], {}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Submission']"})
        },
        'main.submission': {
            'Meta': {'object_name': 'Submission'},
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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