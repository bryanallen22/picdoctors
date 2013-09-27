attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Pic = DS.Model.extend({
  preview_url: attr(),
  original_url: attr(),
  width: attr(),
  height: attr(),
  group: belongsTo('group'),
  markups: hasMany('markup'),
  description: attr()
});

Pd.Pic.reopen({
  
  finished: function(){
    return this.get('group.finished') || true;
  }.property('group.finished'),

  formattedCreated: function(){
    var created = moment(this.get('created'));
    return created.calendar();
  }.property('created'),

  downloadName: function(){
    var url = this.get('original_url'),
        filename = url.split('/').pop(),
        extension = filename.split('.').pop(),
        name = 'Pic-' + filename.substring(0,5) + "." + extension;
    return name;
  }.property('original_url'),

  deselectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', false);
    });
  },

  selectAllMarkups: function(){
    this.get('markups').forEach(function(markup){
      markup.set('selected', true);
    });
  },

  picStyle: function(){
    var url = this.get('preview_url'),
        width = this.get('width'),
        height = this.get('height'),
        uuid = this.get('uuid'),
        backgroundStyle = "background: url('" + url + "');",
        finished = this.get('finished'),
        style = "no-repeat;";

    if(!finished) style += "cursor: crosshair;";

    style += backgroundStyle;
    style += "width:" + width + "px;";
    style += "height:" + height + "px;";

    return style;
  }.property('preview_url', 'width', 'height', 'uuid', 'finished'),

});

