$(function(){
  //globalize 
  window.uploadtour = new Tour();

  uploadtour.addStep({
    element: ".fileupload-addbutton", 
    title: "Add Pictures", 
    content: "Drag into the box or click here to add pictures.",
    placement:"bottom",
  });

  uploadtour.addStep({
    element: "#group", 
    title: "Group Pictures", 
    content: "Want the best of multiple pictures combined? Click two or more pictures on the left to select them and then click the \"Group\" button.",
    placement:"bottom",
  });

  uploadtour.addStep({
    element: "#next", 
    title: "Next",
    content: "When finished adding pictures, click \"Next\" to move on.",
    placement:"bottom",
  });

  $("#upload_tour").click( function() {
    uploadtour.restart();
  });
});

