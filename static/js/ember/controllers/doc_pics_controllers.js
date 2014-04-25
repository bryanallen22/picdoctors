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
    /* Get the 'pic' if it's available, but it might not be if the user hasn't paid yet.
     * In that case, grab 'watermark_pic' */
    return this.get('pic') || this.get('watermark_pic');
  }.property('pic', 'watermark_pic'),

  picStyle: function(){
    return this.get('visiblePic.picStyle');
  }.property('visiblePic'),

});
