sensor_data = data;

function visualization(){
  document.getElementById('content').innerHTML = "";
  var list_of_traces = []
  var keys = Object.keys(sensor_data);
  var len = keys.length;
  keys.sort()
  var i = 0;
  for (i = 0; i < len; i++) {
    if (keys[i] != "time") {
      var trace = {
        x: sensor_data["time"],
        y: sensor_data[keys[i]],
        mode: 'scatter',
        name: keys[i]
      };
      list_of_traces.push(trace);
    }
  }
  var plot_data = list_of_traces;

  var layout = {
    autosize: true,
    height: 1000,
    title: filename,
    xaxis: {
            title: 'Time',
            showline: true
          },
    yaxis: {
            title: "Value",
            rangemode: 'tozero',
            showline: true,
            zeroline: true
          }
  };
  Plotly.newPlot('content', plot_data, layout);
}

function table(){
  document.getElementById('content').innerHTML = "";
  var list_of_data = []
  var keys = Object.keys(sensor_data);
  //sorting values and adding time to last item
  keys.sort()
  keys.reverse()
  keys.pop()
  keys.sort()
  keys.push('time')
  var len = keys.length;
  var i = 0;
  var arrays = [];
  for (i = 0; i < sensor_data[keys[0]].length; i++) {
    arrays.push([]);
  }
  for (var i = 0; i < sensor_data[keys[0]].length; i++) {
    for (var j = 0; j < len; j++) {
        arrays[i].push(sensor_data[keys[j]][i]);
      }
  }
  data = arrays;
  var container = document.getElementById('content');
  var hot = new Handsontable(container, {
    data: data,
    rowHeaders: true,
    stretchH: 'all',
    autoWrapRow: true,
    height: 1000,
    colHeaders: keys,
    columnSorting: true,
    sortIndicator: true,
    contextMenu: true
  });
}

//Are you sure? to delete buttons
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

var visualize_btn = document.getElementById("visualize_btn");
var table_btn = document.getElementById("table_btn");

visualize_btn.onclick = visualization;
table_btn.onclick = table;

//Initially visualization
$(document).ready(visualization);
