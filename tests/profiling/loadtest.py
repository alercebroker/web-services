import subprocess

for i in range(100):
    oid = ["ZTF1", "ZTF2"]
    subprocess.run(
        f"hey -n 100 -c 8 http://localhost:5001/objects/{oid[i%2]}/detections?survey_id=ztf".split(
            " "
        ),
    )
