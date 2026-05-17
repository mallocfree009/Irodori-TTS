#!/usr/bin/env bash

# Move to the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo ".venv directory not found. Please run 'uv sync' first."
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Run the Gradio application
python gradio_app.py --server-name 127.0.0.1 --server-port 7860

# Keep the window open on exit (like the 'pause' in the batch file)
echo "Process completed. Press Enter to exit..."
read
