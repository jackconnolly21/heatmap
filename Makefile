app.run:
	@echo $(PYTHONPATH)
	gunicorn -w 3 -t 600 -b 0.0.0.0:8080 wsgi_application:app

app.run.flask:
	@echo $(PYTHONPATH)
	export FLASK_APP=application.py && flask run
