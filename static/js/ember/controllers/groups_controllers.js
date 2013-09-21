Pd.GroupsController = Ember.ArrayController.extend({});

Pd.GroupController = Ember.ObjectController.extend({});

Pd.GroupNavigationController = Ember.ObjectController.extend({
  needs:['application'],

  setupGroups: function(){
    var current = this.get('model'),
        currentIdx = 0,
        groups = current.get('album.groups'),
        len = groups.get('length'),
        next,
        previous = current;


    for(var i = 0; i<len; i++){
      var group = groups.objectAt(i);
      if(group === current){
        currentIdx = i;
        break;
      }    
    }

    this.set('_previousGroup', null);
    this.set('_nextGroup', null);

    if(currentIdx>0){
      this.set('_previousGroup', groups.objectAt(currentIdx-1));
    }

    if(currentIdx+1<len){
      this.set('_nextGroup', groups.objectAt(currentIdx+1));
    }
  }.property('model'),

  _nextGroup: null,
  
  nextGroup: function(){
    this.get('setupGroups');
    return this.get('_nextGroup');    
  }.property('model', '_nextGroup'),

  _previousGroup: null,

  previousGroup: function(){
    this.get('setupGroups');
    return this.get('_previousGroup');    
  }.property('model', '_previousGroup'),

  isLoggedIn: function(){
    return this.get('controllers.application.isLoggedIn');
  }.property('controllers.application.isLoggedIn')

});
