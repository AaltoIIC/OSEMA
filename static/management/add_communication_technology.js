$(document).ready(function(){
  var communication_form_placeholder = document.getElementById("communication_options");
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
  function get_communication_technology_form()
  {
    $.get('../get_communication_technology_form/' + communication_technology_selection.value,
      function(form_data){
        form_data = JSON.parse(form_data);
        communication_form_placeholder.innerHTML = form_data;
        wrap_into_div(communication_form_placeholder);
      }
    );
  }
  communication_technology_selection = document.getElementById("id_communication_technology");
  communication_technology_selection.onchange = get_communication_technology_form;
});
