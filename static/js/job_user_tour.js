$(function(){
  //globalize 
  tour = new Tour();

  tour.addStep({
    element: "#col1_hook", 
    title: "Job", 
    content: "Your job number is listed in this column.  If you'd like to see your job album, click the job number.",
  });

  tour.addStep({
    element: "#col3_hook", 
    title: "Pictures", 
    content: "Your job pictures will slide around in this column.  If you click on the picture it will take you to the picture and the work (to be) done." 
  });

  tour.addStep({
    element: "#col5_hook", 
    title: "Job Size", 
    content: "The amount of pictures included in this job is listed here." 
  });

  tour.addStep({
    element: "#col7_hook", 
    title: "Job Status", 
    content: "The current status of your job."
  });

  tour.addStep({
    element: "#col12_hook", 
    title: "Available Actions", 
    content: "The available actions you can perform on your job.  These actions change depending on the current state of your Job."
  });

});

function begin_tour(){
  tour.restart();
}
