$(function() {

  // configure typeahead
  alert("in js!");
  $("#teamname").typeahead({
      highlight: false,
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
              "{{{vm_num}}}, {{{name}}}" +
              "</div>"
          )
      }
  });
});

function teams(query, syncResults, asyncResults)
{
    alert("In teams!!")
    // get places matching query (asynchronously)
    var parameters = {
        t: query
    };
    $.getJSON(Flask.url_for("teams"), parameters)
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
