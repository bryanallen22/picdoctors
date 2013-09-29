Pd.DocPicsController = Ember.ArrayController.extend({
  itemController: 'docPicGroup'
});

Pd.DocPicGroupController = Ember.ObjectController.extend({
  needs:['album'],

  isAlbumOwner: function(){
    return this.get('controllers.album.isAlbumOwner');
  }.property('controllers.album.isAlbumOwner'),

  isAlbumDoctor: function(){
    return this.get('controllers.album.isAlbumDoctor');
  }.property('controllers.album.isAlbumDoctor'),

  visiblePic: function(){
    return this.get('pic');
  }.property('pic', 'watermark_pic'),

  picStyle: function(){
    return this.get('visiblePic.picStyle');
  }.property('visiblePic'),

});
