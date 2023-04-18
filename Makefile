poetry:
	pip install -r requirements.txt
	python src/create_data.py
	python src/create_graph.py
	python src/app.py
