$(function(){
  //globalize 
  tour = new Tour({
      name: "become_a_doctor",
  });

  tour.addStep({
    element: "#become_doc_btn", /* html element next to which the step popover should be shown */
    title: "Create an Account", /* title of the popover */
    content: "We'll walk you through the necessary steps of becoming a pic doctor.", /* content of the popover */
    onHide: function (tour) { window.location = "/doc_signin/?next=/account_settings/#merchant_tab"; tour.end();},
    placement:"bottom",
  });

  tour.addStep({
    element: "#merchant_tab", 
    onShow: function (tour) { $("#merchant_tab").click(); },
    title: "Merchant Info", 
    content: "In order to prevent fraud, the US Government requires you to provide the following information.  We cannot allow someone to be a doctor until they've done so.",
  });

  tour.addStep({
    element: "#bank_tab", 
    onShow: function (tour) { $("#bank_tab").click(); },
    title: "Bank Info", 
    content: "In order to withdraw money and see available jobs you'll need to have an associated bank account where your earnings can be deposited.",
  });

  tour.addStep({
    element: "#password_tab", 
    onShow: function (tour) { $("#password_tab").click(); },
    title: "Password", 
    content: "You can change your password on this tab.",
  });

  tour.addStep({
    element: "#home_tab", 
    onShow: function (tour) { $("#home_tab").click(); },
    title: "Profile", 
    content: "You can update profile settings here.",
  });

});

function begin_tour(){
  tour.restart();
}
