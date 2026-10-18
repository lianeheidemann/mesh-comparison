@echo off
cd /d "%~dp0.."
call conda activate meshEval
python -m meshcomparison.geometry --gt data/samples/gt.stl --rm data/samples/mod.stl --out output
