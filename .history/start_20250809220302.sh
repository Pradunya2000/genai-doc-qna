#!/bin/bash

# Run FastAPI in background on port 8000
uvicorn api_app:app --host 0.0.0.0 --port 8000 &

# Run Streamlit on port 8501
streamlit run streamlit/app.py --server.port 8501 --server.address 0.0.0.0
