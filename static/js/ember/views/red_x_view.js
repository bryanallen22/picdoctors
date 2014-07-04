Pd.RedXView = Ember.View.extend({
  tagName: 'img',
  classNames: ['markup-redx'],
  attributeBindings: ['src'],
  src: function(){
    return Pd.staticUrl + "images/redx.png";
  }.property(),


  mouseDown: function(e){
    if(e.which === 1){
      var controller = this.get('controller'),
          model = controller.get('model'),
          pic = model.get('pic'),
          store = controller.get('store');
      model.deleteRecord();
      // if it was created this session, it's not automatically deleted
      // TODO figure out why the hell not
      if(pic) pic.get('markups').removeObject(model);
      
      model.save().then(function(){
        // worked
      },
      function(){
        // didn't work      
      });
    }

    //stop event from propogating up to the pic container
    return false;
  }


});

