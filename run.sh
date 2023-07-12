#    workers_and_resources
#    Copyright (C) 2023  Tomas Härdin
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
set -e
./generate_lp.py > /tmp/program.lp && time lp_solve -S2 -v -presolve -presolver -g 1e3 < /tmp/program.lp | tee solution.txt
grep "Value of objective function" solution.txt
sed -n -e '/Actual values of the variables:/,// p' solution.txt | tail -n +2 | grep -vE 'invested|^con_|^prod_' | sort | ./parse_result.py > out.m
octave --persist out.m
