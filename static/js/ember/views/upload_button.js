Pd.UploadButton = Ember.View.extend({
  tagName: 'input',
  attributeBindings: ['type'],
  type: 'file',
  originalText: 'Upload Finished Product',
  uploadingText: 'Busy Uploading...',

  newPicHandler: function(data){
    var store = this.get('controller.store'),
    group = this.get('controller.model');

    // create the association from the group, (so I can insert him at the top)
    delete data.group;

    var docPic = store.createRecord('docPic', data);
    group.get('docPics').insertAt(0, docPic); 
  },

  textSpan: function(){
    return $('#doc_upload_text');
  }.property(),

  preUpload: function(){
    var me = this.$(),
        textSpan = this.get('textSpan'),
        parent = me.parent(),
        upload = this.get('uploadingText');

      parent.addClass('disabled');
      textSpan.text(upload);
      me.css('cursor', 'default');
      me.attr('disabled', 'disabled');
  },

  postUpload: function(){
    var me = this.$(),
        textSpan = this.get('textSpan'),
        parent = me.parent(),
        orig = this.get('originalText');

      parent.removeClass('disabled');
      textSpan.text(orig);
      me.css('cursor', 'pointer');
      me.removeAttr('disabled');
  },

  change: function(e){
    var self = this;
    // TODO disable button, change text, upload the docPics in the group
    // TODO this actually worked on the first attempt, I get to quit
    // for the night!!!!
    var formData = new FormData();
    this.preUpload();
    formData.append('group_id', this.get('group.id'));
    formData.append('doc_file', this.$().get(0).files[0]);
    $.ajax({
      url: '/doc_upload_handler/', 
      type: 'POST',
      //Ajax events
      success: function(data){ self.postUpload(); self.newPicHandler(data);},
      error: function(){ self.postUpload(); alert('uhoh');},
      // Form data
      data: formData,
      //Options to tell jQuery not to process data or worry about content-type.
      cache: false,
      contentType: false,
      processData: false
    });


  }

});
