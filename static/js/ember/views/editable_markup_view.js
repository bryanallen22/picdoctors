Pd.EditableMarkupView= Ember.View.extend({
  templateName: 'markup_redx',

  mouseDown: function(e){
    if(e.which === 1){
      var controller = this.get('controller'),
          model = controller.get('model'),
          pic = model.get('pic'),
          store = controller.get('store');
      console.log('delete');
      model.deleteRecord();
      // if it was created this session, it's not automatically deleted
      // TODO figure out why the hell not
      pic.get('markups').removeObject(model);
      
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

