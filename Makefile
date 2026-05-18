setup: requirements.txt
	pip install -r requirements.txt

pipeline: load_data.py src/summary_table.py src/stat_analysis.py src/data_subset_analysis.py
	python load_data.py
	python src/summary_table.py
	python src/stat_analysis.py
	python src/data_subset_analysis.py

dashboard: app.py
	python app.py
