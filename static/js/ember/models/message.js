attr = DS.attr;
belongsTo = DS.belongsTo;
hasMany = DS.hasMany;

Pd.Message = DS.Model.extend({
  message: attr(),
  commentor: attr(),
  commentor_id:attr(),
  created: attr(),
  is_owner: attr(),
  group: belongsTo('group'),
  job: belongsTo('job'),
  attachment: attr(),

  prettyAttachmentName: function(){
    var attach = this.get('attachment') || '';
    if(!attach) return attach;

    var path = attach.split('/'),
        file = path[path.length-1],
        split = file.split('-'),
        len = split.length;


    // the server's file name is super important, or this won't work
    return split.splice(0, len-1).join('-');
  }.property('attachment')

});
