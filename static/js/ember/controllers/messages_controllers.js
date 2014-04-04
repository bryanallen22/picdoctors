Pd.MessagesController = Em.ArrayController.extend({
  openCloseText: function(){
    return this.get('showingComments') ? 'Hide Comments' : 'Show Comments';
  }.property('showingComments'),
  commentsText: function(){
    var length = this.get('length'),
        singular = length === 1,
        isAre = singular ? 'is' : 'are',
        comments = singular ? 'comment' : 'comments';

    return 'There ' + isAre + ' ' + length + ' ' + comments;
  }.property('length'),
  showingComments: false,

  actions: {
    openClose: function(){
      this.toggleProperty('showingComments');

    }

  }

});
