import subprocess

for i in range(100):
    oid = ["oid1", "oid2"]
    subprocess.run(
        f"hey -n 100 -c 8 http://localhost:5001/detections/{oid[i%2]}".split(
            " "
        ),
    )
# for i in range(50):
#     subprocess.run(
#         "hey -n 100 -c 8 http://localhost:5001/objects/ZTF1/detections?survey_id=atlas".split(
#             " "
#         )
#     )
