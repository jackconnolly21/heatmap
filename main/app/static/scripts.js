$(function() {

  alert('In script.js')

  // configure typeahead
  $("#teamname").typeahead({
      hint = true,
      highlight: true,
      minLength: 1
  },
  {
      display: function(suggestion) { return null; },
      limit: 10,
      source: teams,
      templates: {
          suggestion: Handlebars.compile(
              "<div>" +
              // using Handlebars templating language, insert values in
              "{{{ id }}}, {{{ teamname }}}" +
              "</div>"
          )
      }
  });

  $("#teamname").on("typeahead:selected", function(eventObject, suggestion, name) {

      // use info
      var number = int(suggestion.id)
      alert(number)
      var teamname = suggestion.teamname

      $("#teamname").val(number)

  });

});

function teams(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        t: query
    };
    $.getJSON('/teams', parameters)
    .done(function(data, textStatus, jqXHR) {

        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}
