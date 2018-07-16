# Volleyball Heat Map

This website will parse through one or more .dvw files, extracting relevant information to create a heat map of where attacks hit in the court, separated by attacker, combination, and possibly other information.

## Adding to the code:
For any database related functions, write the appropriate function in
`datastore.py` (ideally using sqlalchemy ORM) and then use that function
in the `application.py` file. All the database stuff lives in the `db/` folder.
`helpers.py` contains any helper functions that could be used amongst different
files (for example input/output stuff, or generating filenames). `heatMap.py`
has the functions used for generating heatmaps/line charts. Otherwise, normal
Flask application.

### Starting the code
Run `make app.run` in your terminal to run the application.
