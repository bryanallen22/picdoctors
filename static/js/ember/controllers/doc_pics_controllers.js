Pd.DocPicsController = Ember.ArrayController.extend({
  itemController: 'docPicGroup'
});

Pd.DocPicGroupController = Ember.ObjectController.extend({
  needs:['album'],

  isAlbumOwner: Em.computed.alias('controllers.album.isAlbumOwner'),

  isAlbumDoctor: Em.computed.alias('controllers.album.isAlbumDoctor'),

  pic: function(){
    /* Get the 'pic' if it's available, but it might not be if the user hasn't paid yet.
     * In that case, grab 'watermark_pic' */
    return this.get('model.pic') || this.get('model.watermark_pic');
  }.property('model.pic', 'model.watermark_pic'),

  picStyle: function(){
    return this.get('pic.picStyle');
  }.property('pic'),

});
