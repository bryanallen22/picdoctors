// Generated by CoffeeScript 1.4.0

module("bootstrap-tour", {
  teardown: function() {
    this.tour.setState("current_step", null);
    this.tour.setState("end", null);
    return $.each(this.tour._steps, function(i, s) {
      if ((s.element != null) && (s.element.popover != null)) {
        return s.element.popover("hide").removeData("popover");
      }
    });
  }
});

test("Tour should set the tour options", function() {
  this.tour = new Tour({
    name: "test",
    afterSetState: function() {
      return true;
    },
    afterGetState: function() {
      return true;
    }
  });
  equal(this.tour._options.name, "test", "options.name is set");
  ok(this.tour._options.afterGetState, "options.afterGetState is set");
  return ok(this.tour._options.afterSetState, "options.afterSetState is set");
});

test("Tour should have default name of 'tour'", function() {
  this.tour = new Tour();
  return equal(this.tour._options.name, "tour", "tour default name is 'tour'");
});

test("Tour should accept an array of steps and set the current step", function() {
  this.tour = new Tour();
  deepEqual(this.tour._steps, [], "tour accepts an array of steps");
  return strictEqual(this.tour._current, 0, "tour initializes current step");
});

test("Tour.setState should save state cookie", function() {
  this.tour = new Tour();
  this.tour.setState("test", "yes");
  return strictEqual($.cookie("tour_test"), "yes", "tour saves state cookie");
});

test("Tour.getState should get state cookie", function() {
  this.tour = new Tour();
  this.tour.setState("test", "yes");
  strictEqual(this.tour.getState("test"), "yes", "tour gets state cookie");
  return $.cookie("tour_test", null);
});

test("Tour.setState should save state localStorage items", function() {
  this.tour = new Tour({
    useLocalStorage: true
  });
  this.tour.setState("test", "yes");
  return strictEqual(window.localStorage.getItem("tour_test"), "yes", "tour save state localStorage items");
});

test("Tour.getState should get state localStorage items", function() {
  this.tour = new Tour({
    useLocalStorage: true
  });
  this.tour.setState("test", "yes");
  strictEqual(this.tour.getState("test"), "yes", "tour save state localStorage items");
  return window.localStorage.setItem("tour_test", null);
});

test("Tour.addStep should add a step", function() {
  var step;
  this.tour = new Tour();
  step = {
    element: $("<div></div>").appendTo("#qunit-fixture")
  };
  this.tour.addStep(step);
  return deepEqual(this.tour._steps, [step], "tour adds steps");
});

test("Tour with onStart option should run the callback before showing the first step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour({
    onStart: function() {
      return tour_test += 2;
    }
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  return strictEqual(tour_test, 2, "tour runs onStart when the first step shown");
});

test("Tour with onEnd option should run the callback after hiding the last step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour({
    onEnd: function() {
      return tour_test += 2;
    }
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.end();
  return strictEqual(tour_test, 2, "tour runs onEnd when the last step hidden");
});

test("Tour with onShow option should run the callback before showing the step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour({
    onShow: function() {
      return tour_test += 2;
    }
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  strictEqual(tour_test, 2, "tour runs onShow when first step shown");
  this.tour.next();
  return strictEqual(tour_test, 4, "tour runs onShow when next step shown");
});

test("Tour with onShown option should run the callback after showing the step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour({
    onShown: function() {
      return tour_test += 2;
    }
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  return strictEqual(tour_test, 2, "tour runs onShown after first step shown");
});

test("Tour with onHide option should run the callback before hiding the step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour({
    onHide: function() {
      return tour_test += 2;
    }
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.next();
  strictEqual(tour_test, 2, "tour runs onHide when first step hidden");
  this.tour.hideStep(1);
  return strictEqual(tour_test, 4, "tour runs onHide when next step hidden");
});

test("Tour.addStep with onShow option should run the callback before showing the step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture"),
    onShow: function() {
      return tour_test = 2;
    }
  });
  this.tour.start();
  strictEqual(tour_test, 0, "tour does not run onShow when step not shown");
  this.tour.next();
  return strictEqual(tour_test, 2, "tour runs onShow when step shown");
});

test("Tour.addStep with onHide option should run the callback before hiding the step", function() {
  var tour_test;
  tour_test = 0;
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture"),
    onHide: function() {
      return tour_test = 2;
    }
  });
  this.tour.start();
  this.tour.next();
  strictEqual(tour_test, 0, "tour does not run onHide when step not hidden");
  this.tour.hideStep(1);
  return strictEqual(tour_test, 2, "tour runs onHide when step hidden");
});

