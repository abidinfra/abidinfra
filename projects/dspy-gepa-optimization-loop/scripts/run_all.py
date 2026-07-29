from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import run
run(Path(__file__).resolve().parents[1]/'results')
print('All experiments completed; results/summary.json refreshed.')
