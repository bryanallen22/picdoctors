Pd.MessagesController = Em.ArrayController.extend({
  openCloseText: function(){
    return this.get('showingComments') ? 'Hide Comments' : 'Show Comments';
  }.property('showingComments'),
  showingComments: false,

  actions: {
    openClose: function(){
      this.toggleProperty('showingComments');

    }

  }

});
