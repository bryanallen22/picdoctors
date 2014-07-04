Ember.Handlebars.helper('upper', function(item){
  var txt = item || '';
  return txt.toUpperCase();
});

Ember.Handlebars.helper('capitalize', function(item){
  var txt = item || '';
  return txt.capitalize();
});

Ember.Handlebars.helper('static_img', function(image){
  var img = '<img src="' + Pd.staticUrl + image + '">';
  return Ember.Handlebars.SafeString(img); 
});
