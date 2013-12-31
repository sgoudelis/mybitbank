# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'accountFilter'
        db.create_table(u'accounts_accountfilter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('entered', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'accounts', ['accountFilter'])

        # Adding model 'addressAliases'
        db.create_table(u'accounts_addressaliases', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('entered', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'accounts', ['addressAliases'])


    def backwards(self, orm):
        # Deleting model 'accountFilter'
        db.delete_table(u'accounts_accountfilter')

        # Deleting model 'addressAliases'
        db.delete_table(u'accounts_addressaliases')


    models = {
        u'accounts.accountfilter': {
            'Meta': {'object_name': 'accountFilter'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'entered': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        u'accounts.addressaliases': {
            'Meta': {'object_name': 'addressAliases'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'entered': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['accounts']