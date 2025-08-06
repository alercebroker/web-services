from src.s3_handler.lsst import LSSTS3Handler

# 396841690595406_396841690595406.avro
# 396841690595409_396841690595409.avro
# 396841690595417_396841690595417.avro
# 396841724149794_396841724149794.avro
# 396841724149795_396841724149795.avro

avros_data = [
    (396841690595406, 396841690595406),
    (396841690595409, 396841690595409),
    (396841690595417, 396841690595417),
    (396841724149794, 396841724149794),
    (396841724149795, 396841724149795),
]
handler = LSSTS3Handler()

for oid, measurement_id in avros_data:
    data_dict = handler.get_all_stamps(oid, measurement_id, "png")

    for stamp_type, data in data_dict.items():
        
        with open(f'/home/alex/Work/Projects/web-services/multisurvey-stamps/{data["file_name"]}', "wb") as f:
            f.write(data["file"].getbuffer())