Pd.ApplicationController = Ember.ObjectController.extend({});

Pd.AlbumsController = Ember.ArrayController.extend({});
Pd.AlbumController = Ember.ObjectController.extend({});

Pd.GroupsController = Ember.ArrayController.extend({});
Pd.GroupController = Ember.ObjectController.extend({});

Pd.PicsController = Ember.ArrayController.extend({});
Pd.PicsEditController = Ember.ArrayController.extend({
  itemController: 'pic',
});

Pd.PicController = Ember.ObjectController.extend({
  picStyle: function(){
    var url = this.get('preview_url'),
        width = this.get('width'),
        height = this.get('height'),
        uuid = this.get('uuid'),
        backgroundStyle = "background: url('" + url + "');",
        style = "no-repeat;";

    style += backgroundStyle;
    style += "width:" + width + "px;";
    style += "height:" + height + "px;";

    return style;
  }.property('preview_url', 'width', 'height', 'uuid'),

});

Pd.MarkupsController = Ember.ObjectController.extend({});

