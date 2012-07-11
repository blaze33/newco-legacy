# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # Create content object with author and pub date and pasting its id into specially created parent_id attribute
        ct_model = orm['items.Content']
        for model in [orm['items.Question'], orm['items.Answer'], orm['items.ExternalLink'], orm['items.Feature']]:
            for obj in model.objects.all():
                ct = ct_model(author=obj.author, pub_date=obj.pub_date)
                ct.save()
                obj.content_ptr = ct.id
                obj.save()
                if hasattr(obj, "items"):
                    ct.items = obj.items.all()
                elif model==orm['items.Answer']:
                    obj.question_id_store = orm['items.Question'].objects.get(id=obj.question.id).content_ptr
                    obj.save()
                    ct.items = obj.question.items.all()

        # Then switch votes object_id to future one in two steps to avoid collision
        for vote in orm['voting.Vote'].objects.all():
            if vote.content_type.model in ["question", "answer", "externallink", "feature"]:
                model = orm['items.' + vote.content_type.model.capitalize()]
                obj = model.objects.get(pk=vote.object_id)
                vote.object_id = obj.content_ptr + 500000
                vote.save()

        for vote in orm['voting.Vote'].objects.all():
            vote.object_id -= 500000
            vote.save()

    def backwards(self, orm):
        # Rebuild unique ids + author + pub_date + m2m
        for model in [orm['items.Question'], orm['items.Answer'], orm['items.ExternalLink'], orm['items.Feature']]:
            for obj in model.objects.all():
                if obj.id == 0:
                    obj.id = obj.content_ptr
                    obj.save()
                if not obj.author:
                    ct = orm["items.Content"].object.get(pk=obj.content_ptr)
                    obj.author = ct.author
                    obj.pub_date = ct.pub_date
                    obj.save()
                if hasattr(obj,"items"):
                    if obj.items.count() == 0:
                        for item in ct.items.all():
                            obj.items.add(item)

        # Back-switch vote from content to object
        for vote in orm['voting.Vote'].objects.all():
            if vote.content_type.model == "content":
                ct = orm["items.Content"].objects.get(pk=vote.object_id)
                for model in [orm['items.Question'], orm['items.Answer'], orm['items.ExternalLink'], orm['items.Feature']]:
                    if model.objects.filter(content_ptr=ct.id).count() == 1:
                        obj = model.objects.filter(content_ptr=ct.id)[0]
                        content_type = orm['contenttypes.ContentType'].objects.get(app_label="items", model=model.__name__.lower())
                        vote.content_type = content_type
                        vote.object_id = obj.id
                        vote.save()
                        break

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
            'content_ptr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
            'Meta': {'object_name': 'ExternalLink'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_ptr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'items.feature': {
            'Meta': {'object_name': 'Feature'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'content_ptr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'positive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
            'Meta': {'object_name': 'Question'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_ptr': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['items.Item']", 'symmetrical': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
    symmetrical = True
