$(function(){
  //globalize 
  var tour = new Tour();

  tour.addStep({
    element: ".fileupload-addbutton", 
    title: "Add Pictures", 
    content: "Drag into the box or click here to add pictures.",
    placement:"bottom",
  });

  tour.addStep({
    element: "#group", 
    title: "Group Pictures", 
    content: "Need to combine two or more pictures? Click to select them and then hit the \"Group\" button.",
    placement:"bottom",
  });

  tour.addStep({
    element: "#next", 
    title: "Next",
    content: "When finished adding pictures, click \"Next\" to move on.",
    placement:"bottom",
  });

  $("#upload_tour").click( function() {
    tour.restart();
  });
});

