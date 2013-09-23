Pd.PicsRoute = Ember.Route.extend({
  model: function(params){
    var store = this.get('store'),
        self = this;
    // the pics model is embedded in the group
    var pics = this.modelFor('group').get('pics');
    pics.forEach(function(pic){
      var markups = pic.get('markups');
      self.setupMarkups(markups, store, true);
      markups.addArrayObserver(self, { willChange: self.markupsWillChange, didChange: self.markupChanged });
    });
    return pics;
  },

  markupsWillChange: function(){  },

  markupChanged: function(observedObject, idx, removeCount, addCount){
    this.setupMarkups(observedObject, this.get('store'), false);
  },

  setupMarkups: function(markups, store, selectAll){
    // this could easily change to not reset them on delete, but
    // this is a more realistic view of what they'll see if they refresh
      for(var i = 0,len = markups.get('length'); i< len;i++){
        var markup = markups.objectAt(i);
        if(selectAll) markup.set('selected', true);
        markup.set('markupStyle', store.find('markupStyle', i+1));
      }
  }

});

Pd.PicsEditRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pics');
  }
});

Pd.PicsViewRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pics');
  }
});

Pd.PicRoute = Ember.Route.extend({
  model: function(params){
    return this.modelFor('pics').findProperty('id', params.pic_id);
  }

});
