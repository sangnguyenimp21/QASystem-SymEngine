uvicorn app.main:app --host 0.0.0.0 --port $PORT &

# Wait for a few seconds to ensure the backend is up
sleep 5

# Start the Streamlit frontend
streamlit run frontend/main.py