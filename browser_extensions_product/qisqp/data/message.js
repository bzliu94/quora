function addNonVisibleBox() {
  var dom_element = unsafeWindow.document.createElement("div");
  var jq_element = unsafeWindow.$(dom_element);
  jq_element.attr("class", "qisqp_box");
  jq_element.html("<br>&nbsp;");
  jq_element.hide();
  unsafeWindow.$("body").append(jq_element);
}
// idempotent
function removeNonVisibleBox() {
  var jq_element_selector = unsafeWindow.$(".qisqp_box");
  if (jq_element_selector.length != 0) {
    jq_element_selector.remove();
  }
}
var num_messages = 0;
var cumulative_prev_message = "";
var curr_message = "";
function setBoxAndSetMessage(message) {
  if (num_messages == 0) {
    cumulative_prev_message += curr_message;
  } else {
    cumulative_prev_message += "<br>" + curr_message;
  }
  curr_message = message;
  removeNonVisibleBox();
  addNonVisibleBox();
  num_messages += 1;
  var jq_element = unsafeWindow.$(".qisqp_box");
  jq_element.html("QISQP:" + "<span class='qisqp_old'>" + cumulative_prev_message + "</span><br><span class='qisqp_current'>" + curr_message + "</span>");
  jq_element.show();
  jq_element.attr("class", "qisqp_box qisqp_fade_out");
}
;
