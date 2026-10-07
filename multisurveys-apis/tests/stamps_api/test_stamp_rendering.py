import gzip
import io
from concurrent.futures import ThreadPoolExecutor

import astropy.io.fits as fio
import numpy as np

# from stamps_api.s3_handler.base_handler import s3_client
from stamps_api.s3_handler.fits_to_png import transform


def make_fits(seed: int, compressed: bool) -> bytes:
    rng = np.random.default_rng(seed)
    data = rng.normal(100, 10, size=(63, 63)).astype(np.float32)
    data[28:35, 28:35] += 50 * seed  # a "source" that differs per stamp
    buf = io.BytesIO()
    fio.PrimaryHDU(data).writeto(buf)
    raw = buf.getvalue()
    return gzip.compress(raw) if compressed else raw


def test_transform_returns_a_png():
    png = transform(make_fits(1, compressed=True), "cutoutScience", 2, True)
    assert png.startswith(b"\x89PNG")


def test_transform_does_not_use_pyplot(mocker):
    # pyplot keeps a global "current figure" shared by every thread. Its races are rare under the Agg backend, so
    # rather than hoping to reproduce one, fail if pyplot is used at all.
    import matplotlib.pyplot

    mocker.patch.object(matplotlib.pyplot, "figure", side_effect=AssertionError("transform used pyplot"))
    mocker.patch.object(matplotlib.pyplot, "gcf", side_effect=AssertionError("transform used pyplot"))

    assert transform(make_fits(1, compressed=False), "cutoutScience", 2, False).startswith(b"\x89PNG")


def test_concurrent_renders_match_sequential_ones():
    # Each render must be independent of the others running at the same time.
    args = []
    for seed in range(1, 13):
        compressed = seed % 2 == 0  # both the ZTF (gzipped) and LSST (plain) paths
        args.append((make_fits(seed, compressed), "cutoutScience", 2, compressed))

    sequential = [transform(*a) for a in args]
    with ThreadPoolExecutor(max_workers=6) as pool:
        concurrent = list(pool.map(lambda a: transform(*a), args))

    assert concurrent == sequential
    assert len(set(sequential)) == len(sequential)


# def test_s3_client_is_shared_per_region():
#     # Creating a client makes no network call, so this needs no credentials.
#     assert s3_client("us-east-1") is s3_client("us-east-1")
#     assert s3_client("us-east-1") is not s3_client("us-west-2")


# def test_s3_client_is_created_once_under_concurrent_first_calls():
#     with ThreadPoolExecutor(max_workers=8) as pool:
#         clients = list(pool.map(lambda _: s3_client("eu-west-1"), range(16)))
#     assert len({id(c) for c in clients}) == 1
