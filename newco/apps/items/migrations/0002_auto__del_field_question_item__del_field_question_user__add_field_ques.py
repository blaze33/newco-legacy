# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Question.item'
        db.delete_column('items_question', 'item_id')

        # Deleting field 'Question.user'
        db.delete_column('items_question', 'user_id')

        # Adding field 'Question.author'
        db.add_column('items_question', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding M2M table for field items on 'Question'
        db.create_table('items_question_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['items.question'], null=False)),
            ('item', models.ForeignKey(orm['items.item'], null=False))
        ))
        db.create_unique('items_question_items', ['question_id', 'item_id'])


        # Changing field 'Question.pub_date'
        db.alter_column('items_question', 'pub_date', self.gf('django.db.models.fields.DateTimeField')())
        # Deleting field 'Story.item'
        db.delete_column('items_story', 'item_id')

        # Deleting field 'Story.user'
        db.delete_column('items_story', 'user_id')

        # Deleting field 'Story.pub_date'
        db.delete_column('items_story', 'pub_date')

        # Adding M2M table for field items on 'Story'
        db.create_table('items_story_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('story', models.ForeignKey(orm['items.story'], null=False)),
            ('item', models.ForeignKey(orm['items.item'], null=False))
        ))
        db.create_unique('items_story_items', ['story_id', 'item_id'])

        # Deleting field 'Answer.user'
        db.delete_column('items_answer', 'user_id')

        # Adding field 'Answer.author'
        db.add_column('items_answer', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)


        # Changing field 'Answer.pub_date'
        db.alter_column('items_answer', 'pub_date', self.gf('django.db.models.fields.DateTimeField')())
        # Deleting field 'Item.user'
        db.delete_column('items_item', 'user_id')

        # Adding field 'Item.author'
        db.add_column('items_item', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'Item.pub_date'
        db.add_column('items_item', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 6, 8, 0, 0)),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'Question.item'
        db.add_column('items_question', 'item',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['items.Item'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Question.user'
        db.add_column('items_question', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Question.author'
        db.delete_column('items_question', 'author_id')

        # Removing M2M table for field items on 'Question'
        db.delete_table('items_question_items')


        # Changing field 'Question.pub_date'
        db.alter_column('items_question', 'pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))
        # Adding field 'Story.item'
        db.add_column('items_story', 'item',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['items.Item'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Story.user'
        db.add_column('items_story', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Story.pub_date'
        db.add_column('items_story', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 6, 8, 0, 0), blank=True),
                      keep_default=False)

        # Removing M2M table for field items on 'Story'
        db.delete_table('items_story_items')

        # Adding field 'Answer.user'
        db.add_column('items_answer', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Answer.author'
        db.delete_column('items_answer', 'author_id')


        # Changing field 'Answer.pub_date'
        db.alter_column('items_answer', 'pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))
        # Adding field 'Item.user'
        db.add_column('items_item', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Item.author'
        db.delete_column('items_item', 'author_id')

        # Deleting field 'Item.pub_date'
        db.delete_column('items_item', 'pub_date')

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
            'Meta': {'object_name': 'Answer'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 6, 8, 0, 0)'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['items.Question']", 'null': 'True'})
        },
        'items.item': {
            'Meta': {'object_name': 'Item'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 6, 8, 0, 0)'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'items.question': {
            'Meta': {'object_name': 'Question'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 6, 8, 0, 0)'})
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