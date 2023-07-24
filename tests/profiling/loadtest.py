import subprocess

for i in range(50):
    oid = ["ZTF1", "ZTF2"]
    subprocess.run(
        f"hey -n 100 -c 8 http://localhost:5001/objects/{oid[i%2]}/detections?survey_id=ztf".split(
            " "
        ),
    )
for i in range(50):
    subprocess.run(
        "hey -n 100 -c 8 http://localhost:5001/objects/ZTF1/detections?survey_id=atlas".split(
            " "
        )
    )