test("Tour.getStep should get a step", function() {
  var step;
  this.tour = new Tour();
  step = {
    element: $("<div></div>").appendTo("#qunit-fixture"),
    path: "test",
    placement: "left",
    title: "Test",
    content: "Just a test",
    prev: -1,
    next: 2,
    end: false,
    animation: false,
    onShow: function(tour) {},
    onHide: function(tour) {},
    onShown: function(tour) {}
  };
  this.tour.addStep(step);
  return deepEqual(this.tour.getStep(0), step, "tour gets a step");
});

test("Tour.start should start a tour", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  return strictEqual($(".popover").length, 1, "tour starts");
});

test("Tour.start should not start a tour that ended", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.setState("end", "yes");
  this.tour.start();
  return strictEqual($(".popover").length, 0, "previously ended tour don't start again");
});

test("Tour.start(true) should force starting a tour that ended", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.setState("end", "yes");
  this.tour.start(true);
  return strictEqual($(".popover").length, 1, "previously ended tour starts again if forced to");
});

test("Tour.next should hide current step and show next step", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.next();
  strictEqual(this.tour.getStep(0).element.data("popover").tip().filter(":visible").length, 0, "tour hides current step");
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour shows next step");
});

test("Tour.end should hide current step and set end state", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.end();
  strictEqual(this.tour.getStep(0).element.data("popover").tip().filter(":visible").length, 0, "tour hides current step");
  return strictEqual(this.tour.getState("end"), "yes", "tour sets end state");
});

test("Tour.ended should return true is tour ended and false if not", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  strictEqual(this.tour.ended(), false, "tour returns false if not ended");
  this.tour.end();
  return strictEqual(this.tour.ended(), true, "tour returns true if ended");
});

test("Tour.restart should clear all states and start tour", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.next();
  this.tour.end();
  this.tour.restart();
  strictEqual(this.tour.getState("end"), null, "tour sets end state");
  strictEqual(this.tour._current, 0, "tour sets first step");
  return strictEqual($(".popover").length, 1, "tour starts");
});

test("Tour.hideStep should hide a step", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.hideStep(0);
  return strictEqual(this.tour.getStep(0).element.data("popover").tip().filter(":visible").length, 0, "tour hides step");
});

test("Tour.showStep should set a step and show it", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(1);
  strictEqual(this.tour._current, 1, "tour sets step");
  strictEqual($(".popover").length, 1, "tour shows one step");
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour shows correct step");
});

test("Tour.showStep should not show anything when the step doesn't exist", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(2);
  return strictEqual($(".popover").length, 0, "tour doesn't show any step");
});

test("Tour.showStep should skip step when no element is specified", function() {
  this.tour = new Tour();
  this.tour.addStep({});
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(1);
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour skips step with no element");
});

test("Tour.showStep should skip step when element doesn't exist", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: "#tour-test"
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(1);
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour skips step with no element");
});

test("Tour.showStep should skip step when element is invisible", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture").hide()
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(1);
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour skips step with no element");
});

test("Tour.setCurrentStep should set the current step", function() {
  this.tour = new Tour();
  this.tour.setCurrentStep(4);
  strictEqual(this.tour._current, 4, "tour sets current step if passed a value");
  this.tour.setState("current_step", 2);
  this.tour.setCurrentStep();
  return strictEqual(this.tour._current, 2, "tour reads current step state if not passed a value");
});

test("Tour.showNextStep should show the next step", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.start();
  this.tour.showNextStep();
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour shows next step");
});

test("Tour.showPrevStep should show the previous step", function() {
  this.tour = new Tour();
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.addStep({
    element: $("<div></div>").appendTo("#qunit-fixture")
  });
  this.tour.showStep(1);
  this.tour.showPrevStep();
  return strictEqual(this.tour.getStep(0).element.data("popover").tip().filter(":visible").length, 1, "tour shows previous step");
});

test("Tour.showStep should show multiple step on the same element", function() {
  var element;
  element = $("<div></div>").appendTo("#qunit-fixture");
  this.tour = new Tour();
  this.tour.addStep({
    element: element
  });
  this.tour.addStep({
    element: element
  });
  this.tour.start();
  strictEqual(this.tour.getStep(0).element.data("popover").tip().filter(":visible").length, 1, "tour show the first step");
  this.tour.showNextStep();
  return strictEqual(this.tour.getStep(1).element.data("popover").tip().filter(":visible").length, 1, "tour show the second step on the same element");
});
