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
  description: attr(),
  created: attr()
});

Pd.Pic.reopen({
  
  finished: function(){
    var finished = this.get('group.finished');
    if(Ember.isEmpty(finished)) return true;
    return finished;
  }.property('group.finished'),

  formattedCreated: function(){
    // TODO created doesn't exist in the definition
    // so fix that at some point
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

  /*  Do not, under any circumstances, change the padding or margin of  
       this .markup_pic_container or .pic unless you are 200% certain    
       that you aren't messing things up. Careful calculation of offsets 
       for drawing markups at the right location is done, and if you     
       change them, old markups might appear at the wrong spot */
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

