set -e
./generate_lp.py > /tmp/program.lp && time lp_solve -S2 -v -presolve < /tmp/program.lp | tee solution.txt
grep "Value of objective function" solution.txt
sed -n -e '/Actual values of the variables:/,// p' solution.txt | tail -n +2 | grep -vE 'invested|^con_|^prod_' | sort | ./parse_result.py > out.m
octave --persist out.m
