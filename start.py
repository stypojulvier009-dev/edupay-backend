import os
import subprocess
import sys

port = os.environ.get("PORT", "8000")
cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port]
sys.exit(subprocess.call(cmd))
