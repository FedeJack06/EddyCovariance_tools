import sys
from pathlib import Path

# find tob3-py-converter folder absolute path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from campbell import read_cs_files