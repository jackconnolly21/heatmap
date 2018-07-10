app.run: 
	@echo $(PYTHONPATH)
	export FLASK_APP=application.py && flask run
