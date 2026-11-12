"""Run the Skill directly from its source directory."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from scientific_ppt.cli import main
if __name__=='__main__':raise SystemExit(main())
