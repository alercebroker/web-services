import argparse
from core.idmapper import idmapper


def main():
    parser = argparse.ArgumentParser(description="Convert integer oid to string")
    parser.add_argument("oid", type=int, help="the object id")
    args = parser.parse_args()

    print(idmapper.decode_masterid(args.oid))
