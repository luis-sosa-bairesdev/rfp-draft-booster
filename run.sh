#!/bin/bash
# Script to run Streamlit with virtual environment activated

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run Streamlit
streamlit run main.py

