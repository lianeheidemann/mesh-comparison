@echo off
cd /d "%~dp0.."
call conda activate meshEval
python -m meshcomparison.perceptual --gt data/samples/gt.stl --rm data/samples/mod.stl --out output
