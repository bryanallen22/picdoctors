window.Pd = Pd = Ember.Application.create({
  rootElement: '#ember-container',
  LOG_TRANSITIONS: true,
  rootUrl: picDocRootUrl
});

Pd.RestAdapter = DS.RESTAdapter.extend({
  namespace: 'api'
});

Pd.Store = DS.Store.extend({
  adapter: 'Pd.RestAdapter'
});

// hack to inject the csrf token
// TODO probably should make sure this doesn't break anything else
jQuery(document).ajaxSend(function(event, xhr, settings) {
if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      var token = $('input[name="csrfmiddlewaretoken"]').val();
      xhr.setRequestHeader("X-CSRFToken", token);
    }
});

