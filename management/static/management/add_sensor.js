$( window ).on( "load", function() {
  // If user changes the sensor type, available sample rates and default variables must also be changed
  sensor_type_selection = document.getElementById("id_add_sensor-model");
  sample_rate_selection = document.getElementById("id_add-sample_rate");
  default_variable_table = document.getElementById("variable_table");
  sample_rate_selection.value = current_sample_rate; //set default value
  sensor_type_selection.onchange = function() //Change available sample rates if sensor type is changed
  {
    $.get('modify/get_sample_rates/' + sensor_type_selection.value,
      function(data){
        while (sample_rate_selection.firstChild) {
          sample_rate_selection.removeChild(sample_rate_selection.firstChild);
        }
        data = JSON.parse(data)
        Object.keys(data).forEach(function(key) {
          var option = document.createElement("option");
          option.value = key;
          option.text = data[key];
          sample_rate_selection.add(option);
          if (option.value == current_sample_rate) {
            sample_rate_selection.value = option.value;
          }
        })
        change_available_sensitivities();
      }
    );
    $.get('modify/get_default_variables/' + sensor_type_selection.value,
      function(data){
        default_variable_table.innerHTML = data;
      }
    );
  };

  // When sample rate is selected only avaialable sensitivities are shown #template
  sensitivity_selection = document.getElementById("id_add-sensitivity");
  sensitivity_selection.value = current_sensitivity; //set default value

  function change_available_sensitivities() //Change available sensitivites if sample rate is changed
  {
    $.get('modify/get_available_sensitivities/' + sample_rate_selection.value,
      function(sensitivity_data){
        while (sensitivity_selection.firstChild) {
          sensitivity_selection.removeChild(sensitivity_selection.firstChild);
        }
        sensitivity_data = JSON.parse(sensitivity_data)
        Object.keys(sensitivity_data).forEach(function(key) {
          var option = document.createElement("option");
          option.value = key;
          option.text = sensitivity_data[key];
          sensitivity_selection.add(option);
          if (option.value == current_sensitivity) {
            sensitivity_selection.value = option.value;
          }
        })
      }
    );
  };
  sample_rate_selection.onchange = change_available_sensitivities;

  communication_technology_selection = document.getElementById("id_communication_technology");
  communication_instance_selection = document.getElementById("id_communication_instance");
  communication_form_placeholder = document.getElementById("communication_options");
  protocol_selection = document.getElementById("id_protocol");
  protocol_instance_selection = document.getElementById("id_protocol_instance");
  protocol_form_placeholder = document.getElementById("protocol_options");

  //Change communication technology to current setting
  communication_technology_selection.value = current_communication_technology;

  //Change communication technology instance to current setting
  communication_instance_selection.value = current_communication_id;

  //Change protocol to current setting
  protocol_selection.value = current_protocol;

  //Change protocol instance to current
  protocol_instance_selection.value = current_protocol_id;

  // When certain type of communication is selected, a new form is created, so it can be edited
  function get_communication_technology_form()
  {
    $.get('../get_communication_technology_form/' + communication_technology_selection.value + '/' + communication_instance_selection.value,
      function(form_data){
        form_data = JSON.parse(form_data);
        communication_form_placeholder.innerHTML = form_data;
        wrap_into_div(communication_form_placeholder);
      }
    );
  }

  communication_instance_selection.onchange = get_communication_technology_form;

  //Change available communication technology instances based on which communication technology user selects
  function change_available_communication_instances()
  {
    $.get('../get_communication_instances/' + communication_technology_selection.value,
      function(communication_technology_data){
        while (communication_instance_selection.firstChild) {
          communication_instance_selection.removeChild(communication_instance_selection.firstChild);
        }
        communication_technology_data = JSON.parse(communication_technology_data)
        Object.keys(communication_technology_data).forEach(function(key) {
          var option = document.createElement("option");
          option.value = key;
          option.text = communication_technology_data[key];
          communication_instance_selection.add(option);
          if (option.value == current_communication_id && communication_technology_selection.value == current_communication_technology) {
            communication_instance_selection.value = option.value;
          }
          get_communication_technology_form();
        })
      }
    );
  };

  communication_technology_selection.onchange = change_available_communication_instances;

  // When certain type of protocol is selected, a new form is created, so it can be also edited
  function get_protocol_form()
  {
    $.get('../get_protocol_form/' + protocol_selection.value + '/' + protocol_instance_selection.value,
      function(form_data){
        form_data = JSON.parse(form_data);
        protocol_form_placeholder.innerHTML = form_data;
        wrap_into_div(protocol_form_placeholder);
      }
    );
  }

  protocol_instance_selection.onchange = get_protocol_form;

  //Change available protocol instances based on which communication technology user selects
  function change_available_protocol_instances()
  {
    $.get('../get_protocol_instances/' + protocol_selection.value,
      function(protocol_data){
        while (protocol_instance_selection.firstChild) {
          protocol_instance_selection.removeChild(protocol_instance_selection.firstChild);
        }
        protocol_data = JSON.parse(protocol_data)
        Object.keys(protocol_data).forEach(function(key) {
          var option = document.createElement("option");
          option.value = key;
          option.text = protocol_data[key];
          protocol_instance_selection.add(option);
          if (option.value == current_protocol_id && protocol_selection.value == current_protocol) {
            protocol_instance_selection.value = option.value;
          }
        })
        get_protocol_form();
      }
    );
  };

  protocol_selection.onchange = change_available_protocol_instances;


  // wrapping new elements inside div
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
});

$( ".form-control" ).hover(
  function() {
    $( this ).next().css({"display" : "block"});
    //.style.display="block";
  }, function() {
    $( this ).next("p").css({"display" : "none"});
  }
);
