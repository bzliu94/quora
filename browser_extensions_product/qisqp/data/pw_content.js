// courtesy of henry algus
// use this transport for "binary" data type
$.ajaxTransport("+binary", function(options, original_options, jqXHR) {
  // check for conditions and support for blob/arraybuffer response type
  if (window.FormData && (options.dataType && options.dataType == "binary" || options.data && (window.ArrayBuffer && options.data instanceof ArrayBuffer || window.Blob && options.data instanceof Blob))) {
    return {
      // create new XMLHttpRequest
      send: function(headers, callback) {
      // setup all variables
      var xhr = new XMLHttpRequest(), 
        url = options.url, 
        type = options.type, 
        async = options.async || true, 
        // blob or arraybuffer; default is blob
        dataType = options.responseType || "blob", 
        data = options.data || null, 
        username = options.username || null, 
        password = options.password || null;
      xhr.addEventListener("load", function() {
        var data = {};
        data[options.dataType] = xhr.response;
        // make callback and send data
        callback(xhr.status, xhr.statusText, data, xhr.getAllResponseHeaders());
      });
      xhr.open(type, url, async, username, password);
      // setup custom headers
      for (var i in headers) {
        xhr.setRequestHeader(i, headers[i]);
      }
      xhr.responseType = dataType;
      xhr.send(data);
    }, abort: function() {
      jqXHR.abort();
    }};
  }
});
function handleMessage(message) {
  var url = message;
  function successHandler(data, text_status, jqXHR) {
    var blob = data;
    var file_reader = new FileReader;
    function handleRead(event) {
      // var arr_buffer = file_reader.result
      // var ui8a = new unsafeWindow.Uint8Array(arr_buffer)
      var chars = file_reader.result;
      var next_result = {"img_url":url, "chars":chars};
      self.postMessage(next_result);
    }
    file_reader.onloadend = handleRead;
    // file_reader.readAsArrayBuffer(blob)
    file_reader.readAsBinaryString(blob);
  }
  var result = jQuery.ajax({
    type:"GET", 
    // async:false, 
    url:url, 
    data:"", 
    processData:false, 
    contentType:false, 
    responseType:"blob", 
    dataType:"binary", 
    success:successHandler, 
    error:function(jqXHR, text_status, error_thrown) { }, 
    xhrFields:{withCredentials:true}
  });
}
self.on("message", handleMessage);
