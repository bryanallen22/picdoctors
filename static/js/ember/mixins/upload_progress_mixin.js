Pd.UploadProgress = Ember.Mixin.create({
  // it's important to note that current path lives on the application
  // controller, so this mixin can only live there
  showProgress: function(){
    var path = this.get('currentPath');
    switch(path){
      case 'albums.album.groups.group.pics.edit':
        this.set('uploadProgress', true);
        this.set('markupProgress', false);
        this.set('signinProgress', false);
        this.set('setPriceProgress', false);
        return true;
        break;
    }
    return false;
  }.property('currentPath'),

  bigArrows: function(){
    //arrowclass = "arrow_signin" if show_login else "arrow_nosignin"
    return this.get('isLoggedIn');
  }.property('isLoggedIn')




});
