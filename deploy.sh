#!/bin/zsh
# Deploy the POC dashboard as a background Streamlit service.
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$PWD:$PYTHONPATH"
exec python3 -m streamlit run dashboard/app.py \
  --server.headless true \
  --server.port 8501 \
  --browser.gatherUsageStats false
