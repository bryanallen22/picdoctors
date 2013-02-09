$(function(){
  //globalize 
  tour = new Tour();

  tour.addStep({
    element: "#isocontainer", /* html element next to which the step popover should be shown */
    title: "Add Pictures", /* title of the popover */
    content: "The first thing you need to do is add some pictures.  Drag from your desktop/folder to the box." /* content of the popover */
  });

  tour.addStep({
    element: ".fileupload-addbutton", 
    title: "Add Pictures", 
    content: "Or click here to open a File Dialog and choose your pictures that way!" 
  });

  tour.addStep({
    element: "#group", 
    title: "Group Pictures", 
    content: "Do you want the best part of multiple pictures combined? Click individual pictures, in the box on the left, to select them, and then click the Group Button."
  });

  tour.addStep({
    element: "#next", 
    title: "Finished Choosing Pictures", 
    content: "If you are finished choosing pictures to be edited, click the Next Button."
  });


});

function begin_tour(){
  tour.restart();
}
