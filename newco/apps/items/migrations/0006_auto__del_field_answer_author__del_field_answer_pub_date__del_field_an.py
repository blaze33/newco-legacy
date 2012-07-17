# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Answer.author'
        db.delete_column('items_answer', 'author_id')

        # Deleting field 'Answer.pub_date'
        db.delete_column('items_answer', 'pub_date')

        # Deleting field 'Answer.id'
        db.delete_column('items_answer', 'id')


        # Renaming column for 'Answer.content_ptr' to match new field type.
        db.rename_column('items_answer', 'content_ptr', 'content_ptr_id')
        # Changing field 'Answer.content_ptr'
        db.alter_column('items_answer', 'content_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['items.Content'], unique=True, primary_key=True))
        # Adding index on 'Answer', fields ['content_ptr']
        db.create_index('items_answer', ['content_ptr_id'])

        # Adding unique constraint on 'Answer', fields ['content_ptr']
        db.create_unique('items_answer', ['content_ptr_id'])

        # Deleting field 'Question.author'
        db.delete_column('items_question', 'author_id')

        # Deleting field 'Question.pub_date'
        db.delete_column('items_question', 'pub_date')

        # Deleting field 'Question.id'
        db.delete_column('items_question', 'id')

        # Removing M2M table for field items on 'Question'
        db.delete_table('items_question_items')


        # Renaming column for 'Question.content_ptr' to match new field type.
        db.rename_column('items_question', 'content_ptr', 'content_ptr_id')
        # Changing field 'Question.content_ptr'
        db.alter_column('items_question', 'content_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['items.Content'], unique=True, primary_key=True))
        # Adding index on 'Question', fields ['content_ptr']
        db.create_index('items_question', ['content_ptr_id'])

        # Adding unique constraint on 'Question', fields ['content_ptr']
        db.create_unique('items_question', ['content_ptr_id'])

        # Deleting field 'ExternalLink.author'
        db.delete_column('items_externallink', 'author_id')

        # Deleting field 'ExternalLink.pub_date'
        db.delete_column('items_externallink', 'pub_date')

        # Deleting field 'ExternalLink.id'
        db.delete_column('items_externallink', 'id')

        # Removing M2M table for field items on 'ExternalLink'
        db.delete_table('items_externallink_items')


        # Renaming column for 'ExternalLink.content_ptr' to match new field type.
        db.rename_column('items_externallink', 'content_ptr', 'content_ptr_id')
        # Changing field 'ExternalLink.content_ptr'
        db.alter_column('items_externallink', 'content_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['items.Content'], unique=True, primary_key=True))
        # Adding index on 'ExternalLink', fields ['content_ptr']
        db.create_index('items_externallink', ['content_ptr_id'])

        # Adding unique constraint on 'ExternalLink', fields ['content_ptr']
        db.create_unique('items_externallink', ['content_ptr_id'])

        # Deleting field 'Feature.author'
        db.delete_column('items_feature', 'author_id')

        # Deleting field 'Feature.pub_date'
        db.delete_column('items_feature', 'pub_date')

        # Deleting field 'Feature.id'
        db.delete_column('items_feature', 'id')

        # Removing M2M table for field items on 'Feature'
        db.delete_table('items_feature_items')


        # Renaming column for 'Feature.content_ptr' to match new field type.
        db.rename_column('items_feature', 'content_ptr', 'content_ptr_id')
        # Changing field 'Feature.content_ptr'
        db.alter_column('items_feature', 'content_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['items.Content'], unique=True, primary_key=True))
        # Adding index on 'Feature', fields ['content_ptr']
        db.create_index('items_feature', ['content_ptr_id'])

        # Adding unique constraint on 'Feature', fields ['content_ptr']
        db.create_unique('items_feature', ['content_ptr_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Feature', fields ['content_ptr']
        db.delete_unique('items_feature', ['content_ptr_id'])

        # Removing index on 'Feature', fields ['content_ptr']
        db.delete_index('items_feature', ['content_ptr_id'])

        # Removing unique constraint on 'ExternalLink', fields ['content_ptr']
        db.delete_unique('items_externallink', ['content_ptr_id'])

        # Removing index on 'ExternalLink', fields ['content_ptr']
        db.delete_index('items_externallink', ['content_ptr_id'])

        # Removing unique constraint on 'Question', fields ['content_ptr']
        db.delete_unique('items_question', ['content_ptr_id'])

        # Removing index on 'Question', fields ['content_ptr']
        db.delete_index('items_question', ['content_ptr_id'])

        # Removing unique constraint on 'Answer', fields ['content_ptr']
        db.delete_unique('items_answer', ['content_ptr_id'])

        # Removing index on 'Answer', fields ['content_ptr']
        db.delete_index('items_answer', ['content_ptr_id'])

        # Adding field 'Answer.author'
        db.add_column('items_answer', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'Answer.pub_date'
        db.add_column('items_answer', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Answer.id'
        db.add_column('items_answer', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)


        # Renaming column for 'Answer.content_ptr' to match new field type.
        db.rename_column('items_answer', 'content_ptr_id', 'content_ptr')
        # Changing field 'Answer.content_ptr'
        db.alter_column('items_answer', 'content_ptr', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'Question.author'
        db.add_column('items_question', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'Question.pub_date'
        db.add_column('items_question', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Question.id'
        db.add_column('items_question', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding M2M table for field items on 'Question'
        db.create_table('items_question_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['items.question'], null=False)),
            ('item', models.ForeignKey(orm['items.item'], null=False))
        ))
        db.create_unique('items_question_items', ['question_id', 'item_id'])


        # Renaming column for 'Question.content_ptr' to match new field type.
        db.rename_column('items_question', 'content_ptr_id', 'content_ptr')
        # Changing field 'Question.content_ptr'
        db.alter_column('items_question', 'content_ptr', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'ExternalLink.author'
        db.add_column('items_externallink', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'ExternalLink.pub_date'
        db.add_column('items_externallink', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'ExternalLink.id'
        db.add_column('items_externallink', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding M2M table for field items on 'ExternalLink'
        db.create_table('items_externallink_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('externallink', models.ForeignKey(orm['items.externallink'], null=False)),
            ('item', models.ForeignKey(orm['items.item'], null=False))
        ))
        db.create_unique('items_externallink_items', ['externallink_id', 'item_id'])


        # Renaming column for 'ExternalLink.content_ptr' to match new field type.
        db.rename_column('items_externallink', 'content_ptr_id', 'content_ptr')
        # Changing field 'ExternalLink.content_ptr'
        db.alter_column('items_externallink', 'content_ptr', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'Feature.author'
        db.add_column('items_feature', 'author',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'Feature.pub_date'
        db.add_column('items_feature', 'pub_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Adding field 'Feature.id'
        db.add_column('items_feature', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding M2M table for field items on 'Feature'
        db.create_table('items_feature_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feature', models.ForeignKey(orm['items.feature'], null=False)),
            ('item', models.ForeignKey(orm['items.item'], null=False))
        ))
        db.create_unique('items_feature_items', ['feature_id', 'item_id'])


        # Renaming column for 'Feature.content_ptr' to match new field type.
        db.rename_column('items_feature', 'content_ptr_id', 'content_ptr')
        # Changing field 'Feature.content_ptr'
        db.alter_column('items_feature', 'content_ptr', self.gf('django.db.models.fields.IntegerField')())

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
            'Meta': {'object_name': 'Answer', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['items.Question']", 'null': 'True'}),
            'question_id_store': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'items.content': {
            'Meta': {'object_name': 'Content'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'items.externallink': {
            'Meta': {'object_name': 'ExternalLink', '_ormbases': ['items.Content']},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['items.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'items.feature': {
            'Meta': {'object_name': 'Feature', '_ormbases': ['items.Content']},
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
        'items.question': {
            'Meta': {'object_name': 'Question', '_ormbases': ['items.Content']},
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
