//Originally written by Heikki Timonen. Modified by Riku Ala-Laurinaho

function protocol_comparison(sort_by){
    return function(a,b){
            return - b.getElementsByClassName(sort_by)[0].textContent.toLowerCase().localeCompare(a.getElementsByClassName(sort_by)[0].textContent.toLowerCase());
        };
}

$(document).ready(function(){
    $("#protocol_order_inverse").on("change", function(){
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
    $("#protocol_order_option").on("change", function(){
        var elements = $(".table > tbody >tr").get();
        var rule = $("#protocol_order_option").val();
        elements.sort(protocol_comparison(rule));
        console.log(rule);
        if (document.getElementById("protocol_order_inverse").checked) {
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
    $("#protocol_keyword").on("change", function(){
      var elements = $(".table > tbody > tr").get();
      var string = $("#protocol_keyword").val().toLowerCase();
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

$(document).ready(function(){
    $("#search_select").on("change", function(){
    var type = document.getElementById("search_select").value
    var elements = $(".table > tbody > tr").get();
    if (type == "All") {
      for (i = 0, len=elements.length; i<len; i++){
        elements[i].style.display = "";
      }
    }
    else {
      for (i = 0, len=elements.length; i<len; i++){
          if (elements[i].getElementsByClassName('type')[0].textContent == type) {
            elements[i].style.display = "";
          }
          else {
            elements[i].style.display = "none";
          }
      }
    }
    });
});

//Written by Riku Ala-Laurinaho
$(document).ready(function(){
    var delete_buttons = document.getElementsByClassName("delete_button");
    for (var i = 0; i < delete_buttons.length; i++) {
      delete_buttons[i].onclick = function() {
        selection = window.confirm('Are you sure? All sensors, which utilize this protocol instance are also deleted.');
        if (selection) {
          window.location = this.value;
        }
      }
    }
});
