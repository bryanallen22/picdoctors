$(function(){
  //globalize 
  tour = new Tour();

  tour.addStep({
    element: "#price_tour_anchor", 
    title: "Choose a price", 
    content: "How much are you willing to pay for this job? Choose a price and type it here. You won't be charged until the job is complete.",
    placement:"right",
  });

  tour.addStep({
    element: "#suggestions", 
    title: "Suggestions", 
    content: "If you need some suggestions on how much it should cost, click here." 
  });

  tour.addStep({
    element: ".new_card", /* html element next to which the step popover should be shown */
    title: "Credit Card", /* title of the popover */
    content: "Enter your Credit Card information here." /* content of the popover */
  });


  tour.addStep({
    element: "#submit_payment", 
    title: "Submit Payment", 
    content: "Click here to submit your offer.  You won't be charged until the job is complete."
  });


});

function begin_tour(){

  tour.restart();
}
