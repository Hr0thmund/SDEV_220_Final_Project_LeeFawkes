This a proof of concept/minimum viable product of a web-based network device configuration generator. 
In this iteration, the jinja2 template files are stored statically in configurator/jinja2/configurator 
off the project root, and the associates between roles, platforms, and templates is statically
configured at the beginning of configurator/views.py. The platform and card definitions must be
manually loaded into the database - there is a script seed_db.py in the project root to facilitate this,
which has been loaded with a few example platforms and cards for test data.

run "python3 seed_db.py" to load db with test data
run "python3 manage.py flush" to clear test data from db
