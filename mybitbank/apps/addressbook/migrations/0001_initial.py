# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'savedAddress'
        db.create_table(u'addressbook_savedaddress', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('entered', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'addressbook', ['savedAddress'])


    def backwards(self, orm):
        # Deleting model 'savedAddress'
        db.delete_table(u'addressbook_savedaddress')


    models = {
        u'addressbook.savedaddress': {
            'Meta': {'object_name': 'savedAddress'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'entered': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['addressbook']