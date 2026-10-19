#!/usr/bin/env bash
# Build report/report.pdf from report/report_source.md (pandoc + XeLaTeX).
set -euo pipefail
cd "$(dirname "$0")/report"
pandoc report_source.md -s -o report.tex -V mainfont="DejaVu Sans" -V mathfont="DejaVu Math TeX Gyre"
sed -i 's/^\\usepackage{lmodern}//' report.tex   # lmodern is not needed with XeLaTeX
xelatex -interaction=nonstopmode report.tex >/dev/null
xelatex -interaction=nonstopmode report.tex >/dev/null
rm -f report.aux report.log report.out report.tex
echo "built report/report.pdf"
