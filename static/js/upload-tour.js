$(function(){
  var tour = new Tour();

  tour.addStep({
    element: "#isocontainer", /* html element next to which the step popover should be shown */
    title: "Something", /* title of the popover */
    content: "Something" /* content of the popover */
  });

  tour.start();

});
