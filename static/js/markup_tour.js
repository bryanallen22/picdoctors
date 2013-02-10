$(function(){
  //globalize 
  tour = new Tour();

  tour.addStep({
    element: ".instruction", 
    title: "Describe General Instructions", 
    content: "Add detailed instructions of things you'd like done to the overall picture. IE. Brighten up the picture, Fix up the colors." 
  });

  tour.addStep({
    element: ".markup_pic_container", /* html element next to which the step popover should be shown */
    title: "Markup Your Picture", /* title of the popover */
    content: "Click and drag a location on your picture where you'd like a specific change done." /* content of the popover */
  });

  tour.addStep({
    element: ".imaginary_instruction_for_tour", 
    title: "Describe Specific Instruction", 
    content: "A coorelating colored description field will appear below the General Instructions. Add a detailed description of what you'd like done for that specific area. IE. Remove the red eye, Make me smile, blur out the logo." 
  });

  tour.addStep({
    element: ".markup_pic_container", 
    title: "Repeat", 
    content: "You can add as many markups as you'd like!"
  });

  tour.addStep({
    element: "#next", 
    title: "Finished", 
    content: "If you are finished describing the changes you'd like done click next.",
    placement:"bottom",
  });


});

function begin_tour(){
  tour.restart();
}
