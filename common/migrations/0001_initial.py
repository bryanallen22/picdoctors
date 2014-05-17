# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BPAccount'
        db.create_table(u'common_bpaccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal(u'common', ['BPAccount'])

        # Adding model 'BPHold'
        db.create_table(u'common_bphold', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('cents', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'common', ['BPHold'])

        # Adding model 'BPCredit'
        db.create_table(u'common_bpcredit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('cents', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'common', ['BPCredit'])

        # Adding model 'BPDebit'
        db.create_table(u'common_bpdebit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('associated_hold', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPHold'])),
            ('associated_credit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPCredit'], null=True, blank=True)),
        ))
        db.send_create_signal(u'common', ['BPDebit'])

        # Adding model 'Profile'
        db.create_table(u'common_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255, db_index=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(db_index=True, unique=True, max_length=32, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('accepted_eula', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bp_account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPAccount'], null=True, blank=True)),
            ('auto_approve', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rating', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('approval_pic_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('approval_pic_last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Pic'], null=True, blank=True)),
            ('doc_profile_desc', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'common', ['Profile'])

        # Adding M2M table for field groups on 'Profile'
        db.create_table(u'common_profile_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'common.profile'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'common_profile_groups', ['profile_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Profile'
        db.create_table(u'common_profile_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'common.profile'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'common_profile_user_permissions', ['profile_id', 'permission_id'])

        # Adding model 'Pic'
        db.create_table(u'common_pic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Album'], null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('browser_group_id', self.gf('django.db.models.fields.IntegerField')(default=100000)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Group'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('original', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('preview', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('path_owner', self.gf('django.db.models.fields.CharField')(default='user', max_length=16)),
            ('watermark', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('original_width', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('original_height', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('preview_width', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('preview_height', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('thumb_width', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('thumb_height', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'common', ['Pic'])

        # Adding model 'Album'
        db.create_table(u'common_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Profile'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('num_groups', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('groups_last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sequences_last_set', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('allow_publicly', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'common', ['Album'])

        # Adding model 'Group'
        db.create_table(u'common_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Album'])),
            ('is_locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'common', ['Group'])

        # Adding model 'DocPicGroup'
        db.create_table(u'common_docpicgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='doc_pic_group', to=orm['common.Group'])),
            ('pic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Pic'])),
            ('watermark_pic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='watermark_pic', to=orm['common.Pic'])),
        ))
        db.send_create_signal(u'common', ['DocPicGroup'])

        # Adding model 'Job'
        db.create_table(u'common_job', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Album'])),
            ('skaa', self.gf('django.db.models.fields.related.ForeignKey')(related_name='job_owner', to=orm['common.Profile'])),
            ('doctor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='job_doctor', null=True, to=orm['common.Profile'])),
            ('ignore_last_doctor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='job_block_doctor', null=True, to=orm['common.Profile'])),
            ('payout_price_cents', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('price_too_low_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bp_hold', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPHold'])),
            ('bp_debit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.BPDebit'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='in_market', max_length=15, db_index=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_communicator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_communicator', null=True, to=orm['common.Profile'])),
            ('accepted_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'common', ['Job'])

        # Adding model 'PriceTooLowContributor'
        db.create_table(u'common_pricetoolowcontributor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Job'])),
            ('doctor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Profile'])),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'common', ['PriceTooLowContributor'])

        # Adding model 'DocBlock'
        db.create_table(u'common_docblock', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Job'])),
            ('doctor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Profile'])),
        ))
        db.send_create_signal(u'common', ['DocBlock'])

        # Adding model 'DocRating'
        db.create_table(u'common_docrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 1, 0, 0), auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('doctor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Profile'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Job'])),
            ('overall_rating', self.gf('django.db.models.fields.IntegerField')()),
            ('comments', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'common', ['DocRating'])


    def backwards(self, orm):
        # Deleting model 'BPAccount'
        db.delete_table(u'common_bpaccount')

        # Deleting model 'BPHold'
        db.delete_table(u'common_bphold')

        # Deleting model 'BPCredit'
        db.delete_table(u'common_bpcredit')

        # Deleting model 'BPDebit'
        db.delete_table(u'common_bpdebit')

        # Deleting model 'Profile'
        db.delete_table(u'common_profile')

        # Removing M2M table for field groups on 'Profile'
        db.delete_table('common_profile_groups')

        # Removing M2M table for field user_permissions on 'Profile'
        db.delete_table('common_profile_user_permissions')

        # Deleting model 'Pic'
        db.delete_table(u'common_pic')

        # Deleting model 'Album'
        db.delete_table(u'common_album')

        # Deleting model 'Group'
        db.delete_table(u'common_group')

        # Deleting model 'DocPicGroup'
        db.delete_table(u'common_docpicgroup')

        # Deleting model 'Job'
        db.delete_table(u'common_job')

        # Deleting model 'PriceTooLowContributor'
        db.delete_table(u'common_pricetoolowcontributor')

        # Deleting model 'DocBlock'
        db.delete_table(u'common_docblock')

        # Deleting model 'DocRating'
        db.delete_table(u'common_docrating')


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
            'bp_hold': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.BPHold']"}),
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nickname': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Pic']", 'null': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
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