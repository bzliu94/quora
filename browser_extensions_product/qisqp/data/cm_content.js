var is_logged_in = false;
function handleClick(node, data) {
  jq_element = $(node);
  var url = jq_element.attr("src");
  // console.log("clicked");
  // console.log(url);
  self.postMessage(url);
}
self.on("click", handleClick);
