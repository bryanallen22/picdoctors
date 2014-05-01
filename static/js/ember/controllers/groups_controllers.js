Pd.GroupsController = Ember.ArrayController.extend({});

Pd.GroupController = Ember.ObjectController.extend({ });

Pd.GroupNavigationController = Ember.ObjectController.extend({
  needs:['application', 'album'],

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

  nextLabel: function(){
    var nextGroup = this.get('nextGroup'),
    finished = this.get('finished'),
    needsPay = this.get('needsPay'),
    needsSignIn = this.get('needsSignIn');

    if(nextGroup) return "Next";
    if(needsPay) return "Pay";
    if(needsSignIn) return "Sign In";
    if(finished) return "Jobs";
  }.property('nextGroup','finished', 'needsPay', 'needsSignIn'),

  needsPay: function(){
    var finished = this.get('finished'),
    isLoggedIn = this.get('isLoggedIn');
    return !finished && isLoggedIn;
  }.property('finished', 'isLoggedIn'),

  needsSignIn: function(){
    var finished = this.get('finished'),
    isLoggedIn = this.get('isLoggedIn');
    return !finished && !isLoggedIn;
  }.property('finished', 'isLoggedIn'),

  _previousGroup: null,

  previousGroup: function(){
    this.get('setupGroups');
    return this.get('_previousGroup');
  }.property('model', '_previousGroup'),

  previousLabel: function(){
    var previousGroup = this.get('previousGroup'),
    finished = this.get('finished');

    if(previousGroup) return "Previous";
    if(!finished) return "Upload";
    if(finished) return "Jobs";
  }.property('previousGroup', 'finished'),

  sameButtons: function(){
    return this.get('previousLabel') === this.get('nextLabel');
  }.property('previousLabel', 'nextLabel'),

  albumOwner: function(){
    var ownerId = this.get('album.owner'),
    userId = this.get('controllers.application.id');

    return (ownerId == userId) || (userId == -1 && ownerId == null);;
  }.property('album.owner', 'controllers.application.id'),

  albumDoctor: function(){
    var docId = this.get('album.doctor'),
    userId = this.get('controllers.application.id');

    return docId == userId;
  }.property('album.doctor', 'controllers.application.id'),

  isLoggedIn: function(){
    return this.get('controllers.application.isLoggedIn');
  }.property('controllers.application.isLoggedIn'),

  allPicsUploaded: function(){
    var ret = true,
        groups = this.get('album.groups');

    return groups.isEvery('hasDocPic');
  }.property('album.groups.@each.hasDocPic'),

  canFinishJob: Ember.computed.and('albumDoctor', 'allPicsUploaded', 'album.job.isDoctorAccepted'),

  actions:{
    completeJob: function(){
      var job = this.get('album.job');
      $.ajax({
        type:'POST',
        url:"/mark_job_completed/",
        data:{job_id:job.get('id')}
      }).then(function(results){
        var status = Em.get(results, 'job_info.status');
        if(status == 'Work Submitted, Pending Approval'){
          job.set('status', 'mod_need');
        } else if(status == 'Doctor Submitted, Pending Approval'){
          job.set('status', 'doctor_sub');
        }
      },function(){
        alert('there was an error marking the job as completed');
      });
    },

    next: function(){
      var nextGroup = this.get('nextGroup'),
      finished = this.get('finished'),
      needsPay = this.get('needsPay'),
      needsSignIn = this.get('needsSignIn'),
      albumDoctor = this.get('albumDoctor'),
      albumOwner = this.get('albumOwner');

      if(nextGroup && !finished) this.transitionToRoute('pics.edit', nextGroup);
      else if(nextGroup && finished) this.transitionToRoute('pics.view', nextGroup);
      else if(albumOwner){
        if(needsPay) this.transitionToRoute('album.pay');
        else if(needsSignIn) this.transitionToRoute('signinToPay');
        else if(finished) this.transitionToRoute('jobs.userJobs');
      } else if(albumDoctor) {
        if(finished) this.transitionToRoute('jobs.docJobs');
      } else if (!albumDoctor) {
        if(finished) this.transitionToRoute('jobs.newJobs');
      }

    },

    previous: function(){
      var previousGroup = this.get('previousGroup'),
      finished = this.get('finished'),
      albumDoctor = this.get('albumDoctor'),
      albumOwner = this.get('albumOwner');

      if(previousGroup && !finished) this.transitionToRoute('pics.edit', previousGroup);
      else if(previousGroup && finished) this.transitionToRoute('pics.view', previousGroup);
      else if (albumOwner){
        if(finished) this.transitionToRoute('jobs.userJobs');
        else this.transitionToRoute('album.upload');
      } else if (albumDoctor) {
        if(finished) this.transitionToRoute('jobs.docJobs');
      } else if(!albumDoctor) {
        if(finished) this.transitionToRoute('jobs.newJobs');
      }
    }

  }

});
