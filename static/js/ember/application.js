window.Pd = Pd = Ember.Application.create({
  rootElement: '#ember-container',
  LOG_TRANSITIONS: true
});

Pd.RestAdapter = DS.RESTAdapter.extend({
  namespace: 'api'
});

Pd.Store = DS.Store.extend({
  adapter: 'Pd.RestAdapter'
});

jQuery(document).ajaxSend(function(event, xhr, settings) {
if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
      var token = $('input[name="csrfmiddlewaretoken"]').val();
      xhr.setRequestHeader("X-CSRFToken", token);
    }
  });


Pd.Router.map(function(){
  this.route('signinToPay');
  this.resource('albums' , { path: 'albums'}, function(){
    this.resource('album', { path: ':album_id'}, function(){
      this.route('pay');
      this.route('upload');
      this.resource('groups', {path: 'groups'}, function(){
        this.resource('group', {path: ':group_id'}, function(){
          this.resource('pics', {path: 'pics'}, function(){
            this.route('edit');
            this.resource('pic', {path: ':pic_id'}, function(){
              this.resource('markups', {path: 'markups'}, function(){
              });
            });
          });
        });
      });
    });
  });
});

