attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.DocPicGroup = DS.Model.extend({
  group: belongsTo('group'),
  // this doesn't necessarily get sent down
  pic: belongsTo('pic'),
  watermark_pic: belongsTo('pic')
});

