function checkImage(data) {
  var url = data.srcURL;
  var re1 = "((j|J)(p|P)(e|E)?(g|G))";
  var re2 = "((p|P)(n|N)(g|G))";
  var re3 = "((g|G)(i|I)(f|F))";
  var re4 = "((b|B)(m|M)(p|P))";
  var extension_str = "(" + re1 + "|" + re2 + "|" + re3 + "|" + re4 + ")";
  var re_str = "^((https?:)|(file:))//.*\\." + extension_str + "$";
  var re = new RegExp(re_str);
  var did_match = url.match(re) != null;
  return did_match;
}
function addContextMenuOption() {
  var contextMenu = require("sdk/context-menu");
  var data = require("sdk/self").data;
  var menuItem = contextMenu.Item({
    label:"Post image to Quora", 
    context:[contextMenu.SelectorContext("img"), contextMenu.PredicateContext(checkImage)], 
    contentScriptFile:[data.url("jquery-1.12.1.js"), data.url("cm_content.js")], 
    image:data.url("qisqp_16.png"), 
    onMessage:handleStageOne
  });
}
addContextMenuOption();
var tabs = require("sdk/tabs");
function handleStageOne(message) {
  var url = message;
  // console.log("url");
  var tab = tabs.activeTab;
  var encoded_url = encodeURIComponent(url);
  var next_url = "https://www.quora.com/?qisqp_img_url=" + encoded_url;
  tab.url = next_url;
}
function startListening(worker) {
  function handleFileRequest(message) {
    var url = message;
    // console.log(url)
    var re_str1 = "^https?://.*$";
    var re1 = new RegExp(re_str1);
    var re_str2 = "^file://(.*)$";
    var re2 = new RegExp(re_str2);
    var did_match_remote = url.match(re1) != null;
    var did_match_local = url.match(re2) != null;
    if (did_match_local == true) {
      var file_path = url.match(re2)[1];
      var file_io = require("sdk/io/file");
      var mode = "rb";
      var byte_reader = file_io.open(file_path, mode);
      var chars = byte_reader.read();
      byte_reader.close();
      var local_url = file_path;
      var result = {"chars":chars, "img_url":local_url};
      worker.port.emit("request_file_result", result);
    } else {
      if (did_match_remote == true) {
        var pwHandle = function(message) {
          var img_url = message["img_url"];
          var chars = message["chars"];
          var result = {"chars":chars, "img_url":img_url};
          // console.log(result);
          worker.port.emit("request_file_result", result);
          delete page_worker;
        };
        var pw = require("sdk/page-worker");
        var data = require("sdk/self").data;
        var page_worker = pw.Page({
          contentScriptFile:[data.url("jquery-1.12.1.js"), data.url("pw_content.js")], 
          contentURL:url, 
          onMessage:pwHandle
        });
        page_worker.postMessage(url);
      }
    }
  }
  worker.port.on("request_file", handleFileRequest);
}
var page_mod = require("sdk/page-mod");
var data = require("sdk/self").data;
page_mod.PageMod({
  include:["https://www.quora.com/?qisqp_img_url=*"], 
  contentScriptWhen:"end", 
  contentScriptFile:[data.url("jquery-1.12.1.js"), data.url("message.js"), data.url("content2.js")], 
  contentStyleFile:[data.url("message.css")], 
  onAttach:startListening
});
