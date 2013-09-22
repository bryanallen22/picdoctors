Pd.JobsRoute = Ember.Route.extend({});

Pd.JobsNewJobsRoute = Ember.Route.extend({
  redirect: function(){
    window.location.replace("/new_jobs");
  }
});

Pd.JobsDocJobsRoute = Ember.Route.extend({
  redirect: function(){
    window.location.replace("/doc_jobs");
  }
});
