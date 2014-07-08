

/*
 * Everybody wants this postTo thing, so I'm adding it globally. Don't sue me, I
 * think it actually is appropriate.
 */
window.postTo = function(url, obj, callback, errorCallback) {
  var CSRF_TOKEN = $('input[name=csrfmiddlewaretoken]').attr('value');
  $.ajax({
    headers: {
      "X-CSRFToken":CSRF_TOKEN
    },
    type: "POST",
    url: url,
    data: obj,
    success : callback,
    error : errorCallback
  });

};

window.CallHome= function(url, csrf, job_id){
      var json_data = JSON.stringify(
        {
          "job_id" : job_id,
        }
      );
      
      $.ajax({
        headers: {
          "X-CSRFToken":csrf
        },
        type: 'POST',
        url:  url,
        data: json_data,
        success : function(data, textStatus) {
          location.href = data.relocate;
        },

      });

};

