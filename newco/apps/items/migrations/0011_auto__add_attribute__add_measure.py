# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Attribute'
        db.create_table('items_attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('items', ['Attribute'])

        # Adding model 'Measure'
        db.create_table('items_measure', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['items.Content'], unique=True, primary_key=True)),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['items.Attribute'])),
            ('data', self.gf('django_hstore.fields.DictionaryField')(db_index=True)),
        ))
        db.send_create_signal('items', ['Measure'])


    def backwards(self, orm):
        # Deleting model 'Attribute'
        db.delete_table('items_attribute')

        # Deleting model 'Measure'
        db.delete_table('items_measure')


    models = {
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
        'items.answer': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Answer', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['items.Question']", 'null': 'True'})
        },
        'items.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'items.content': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Content'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'})
        },
        'items.feature': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Feature', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'positive': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        'items.link': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Link', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'items.measure': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Measure', '_ormbases': ['items.Content']},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['items.Attribute']"}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'data': ('django_hstore.fields.DictionaryField', [], {'db_index': 'True'})
        },
        'items.question': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Question', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'})
        },
        'items.story': {
            'Meta': {'object_name': 'Story'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
        },
        'voting.vote': {
            'Meta': {'unique_together': "(('user', 'content_type', 'object_id'),)", 'object_name': 'Vote', 'db_table': "'votes'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.SmallIntegerField', [], {})
        }
    }

    complete_apps = ['items']