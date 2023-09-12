import subprocess

for i in range(2):
    oid = ["oid1", "oid2"]
    subprocess.run(
        f"hey -n 100 -c 8 http://localhost:5001/magstats/{oid[i%2]}".split(
            " "
        ),
    )