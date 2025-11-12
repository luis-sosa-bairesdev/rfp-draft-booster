#!/bin/bash
# Activate virtual environment and run Streamlit

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run main.py
