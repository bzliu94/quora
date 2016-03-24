// depend on $ being available at page as jQuery

// this script is being loaded after all other scripts on page

var form_key = unsafeWindow.require("settings").formkey;
function getMIMEType(url) {
  var extension = getSanctionedFileExtension(url);
  var mime_type;
  switch(extension) {
    case "jpg":
    ;
    case "jpeg":
      mime_type = "image/jpeg";
      break;
    case "png":
      mime_type = "image/png";
      break;
    case "gif":
      mime_type = "image/gif";
      break;
    case "bmp":
      mime_type = "image/bmp";
      break;
  }
  // console.log(mime_type);
  return mime_type;
}
function getSanctionedFileExtension(url) {
  var flags = "i";
  var re_str = "^.*\\.((jpe?g)|(png)|(gif)|(bmp))$";
  var re = new RegExp(re_str, flags);
  var match_arr = url.match(re);
  var extension = match_arr[1];
  // console.log(url);
  // console.log(extension);
  return extension;
}
// console.log("stage two");
checkLoggedIn();
function prepareUI() {
  // update interface
  var full_url = unsafeWindow.document.location.href;
  var re_str = "^https://www.quora.com/\\?qisqp_img_url=(.*)$";
  var re = new RegExp(re_str);
  var match_arr = full_url.match(re);
  var encoded_url = match_arr[1];
  var url = decodeURIComponent(decodeURIComponent(encoded_url));
  setBoxAndSetMessage("Image is being communicated.");
  self.port.emit("request_file", url);
}
function handleFileRequestResult(message) {
  var chars = message["chars"];
  var img_url = message["img_url"];
  var blob_param;
  var num_bytes = chars.length;
  var arr = new Uint8Array(num_bytes);
  for (var i = 0;i < chars.length;i++) {
    var char = chars[i];
    var int_value = char.charCodeAt(0);
    arr[i] = int_value;
  }
  blob_param = [arr];
  function successHandler(data, text_status, jqXHR) {
    // console.log(data);
    // console.log("success");
    var json_str = data;
    var json_obj = JSON.parse(json_str);
    var url_list = json_obj["qimg_urls"];
    var url = url_list[0];
    handleRemoteURL(url);
  }
  var url = "https://www.quora.com/_/imgupload/upload_POST";
  var form_data = new FormData;
  form_data.append("formkey", form_key);
  form_data.append("kind", "qtext");
  var mime_type = getMIMEType(img_url);
  var extension = getSanctionedFileExtension(img_url);
  var file = new Blob(blob_param, {type:mime_type});
  form_data.append("file", file, "file." + extension);
  // console.log(form_data);
  // console.log(blob_param);
  next_result = jQuery.ajax({
    type:"POST", 
    url:url, 
    data:form_data, 
    processData:false,
    // changed from "multipart/form-data" as otherwise we have no boundary
    contentType:false, 
    dataType:"text", 
    success:successHandler, 
    error:function(jqXHR, text_status, error_thrown) { 
      // console.log("failure");
      // console.log(text_status + error_thrown);
    }, 
    crossDomain:true, xhrFields:{withCredentials:true}
  });
}
self.port.on("request_file_result", handleFileRequestResult);
function handleRemoteURL(remote_url) {
  // console.log("we have a remote url");
  // console.log(remote_url);
  addImage(remote_url);
  scrollAskBarDetails(remote_url);
  setBoxAndSetMessage("Image has been inserted.");
}
function showAskBar() {
  var id = unsafeWindow.$(".LookupBarSelector").attr("id");
  // console.log(id);
  var re = new RegExp("__w2_(.+)_wrapper");
  var cid = id.match(re)[1];
  var w2 = unsafeWindow.require("webnode2");
  var lookup_bar_selector = w2._components[cid];
  lookup_bar_selector.setHighlight(true);
}
function expandAskBar() {
  var id = unsafeWindow.$(".details_toggle.add_details").attr("id");
  // console.log(id);
  var re = new RegExp("__w2_(.+)_add_details");
  var cid = id.match(re)[1];
  var w2 = unsafeWindow.require("webnode2");
  var lookup_bar_add_question = w2._components[cid];
  lookup_bar_add_question.showQuestionDetailsEditor(true);
}
function scrollAskBarDetails(img_url) {
  function scroll(event_object, detail_box_jq) {
    var detail_box = detail_box_jq[0];
    var scroll_height = Math.max(detail_box.scrollHeight, detail_box.clientHeight);
    detail_box.scrollTop = cloneInto(scroll_height - detail_box.clientHeight, unsafeWindow);
    // console.log("details", detail_box, scroll_height, detail_box.clientHeight)
  }
  var detail_box_jq = unsafeWindow.$(".AskBarDetails");
  // only support having one copy of an image quick-added at a time
  var image_jq = detail_box_jq.find("img[src*='" + img_url + "']");
  image_jq.load(cloneInto(function(event_object) {
      scroll(event_object, detail_box_jq);
    }, unsafeWindow, {cloneFunctions:true}));
}
function addImage(remote_url) {
  var doc_id = unsafeWindow.$(".doc").parent().attr("w2cid");
  var w2 = unsafeWindow.require("webnode2");
  var editor_component = w2._components[doc_id];
  var doc = editor_component.doc;
  var url_list = [remote_url];
  doc.insertImages(cloneInto(url_list, unsafeWindow, {cloneFunctions:true}));
}
function checkLoggedIn() {
  url = "https://www.quora.com/api/logged_in_user";
  function successHandler(data, text_status, jqXHR) {
    // console.log(data);
    var text = data.substr("while(1);".length);
    var json_value;
    if (text.length == 0) {
      json_value = {};
    } else {
      json_value = JSON.parse(text);
    }
    // console.log(json_value);
    var logged_in;
    if ("name" in json_value) {
      logged_in = true;
    } else {
      logged_in = false;
    }
    // console.log(logged_in);
    if (logged_in == false) {
      setBoxAndSetMessage("You are not logged in; process aborted.");
    }
    if (logged_in == true) {
      prepareUI();
      showAskBar();
      expandAskBar();
    }
  }
  result = jQuery.ajax({
    type:"GET", 
    async:false, 
    url:url, data:"", 
    processData:false, 
    contentType:false, 
    dataType:"text", 
    success:successHandler, 
    error:function(jqXHR, text_status, error_thrown) { }, 
    xhrFields:{withCredentials:true}
  });
}
;
