
attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.User = DS.Model.extend({
  nickname: attr(),
  email: attr(),
});

Pd.Album = DS.Model.extend({
  groups: hasMany('group'),
});

Pd.Group = DS.Model.extend({
  pics: hasMany('pic'),
  album: belongsTo('album')
});

Pd.Pic = DS.Model.extend({
  group: belongsTo('group'),
  markups: hasMany('markup'),
  general_instructions: attr(),
  preview_url: attr(),
  width: attr(),
  height: attr()
});

Pd.Markup = DS.Model.extend({
  pic: belongsTo('pic'),

  border_style: attr(),
  color: attr(),
  color_name: attr(),
  description: attr(),
  height: attr(),
  left: attr(),
  pic: attr(),
  top: attr(),
  width: attr()

});
