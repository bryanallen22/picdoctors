$(function(){
  //globalize 
  var tour = new Tour();

  tour.addStep({
    element: "#isocontainer", /* html element next to which the step popover should be shown */
    title: "Add Pictures", /* title of the popover */
    content: "First we need to add some pictures.  Drag from your desktop or a folder to this box." /* content of the popover */
  });

  tour.addStep({
    element: ".fileupload-addbutton", 
    title: "Add Pictures", 
    content: "Or click here to choose your files using a File Dialog.",
    placement:"bottom",
  });

  tour.addStep({
    element: "#group", 
    title: "Group Pictures", 
    content: "Do you want the best part of multiple pictures combined? Click individual pictures, in the box on the left, to select them, and then click the Group Button.",
    placement:"bottom",
  });

  tour.addStep({
    element: "#next", 
    title: "Finished Adding Pictures", 
    content: "When you are finished choosing pictures to be edited, click the Next Button.",
    placement:"bottom",
  });

  $("#upload_tour").click( function() {
    tour.restart();
  });
});

