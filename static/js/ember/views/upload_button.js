Pd.UploadButton = Ember.View.extend({
  tagName: 'input',
  attributeBindings: ['type'],
  type: 'file',
  originalText: 'Upload Finished Product',
  uploadingText: 'Busy Uploading...',

  newPicHandler: function(data){
    var store = this.get('controller.store'),
        group = this.get('controller.model.docPicGroups');

    // there has got to be some way to hook this up
    // using ember data, without having to manually sideload it piece
    // by piece
    var dpg = data.docPicGroup,
        pics = data.pics;

    // remove the group, and manually add later
    // for some reason it knows its parent when we create the
    // record below, but the parent doesn't know it
    // (some sort of lazy load from the parent's point of view)
    // and then when I try and insert it into the parent at 0
    // it gets confused, and removes it from its old parent (at 0)
    // and rejoins at the end of the list...
    // I might just do an ordered computed property version of the doc pics
    // then I wouldn't have to worry about all of that
    delete dpg.group;

    pics.forEach(function(pic){
      store.push('pic', pic);
    });

    var dp = store.push('docPicGroup', dpg);

    group.insertAt(0, dp);
  },

  textSpan: function(){
    return $('#doc_upload_text');
  }.property(),

  preUpload: function(){
    var me = this.$(),
        textSpan = this.get('textSpan'),
        parent = me.closest('.fileupload-addbutton'),
        upload = this.get('uploadingText');

      parent.addClass('disabled');
      textSpan.text(upload);
      me.css('cursor', 'default');
      me.attr('disabled', 'disabled');
  },

  postUpload: function(){
    var me = this.$(),
        textSpan = this.get('textSpan'),
        parent = me.closest('.fileupload-addbutton'),
        form = parent.closest('#fake_form_for_reset')[0],
        orig = this.get('originalText');

      parent.removeClass('disabled');
      textSpan.text(orig);
      me.css('cursor', 'pointer');
      me.removeAttr('disabled');
      form.reset();
  },

  change: function(e){
    var self = this;
    var formData = new FormData();
    this.preUpload();
    formData.append('group_id', this.get('group.id'));
    formData.append('doc_file', this.$().get(0).files[0]);
    $.ajax({
      url: '/doc_upload_handler/', 
      type: 'POST',
      //Ajax events
      success: function(data){ self.postUpload(); self.newPicHandler(data);},
      error: function(){ self.postUpload(); alert('Failure');},
      // Form data
      data: formData,
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });
  }
});
