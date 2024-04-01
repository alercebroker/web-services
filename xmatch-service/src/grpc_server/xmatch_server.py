from grpc_server.xmatch_pb2_grpc import (
    XmatchServiceServicer,
    add_XmatchServiceServicer_to_server,
)
from grpc_server.xmatch_pb2 import ConesearchResponse, ConesearchRequest, Object
from core.service import get_oids_from_coordinates
import grpc
from concurrent import futures
from database.database import create_connection
import os


class XmatchServicer(XmatchServiceServicer):
    def __init__(self):
        user = os.getenv("DB_USER")
        pwd = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT", 5432)
        db = os.getenv("DB_DATABASE", "xmatch")
        self.pool = create_connection(user, pwd, host, port, db)

    def Conesearch(self, request: ConesearchRequest, context):
        ra = request.ra
        dec = request.dec
        radius = request.radius
        cat = request.catalog
        nneighbor = request.nneighbors
        result = get_oids_from_coordinates(ra=ra, dec=dec, radius=radius, pool=self.pool, cat=cat, nneighbor=nneighbor)
        result = [
            Object(id=mastercat.id, ra=mastercat.ra, dec=mastercat.dec, catalog=mastercat.cat, distance=0)
            for mastercat in result
        ]
        return ConesearchResponse(objects=result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_XmatchServiceServicer_to_server(XmatchServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("Starting server. Listening on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
