window.Pd = Pd = Ember.Application.create({
  rootElement: '#ember-container',
  LOG_TRANSITIONS: !picDocProduction,
  rootUrl: picDocRootUrl,
  token: $('input[name="csrfmiddlewaretoken"]').val()
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
