$(function(){
  //globalize 
  var settingsTour = $("#doc_home_tour, #settings_tour"),
      docLand = $('#doc_home_tour').length;
  
  if(!settingsTour.length){
    return;  
  }

  var tour = new Tour({
      name: "become_a_doctor",
  });

  tour.addStep({
    element: "#become_doc_btn", /* html element next to which the step popover should be shown */
    title: "Create an Account", /* title of the popover */
    content: "We'll walk you through the necessary steps of becoming a pic doctor.", /* content of the popover */
    placement:"bottom"
  });

  var path = docLand ? "/doc_signin/?next=/account_settings/#merchant_tabtour" :"/account_settings/#merchant_tabtour";
  tour.addStep({
    path: path,
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
    element: "#bad_tab", 
    onShow: function (tour) { $("#bad_tab").click(); },
    title: "Become A Pic Doctor", 
    content: "Are you interested in making the jump to Pic Doctor?",
  });

  tour.addStep({
    element: "#cc_tab", 
    onShow: function (tour) { $("#cc_tab").click(); },
    title: "Credit Cards", 
    content: "Manage your previously entered Credit Cards here.",
  });

  tour.addStep({
    element: "#password_tab", 
    onShow: function (tour) { $("#password_tab").click(); },
    title: "Password", 
    content: "You can change your password on this tab.",
  });

  tour.addStep({
    element: "#profile_tab", 
    onShow: function (tour) { $("#profile_tab").click(); },
    title: "Profile", 
    content: "You can update profile settings here.",
  });

  settingsTour.click( function() {
    tour.restart();
  });

  if(window.location.hash == '#merchant_tabtour'){
    tour.restart();
  }

});

