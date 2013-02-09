$(function(){
  //globalize 
  tour = new Tour();

  tour.addStep({
    element: "#col1_hook", 
    title: "Job", 
    content: "The job number is listed in this column.  If you'd like to see the work to be done, click the job number.",
  });

  tour.addStep({
    element: "#col3_hook", 
    title: "Pictures", 
    content: "The job pictures will slide around in this column.  When a picture is clicked you will be taken to the picture and the work (to be) done." 
  });

  tour.addStep({
    element: "#col5_hook", 
    title: "Job Size", 
    content: "The amount of pictures included in this job is listed here." 
  });

  tour.addStep({
    element: "#col7_hook", 
    title: "Job Worth", 
    content: "The amount the job is worth, and how much will be paid out to you if the job is completed and accepted." 
  });

  tour.addStep({
    element: "#col9_hook", 
    title: "Job Status", 
    content: "The current status of the job."
  });

  tour.addStep({
    element: "#col12_hook", 
    title: "Available Actions", 
    content: "The available actions you can perform on this job.  These actions change depending on the current state of the Job."
  });

});

function begin_tour(){
  tour.restart();
}
