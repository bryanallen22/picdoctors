attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Group = DS.Model.extend({
  pics: hasMany('pic'),
  docPics: hasMany('docPic'),
  album: belongsTo('album')
});

Pd.Group.reopen({
  finished: function(){
    return this.get('album.finished');
  }.property('album.finished'),

  hasDocPics: function(){
    return !Ember.isEmpty(this.get('docPics'));
  }.property('docPics')
});
