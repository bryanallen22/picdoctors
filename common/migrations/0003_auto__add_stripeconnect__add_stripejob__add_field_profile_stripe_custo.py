# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StripeConnect'
        db.create_table(u'common_stripeconnect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('token_type', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('stripe_publishable_key', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('scope', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('livemode', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('stripe_user_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal(u'common', ['StripeConnect'])

        # Adding model 'StripeJob'
        db.create_table(u'common_stripejob', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('stripe_card_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cents', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('stripe_charge_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('hold_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('captured_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'common', ['StripeJob'])

        # Adding field 'Profile.stripe_customer_id'
        db.add_column(u'common_profile', 'stripe_customer_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Profile.stripe_connect'
        db.add_column(u'common_profile', 'stripe_connect',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['common.StripeConnect'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Job.stripe_job'
        db.add_column(u'common_job', 'stripe_job',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.StripeJob'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Job.bp_hold'
        db.alter_column(u'common_job', 'bp_hold_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPHold'], null=True))

    def backwards(self, orm):
        # Deleting model 'StripeConnect'
        db.delete_table(u'common_stripeconnect')

        # Deleting model 'StripeJob'
        db.delete_table(u'common_stripejob')

        # Deleting field 'Profile.stripe_customer_id'
        db.delete_column(u'common_profile', 'stripe_customer_id')

        # Deleting field 'Profile.stripe_connect'
        db.delete_column(u'common_profile', 'stripe_connect_id')

        # Deleting field 'Job.stripe_job'
        db.delete_column(u'common_job', 'stripe_job_id')


        # Changing field 'Job.bp_hold'
        db.alter_column(u'common_job', 'bp_hold_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['common.BPHold']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'common.album': {
            'Meta': {'object_name': 'Album'},
            'allow_publicly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'groups_last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_groups': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sequences_last_set': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Profile']", 'null': 'True', 'blank': 'True'})
        },
        u'common.bpaccount': {
            'Meta': {'object_name': 'BPAccount'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        u'common.bpcredit': {
            'Meta': {'object_name': 'BPCredit'},
            'cents': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        u'common.bpdebit': {
            'Meta': {'object_name': 'BPDebit'},
            'associated_credit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPCredit']", 'null': 'True', 'blank': 'True'}),
            'associated_hold': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPHold']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        u'common.bphold': {
            'Meta': {'object_name': 'BPHold'},
            'cents': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        u'common.docblock': {
            'Meta': {'object_name': 'DocBlock'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Job']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.docpicgroup': {
            'Meta': {'object_name': 'DocPicGroup'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc_pic_group'", 'to': u"orm['common.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Pic']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'watermark_pic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'watermark_pic'", 'to': u"orm['common.Pic']"})
        },
        u'common.docrating': {
            'Meta': {'object_name': 'DocRating'},
            'comments': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Job']"}),
            'overall_rating': ('django.db.models.fields.IntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.group': {
            'Meta': {'object_name': 'Group'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Album']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.job': {
            'Meta': {'object_name': 'Job'},
            'accepted_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Album']"}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bp_debit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPDebit']", 'null': 'True', 'blank': 'True'}),
            'bp_hold': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPHold']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'job_doctor'", 'null': 'True', 'to': u"orm['common.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore_last_doctor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'job_block_doctor'", 'null': 'True', 'to': u"orm['common.Profile']"}),
            'last_communicator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_communicator'", 'null': 'True', 'to': u"orm['common.Profile']"}),
            'payout_price_cents': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price_too_low_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'skaa': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'job_owner'", 'to': u"orm['common.Profile']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'in_market'", 'max_length': '15', 'db_index': 'True'}),
            'stripe_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.StripeJob']", 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.pic': {
            'Meta': {'object_name': 'Pic'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Album']", 'null': 'True', 'blank': 'True'}),
            'browser_group_id': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'original_height': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'original_width': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'path_owner': ('django.db.models.fields.CharField', [], {'default': "'user'", 'max_length': '16'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'preview_height': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'preview_width': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumb_height': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumb_width': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'watermark': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'common.pricetoolowcontributor': {
            'Meta': {'object_name': 'PriceTooLowContributor'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Job']"}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.profile': {
            'Meta': {'object_name': 'Profile'},
            'accepted_eula': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approval_pic_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'approval_pic_last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'auto_approve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bp_account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPAccount']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doc_profile_desc': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'fixed_payout_pct': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nickname': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Pic']", 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'stripe_connect': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['common.StripeConnect']", 'null': 'True', 'blank': 'True'}),
            'stripe_customer_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'common.stripeconnect': {
            'Meta': {'object_name': 'StripeConnect'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'livemode': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'stripe_publishable_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'stripe_user_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'token_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'common.stripejob': {
            'Meta': {'object_name': 'StripeJob'},
            'captured_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cents': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hold_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_card_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'stripe_charge_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']