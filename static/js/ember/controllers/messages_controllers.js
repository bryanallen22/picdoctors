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

  clearAttachment: function(){
    this.set('filename', undefined);
    this.set('file', undefined);
  },

  actions: {
    openClose: function(){
      this.toggleProperty('showingComments');
    },
    sendThatMessage: function(){
      var msg = this.get('newMessage'),
      me = this.get('controllers.application'),
      job = this.get('controllers.album.job'),
      self = this,
      success, failure;

      success = function(data){
        var record=self.store.push('message', data.message);
        self.get('messages').pushObject(record);

        self.set('newMessage', '');
        self.set('sending', false);
        self.clearAttachment();
      };

      failure = function(){
        alert('failed');
      };

      if(Ember.isEmpty(msg)){
        return;
      }

      var formData = new FormData();

      formData.append('msg', msg);
      formData.append('file', this.get('file'));
      formData.append('group_id', this.get('model.id'));
      formData.append('job_id', job.get('id'));

      this.set('sending', true);

      $.ajax({
        url: '/api/messages', 
        type: 'POST',
        //Ajax events
        success:success,
        error: function(){ alert('Failure');},
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
      });

    },
    removeAttachment: function(){
      this.clearAttachment();
    },
    fileChange: function(e){
      var el = $(e.target);

      this.set('file', el[0].files[0]);
      this.set('filename', el.val());
    }
  }
});
