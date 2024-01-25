virtualenv:
	source myvirtualenv/bin/activate
	export OPENAI_API_KEY=`cat ~/Dropbox/ai/apikey.txt`

run:
	python3 llm_post_feedback.py | tee llm_simulation_out.txt
	rm -f llm_simulation_out.sqlite
	sqlite3 llm_simulation_out.sqlite < stats.sql

sqlite:
	sqlite3 llm_simulation_out.sqlite 