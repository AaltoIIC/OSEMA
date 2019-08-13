$( ".form-control" ).hover(
  function() {
    $( this ).next().css({"display" : "block"});
  }, function() {
    $( this ).next("p").css({"display" : "none"});
  }
);

var download_file_btn = document.getElementById("download_file_btn");
download_file_btn.onclick = function() {
  location.href="download/software/" + sensor_id;
  }
