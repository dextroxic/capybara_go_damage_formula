# Makefile
install:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

run: # Local dev, no sharing
	. venv/bin/activate && python app.py

run-share: # Share link for others to use
	SHARE=true INBROWSER=true PORT=7861 . venv/bin/activate && python app.py

run-auth: # Add password protection
	AUTH=true INBROWSER=true . venv/bin/activate && python app.py

run-prod: # Share + auth + specific port
	SHARE=true AUTH=true PORT=7861 . venv/bin/activate && python app.py
