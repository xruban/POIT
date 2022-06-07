$(document).ready(function() {

  var namespace = null;
  var socket = null;
  var status = true;

  var x = new Array();
  var y = new Array();
  var z = new Array();
  var trace;
  var tracez;
  var layout;

  $('#init_form').on('submit', function(e) {
    e.preventDefault();

    namespace = '/test';
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
      socket.emit('my_event', {
        data: 'I\'m connected!',
        value: 1
      });
    });

    socket.on('my_response', function(msg) {
      console.log(msg.data);

      // $('#log').append('Received #'+msg.count+': '+msg.data+'<br>').html();
      if (status == true) {
        // For list tab
        $('#log_table tbody').append('<tr><td># ' + msg.count + '</td><td>' + msg.data + '</td></tr>');

        // For plot tab
        x.push(parseFloat(msg.count));
        y.push(parseFloat(msg.sinus));
        z.push(parseFloat(msg.cosinus));

        trace = {
          x: x,
          y: y,
        };

        tracez = {
          x: x,
          y: z,
        };

        layout = {
          title: 'Data',
          xaxis: {
            title: 'x',
          },
          yaxis: {
            title: 'y,z',
            //range: [-1,1]
          }
        };
        console.log(trace);
        console.log("this is tracez: ", tracez);
        var traces = new Array();
        traces.push(trace);
        traces.push(tracez);
        Plotly.newPlot('plotdiv', traces, layout);

        // For indicator tab
        var data = [{
          domain: {
            x: [0, 1],
            y: [0, 1]
          },
          value: parseFloat(msg.data),
          title: {
            text: "Values"
          },
          type: "indicator",
          mode: "gauge+number",
          delta: {
            reference: 1
          },
          gauge: {
            axis: {
              range: [null, 1]
            }
          }
        }];

        var layout = {
          width: 600,
          height: 400
        };

        Plotly.newPlot('indicatordiv', data, layout);
      }

    });

    $('#disabled_button').attr('disabled', false).addClass('uk-button-primary');
    $('#init_screen').slideUp(1000);
    $('#management_screen').slideDown(1000);

    return false;
  });

  // namespace = '/test';
  // var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
  //
  // socket.on('connect', function() {
  //   socket.emit('my_event', {data: 'I\'m connected!', value: 1}); });
  //
  // socket.on('my_response', function(msg) {
  //   console.log(msg.data);
  //   $('#log').append('Received #'+msg.count+': '+msg.data+'<br>').html(); });

  // $('form#emit').submit(function(event) {
  $('#submit_emit').on('click', function(event) {
    event.preventDefault();
    socket.emit('my_event', {
      value: $('#emit_value').val()
    });
    return false;
  });

  $('#buttonVal').click(function(event) {
    socket.emit('db_event', {
      value: $('#buttonVal').val()
    });
    if ($(this).val() == "start") {
      $(this).val("stop");
      $(this).text("Stop");
    } else {
      $(this).val("start");
      $(this).text("Start");
    }
    return false;
  });

  // $('form#disconnect').submit(function(event) {
  $('#disabled_button').on('click', function(event) {
    socket.emit('disconnect_request');

    $('#disabled_button').attr('disabled', true).removeClass('uk-button-primary');
    $('#management_screen').slideUp(1000);
    $('#init_screen').slideDown(1000);

    return false;
  });


  $('#submit_stop').on('click', function(event) {
    event.preventDefault();
    status = false;

    $('#submit_stop').attr('disabled', true);
    $('#submit_start').attr('disabled', false);

    return false;
  });

  $('#submit_start').on('click', function(event) {
    event.preventDefault();
    status = true;

    $('#submit_start').attr('disabled', true);
    $('#submit_stop').attr('disabled', false);

    return false;
  });

});
