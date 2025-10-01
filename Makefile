run:
	poetry run uvicorn app.main:app --lifespan on --reload --host 127.0.0.1 --port 8000
