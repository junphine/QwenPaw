# -*- coding: utf-8 -*-
import sys
if len(sys.argv)==1:
    sys.argv+=[
        "hub",
        "--port",
        "8088",
        "--host",
        "0.0.0.0",
        "--force-public"
    ]
print(sys.argv)
from qwenpaw.cli.main import cli

if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter

