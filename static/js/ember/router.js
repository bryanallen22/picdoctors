

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

