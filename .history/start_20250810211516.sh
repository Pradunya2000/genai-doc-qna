#!/bin/bash

# Start the FastAPI backend in the background
uvicorn api_app:app --host 0.0.0.0 --port 8000 &

# Wait a few seconds for the backend to start
sleep 5

# Start the Streamlit frontend
streamlit run streamlit/app.py --server.port 8001 --server.baseUrlPath / --server.address 0.0.0.0