

Pd.Router.map(function(){
  this.route('signinToPay');
  this.resource('jobs', {path: 'jobs'}, function(){
    this.route('newJobs');
    this.route('docJobs');
    this.route('userJobs');
  });
  this.resource('albums' , { path: 'albums'}, function(){
    this.resource('album', { path: ':album_id'}, function(){
      this.route('pay');
      this.route('upload');
      this.route('markupEdit');
      this.route('markupView');
      this.resource('groups', {path: 'groups'}, function(){
        this.resource('group', {path: ':group_id'}, function(){
          this.resource('pics', {path: 'pics'}, function(){
            this.route('edit');
            this.route('view');
            this.resource('pic', {path: ':pic_id'}, function(){
              this.resource('markups', {path: 'markups'}, function(){
              });
            });
          });
        });
      });
    });
  });
  this.resource('settings', function(){
    this.route('profile');
    this.route('password');
    this.route('emailConfig');
    this.route('roles');
    this.route('bank_account');
    this.route('merchant_info');
  });
});

