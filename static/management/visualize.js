sensor_data = data;

$(document).ready(function(){
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


  Plotly.newPlot('graph', plot_data, layout);
});
