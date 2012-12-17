# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'AffiliationItem', fields ['item', 'object_id', 'store']
        db.delete_unique('affiliation_affiliationitem', ['item_id', 'object_id', 'store_id'])

        # Removing unique constraint on 'AffiliationItemCatalog', fields ['store', 'object_id']
        db.delete_unique('affiliation_affiliationitemcatalog', ['store_id', 'object_id'])

        # Deleting model 'AffiliationItemCatalog'
        db.delete_table('affiliation_affiliationitemcatalog')

        # Adding field 'AffiliationItem._shipping_price'
        db.add_column('affiliation_affiliationitem', '_shipping_price',
                      self.gf('django.db.models.fields.DecimalField')(default=-1, max_digits=14, decimal_places=2),
                      keep_default=False)

        # Adding field 'AffiliationItem._availability'
        db.add_column('affiliation_affiliationitem', '_availability',
                      self.gf('django.db.models.fields.CharField')(default='see site', max_length=50),
                      keep_default=False)

        # Adding unique constraint on 'AffiliationItem', fields ['object_id', 'store']
        db.create_unique('affiliation_affiliationitem', ['object_id', 'store_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'AffiliationItem', fields ['object_id', 'store']
        db.delete_unique('affiliation_affiliationitem', ['object_id', 'store_id'])

        # Adding model 'AffiliationItemCatalog'
        db.create_table('affiliation_affiliationitemcatalog', (
            ('ean', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('currency', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('img_medium', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('img_small', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('img_large', self.gf('django.db.models.fields.URLField')(max_length=1000)),
            ('object_id', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['affiliation.Store'])),
        ))
        db.send_create_signal('affiliation', ['AffiliationItemCatalog'])

        # Adding unique constraint on 'AffiliationItemCatalog', fields ['store', 'object_id']
        db.create_unique('affiliation_affiliationitemcatalog', ['store_id', 'object_id'])

        # Deleting field 'AffiliationItem._shipping_price'
        db.delete_column('affiliation_affiliationitem', '_shipping_price')

        # Deleting field 'AffiliationItem._availability'
        db.delete_column('affiliation_affiliationitem', '_availability')

        # Adding unique constraint on 'AffiliationItem', fields ['item', 'object_id', 'store']
        db.create_unique('affiliation_affiliationitem', ['item_id', 'object_id', 'store_id'])


    models = {
        'affiliation.affiliationitem': {
            'Meta': {'unique_together': "(('store', 'object_id'),)", 'object_name': 'AffiliationItem'},
            '_availability': ('django.db.models.fields.CharField', [], {'default': "'see site'", 'max_length': '50'}),
            '_shipping_price': ('django.db.models.fields.DecimalField', [], {'default': '-1', 'max_digits': '14', 'decimal_places': '2'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'currency': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'ean': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_large': ('django.db.models.fields.URLField', [], {'max_length': '1000'}),
            'img_medium': ('django.db.models.fields.URLField', [], {'max_length': '1000'}),
            'img_small': ('django.db.models.fields.URLField', [], {'max_length': '1000'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['items.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '2'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['affiliation.Store']"}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'affiliation.store': {
            'Meta': {'object_name': 'Store'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'items.item': {
            'Meta': {'object_name': 'Item'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['affiliation']