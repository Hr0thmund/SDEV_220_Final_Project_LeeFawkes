This a proof of concept/minimum viable product of a web-based network device configuration generator. 
In this iteration, the jinja2 template files are stored statically in configurator/jinja2/configurator 
off the project root, and the associations between roles, platforms, and templates is statically
configured at the beginning of configurator/views.py. The platform and card definitions must be
manually loaded into the database - there is a script seed_db.py in the project root to facilitate this,
which has been loaded with a few example platforms and cards for test data.

run "python3 manage.py flush" to clear test data from db

To clone and set up the project:

git clone https://github.com/Hr0thmund/SDEV_220_Final_Project_LeeFawkes.git webconf

cd webconf

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python3 seed_db.py
