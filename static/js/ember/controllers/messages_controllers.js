Pd.MessagesController = Em.ObjectController.extend({
  needs:['application', 'album'],
  openCloseText: function(){
    return this.get('showingComments') ? 'Hide Comments' : 'Show Comments';
  }.property('showingComments'),
  commentsText: function(){
    var length = this.get('messages.length'),
    singular = length === 1,
    isAre = singular ? 'is' : 'are',
    comments = singular ? 'comment' : 'comments';

    return 'There ' + isAre + ' ' + length + ' ' + comments;
  }.property('messages.length'),
  showingComments: true,
  prettyFilename: function(){
    var filename = this.get('filename') || '',
        split = filename.split('\\'),
        len = split.length;
    return split[len-1];
  }.property('filename'),

  actions: {
    openClose: function(){
      this.toggleProperty('showingComments');
    },
    sendThatMessage: function(){
      var msg = this.get('newMessage'),
      me = this.get('controllers.application'),
      job = this.get('controllers.album.job'),
      self = this;

      if(Ember.isEmpty(msg)){
        return;
      }

      var newRecord = this.get('messages').createRecord({
        message:msg,
        commentor: me.get('nickname'),
        is_owner: true,
        created: 'Just Now',
        group: this.get('model'),
        job: job,
        file:'processing'
      });
      var formData = new FormData();

      formData.append('msg', msg);
      formData.append('file', this.get('file'));
      formData.append('group_id', this.get('model.id'));
      formData.append('job_id', job.get('id'));

      $.ajax({
        url: '/message_multipart_upload_handler/', 
        type: 'POST',
        //Ajax events
        success: function(data){
          self.set('newMessage', '');
          self.set('filename', undefined);
          self.set('file', undefined);
        },


        error: function(){ alert('Failure');},
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
      });

    },
    fileChange: function(e){
      var el = $(e.target);

      this.set('file', el[0].files[0]);
      this.set('filename', el.val());
    }
  }
});
