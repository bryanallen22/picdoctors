
String.prototype.pluralize = function(count, plural)
{
    if (plural == null)
          plural = this + 's';

      return (count == 1 ? this : plural)
}


Number.prototype.padLeft = function(n,str){
      return Array(n-String(this).length+1).join(str||'0')+this;
}

