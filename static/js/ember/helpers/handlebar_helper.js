Ember.Handlebars.helper('upper', function(item){
  var txt = item || '';
  return txt.toUpperCase();
});

Ember.Handlebars.helper('capitalize', function(item){
  var txt = item || '';
  return txt.capitalize();
});
