$(document).ready(function(){
  var protocol_form_placeholder = document.getElementById("protocol_options");
  function wrap_into_div(element)
  {
    var children = element.children;
    var length = children.length / 2;
    for (var i = 0; i < length; i++) {
      var label = children[0];
      var input = children[1]
      var div = document.createElement("div");
      div.className = "mb-3";
      div.appendChild(label);
      div.appendChild(input);
      element.appendChild(div);
    }
  }
  function get_protocol_form()
  {
    $.get('../get_protocol_form/' + protocol_selection.value,
      function(form_data){
        form_data = JSON.parse(form_data);
        protocol_form_placeholder.innerHTML = form_data;
        wrap_into_div(protocol_form_placeholder);
      }
    );
  }
  protocol_selection = document.getElementById("id_protocol");
  protocol_selection.onchange = get_protocol_form;
});
