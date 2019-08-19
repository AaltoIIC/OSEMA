/* Functions for searching  sensors in browse_sesnors.html page */

// Originally writteny by: Heikki Timonen, modified by Riku Ala-Laurinaho

/*Function comparison */
function sensor_comparison(sort_by){
    return function(a,b){
            return - b.getElementsByClassName(sort_by)[0].textContent.toLowerCase().localeCompare(a.getElementsByClassName(sort_by)[0].textContent.toLowerCase());
        };
}

$(document).ready(function(){
    $("#sensor_order_option").on("change", function(){
        var elements = $(".table > tbody >tr").get();
        var rule = $("#sensor_order_option").val();
        elements.sort(sensor_comparison(rule));
        if (document.getElementById("sensor_order_inverse").checked) {
          elements.reverse();
        }
        var elem = $(".table > tbody").get()[0];
        while (elem.firstChild){
            elem.removeChild(elem.firstChild);
        }

        for (i = 0, len = elements.length; i<len; i++){
            elem.appendChild(elements[i]);
        }
    });
});


$(document).ready(function(){
    $("#sensor_order_inverse").on("change", function(){
    var elements = $(".table > tbody > tr").get();
    var elem = $(".table > tbody").get()[0];
    while(elem.firstChild){
        elem.removeChild(elem.firstChild);
    }
    elements.reverse();
    for (i = 0, len=elements.length; i<len; i++){
        elem.appendChild(elements[i]);
    }
    });
});

$(document).ready(function(){
    $("#sensor_keyword").on("change", function(){
      var elements = $(".table > tbody > tr").get();
      var string = $("#sensor_keyword").val().toLowerCase();
      for (i = 0, len=elements.length; i<len; i++){
        found = 0 //0 not found, 1 = found
        var subElements = elements[i].getElementsByTagName('td')
        for (j = 0, len_sub=subElements.length; j<len_sub; j++){
          if (subElements[j].textContent.toLowerCase().search(string) > -1){
            found = 1;
            break;
          }
        }
        if (found === 0){
          elements[i].style.display = "none";
        }
        else {
          elements[i].style.display = "";
        }
      }
    });
});

//Written by Riku Ala-Laurinaho
$(document).ready(function(){
    var delete_buttons = document.getElementsByClassName("delete_button");
    for (var i = 0; i < delete_buttons.length; i++) {
      delete_buttons[i].onclick = function() {
        selection = window.confirm('Are you sure?');
        if (selection) {
          window.location = this.value;
        }
      }
    }
});

$('.status').each(function() {
  if ( this.innerHTML == "Measuring" ) {
    $(this).css('color', 'green');
  }
  else if (this.innerHTML == "Measuring, Waiting-for-update") {
      $(this).css({'color' : '#888e00'});
  }
  else if (this.innerHTML == "Waiting-for-update") {
      $(this).css('color', 'orange');
  }
  else if (this.innerHTML == "Failure, MemoryError" || this.innerHTML == 'Failure, OSError' || this.innerHTML == 'Failure, I2CError') {
      $(this).css('color', 'red');
  }
});
