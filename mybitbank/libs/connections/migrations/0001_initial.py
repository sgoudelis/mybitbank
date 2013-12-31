# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CurrencyService'
        db.create_table(u'connections_currencyservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rpcusername', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rpcpassword', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rpchost', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('rpcport', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('entered', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'connections', ['CurrencyService'])


    def backwards(self, orm):
        # Deleting model 'CurrencyService'
        db.delete_table(u'connections_currencyservice')


    models = {
        u'connections.currencyservice': {
            'Meta': {'object_name': 'CurrencyService'},
            'entered': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rpchost': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rpcpassword': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rpcport': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rpcusername': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['connections']