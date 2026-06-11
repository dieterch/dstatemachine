#!/usr/bin/env python3
"""Create or replace encrypted myPlant credentials for dstatemachine."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import dmyplant2 as dmp2


def main() -> int:
    cred_file = ROOT / "data/.credentials"
    salt_file = ROOT / ".salt"

    if cred_file.exists() or salt_file.exists():
        print("Replacing existing credential store.")
        dmp2.tryagain()

    dmp2.cred()
    print("Credentials written to data/.credentials and .salt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
