/*
JS for panels

Created for the RoboTeam Twente as part of the Design Project for the Bachelor
Technical Computer Science of the University of Twente.

All Rights Reserved.
*/

$.ready(function () {
  // Bind hide and switch buttons
  $(".panel-hide, .panel-switch").click(function (event) {
    showOtherPanel($(event.target).closest(".panel"));
  });

  // Bind full screen buttons
  $(".panel-full-screen").click(function (event) {
    showSinglePanel($(event.target).closest(".panel"));
  });

  // Bind show other buttons
  $(".panel-show-other").click(function () {
    showAllPanels();
  });
});

/**
 * Function to show all panels
 */
function showAllPanels() {
  $(".panel-full-screen, .panel-hide").css("display", "inline");
  $(".panel").show();
  $(".panel-show-other, .panel-switch").hide();
}

/**
 * Function to show a single panel
 *
 * @param panel The panel to show
 */
function showSinglePanel(panel) {
  $(".panel, .panel-full-screen, .panel-hide").hide();
  $(panel).show();
  $(".panel-show-other, .panel-switch").css("display", "inline");
}

/**
 * Function to show the other panel instead of this one
 * @param thisPanel The current pannel
 */
function showOtherPanel(thisPanel) {
  $(".panel").show();
  $(".panel-full-screen, .panel-hide").hide();
  $(thisPanel).hide();
  $(".panel-show-other, .panel-switch").css("display", "inline");
}