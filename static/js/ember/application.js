window.Pd = Pd = Ember.Application.create({
  rootElement: '#ember-container',
  LOG_TRANSITIONS: !picDocProduction,
  staticUrl: picDocStaticUrl,
  token: $('input[name="csrfmiddlewaretoken"]').val(),
  stripe_oauth:'https://connect.stripe.com/oauth/authorize',
  href: window.location.href,
  getQueryParams: function()
  {
    if(this.queryParams){
      return this.queryParams;
    }
    var vars = [], hash;
    var hashes = this.href.slice(this.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    this.queryParams = vars;
    return vars;
  },
  getQueryParam: function(key){
     var params = this.getQueryParams();
     return params[key];
  }
});

// AKA don't start the app cause aint nothing to hook up to
if($('#ember-container').length==0){
  Pd.deferReadiness();
}

Pd.ApplicationAdapter = DS.RESTAdapter.extend({
  namespace: 'api'
});

// hack to inject the csrf token
// TODO probably should make sure this doesn't break anything else
jQuery(document).ajaxSend(function(event, xhr, settings) {
if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      var token = $('input[name="csrfmiddlewaretoken"]').val();
      xhr.setRequestHeader("X-CSRFToken", token);
    }
});
