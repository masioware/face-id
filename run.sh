#!/usr/bin/env bash
set -euo pipefail

export LD_LIBRARY_PATH="$(python3.13 - <<'PY'
import importlib.resources as r
print((r.files("nvidia.cudnn") / "lib").as_posix())
PY
):${LD_LIBRARY_PATH:-}"

exec uvicorn --factory app:create_app --host 0.0.0.0 --port 8081