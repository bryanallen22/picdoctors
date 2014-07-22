// In all reality you would put each route in its own file, but this is just for fun
Pd.ApplicationRoute = Ember.Route.extend({
  model: function(){
    this.pushMarkupStyles();
    // I like the idea of the application model being the user
    // the user is the center of our universe
    return this.get('store').find('user', -1);
  },

  pushMarkupStyles: function(){
    var store = this.get('store');
    Pd.MarkupStyle.FIXTURE.forEach(function(ms){
      store.push('markupStyle', ms);
    });
  }
});

Pd.SigninToPayRoute = Ember.Route.extend({
  afterModel: function(model, transition){
    transition.abort();
    window.location.href = '/signin/?next=/set_price/';
  }
});
