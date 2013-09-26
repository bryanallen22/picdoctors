attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.BasePic = DS.Model.extend({
  preview_url: attr(),
  original_url: attr(),
  width: attr(),
  height: attr()
});

Pd.BasePic.reopen({
  finished: function(){
    return this.get('group.finished');
  }.property('group.finished'),
});

Pd.Pic = Pd.BasePic.extend({
  group: belongsTo('group'),
  markups: hasMany('markup'),
  description: attr()
});

Pd.Pic.reopen({
  deselectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', false);
    });
  },

  selectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', true);
    });
  }
});

Pd.DocPic = Pd.BasePic.extend({
  group: belongsTo('group'),
  created: attr()
});

Pd.DocPic.reopen({
  downloadName: function(){
    var url = this.get('original_url'),
        filename = url.split('/').pop(),
        extension = filename.split('.').pop(),
        name = 'DoctorPic-' + filename.substring(0,5) + "." + extension;
    return name;
  }.property('original_url'),

  formattedCreated: function(){
    var created = moment(this.get('created'));
    return created.calendar();
  }.property('created')
});
