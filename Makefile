# Run App
app.run:
	@echo $(PYTHONPATH)
	cd main/app/ && gunicorn -w 3 -t 600 -b 0.0.0.0:8080 wsgi_application:app

app.run.flask:
	@echo $(PYTHONPATH)
	cd main/app/ && export FLASK_APP=application.py && flask run

# Run Tests
test.all:
	@echo $(PYTHONPATH)
	cd tests/ && py.test
