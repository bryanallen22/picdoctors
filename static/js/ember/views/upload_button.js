Pd.UploadButton = Ember.View.extend({
  templateName: '_doc_upload_button',
  didInsertElement: function() {
    var self = this;

    // todo figure out how to monitor this with ember
    $('#doc_file').change( function(e){ self.doc_upload(self,e)} );
    this._super();
  },

  doc_upload : function(self, e) {
    // TODO disable button, change text, upload the docPics in the group
    // TODO this actually worked on the first attempt, I get to quit
    // for the night!!!!
    var formData = new FormData();
    formData.append('group_id', self.get('group.id'));
    formData.append('doc_file', $('#doc_file').get(0).files[0]);
    $.ajax({
        url: '/doc_upload_handler/', 
        type: 'POST',
        //Ajax events
        success: function(data){ self.newPicHandler(data);},
        error: function(){ alert('uhoh');},
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });
  },

  newPicHandler: function(data){
    var store = this.get('controller.store'),
        group = this.get('controller.model');

    store.push('docPic', data);
    var dp = store.find('docPic', data.id);
    group.get('docPics').insertAt(0, dp);

  }

});
