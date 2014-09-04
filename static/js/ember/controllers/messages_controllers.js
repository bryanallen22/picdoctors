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
        job: job
      });

      newRecord.save().then(function(){
        self.set('newMessage', '');
        self.set('file', undefined);
      });
    },
    fileChange: function(e){
      this.set('file', $(e.target).val());
    }
  }
});
