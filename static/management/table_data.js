sensor_data = data;

$(document).ready(function(){
  var list_of_data = []
  var keys = Object.keys(sensor_data);
  var len = keys.length;
  //sorting values and adding time to last item
  keys.sort()
  keys.reverse()
  keys.pop()
  keys.sort()
  keys.push('time')
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
  var container = document.getElementById('example');
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
});
