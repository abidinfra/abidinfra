import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import rrwa, build_examples, hard_fail

def test_rrwa_bounds():
    r=rrwa([.8,.82,.81,.79,.83,.8,.81,.82,.1,.8])
    assert 0<=r['aggregate']<=1 and r['removed']>=1

def test_dataset_separate_directions():
    e=build_examples()
    assert len([x for x in e if x.direction=='en_to_yue'])==30
    assert len([x for x in e if x.direction=='en_to_zh'])==30

def test_variety_guard():
    build_examples()
    assert hard_fail('en_to_zh','我哋今日冇時間')
