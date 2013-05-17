$(function(){
  //globalize 
  var tour = new Tour();

  tour.addStep({
    element: "#price_tour_anchor", 
    title: "Choose a price", 
    content: "How much is the job worth? You won't be charged until the job is complete.",
    placement:"right",
  });

  tour.addStep({
    element: "#suggestions", 
    title: "Suggestions", 
    content: "Need suggestion on how much to pay? Click here." 
  });

  tour.addStep({
    element: ".new_card", /* html element next to which the step popover should be shown */
    title: "Credit Card", /* title of the popover */
    content: "Enter your Credit Card information here. Your CCV2 number is usually the last 3 digits printed on the back of your card." /* content of the popover */
  });


  tour.addStep({
    element: "#submit_payment", 
    title: "Submit Payment", 
    content: "Click here to submit your offer.  You won't be charged until the job is complete."
  });

  $("#setprice_tour").click( function() {
    tour.restart();
  });

});

