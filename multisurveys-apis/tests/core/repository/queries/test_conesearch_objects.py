import numpy as np
from astropy.coordinates import SkyCoord
from db_plugins.db.sql._connection import PsqlDatabase
from db_plugins.db.sql.models import Object
from sqlalchemy import select
from sqlalchemy.orm import Session

import core.repository.queries.conesearch as queries


def generate_ra_coordinates(ra_center_deg, dec_center_deg, n, half_range_arcsec):
    """
    Generate `n` coordinates evenly spaced along the RA axis,
    centered at (ra_center, dec_center), within ±half_range_arcsec.

    Parameters
    ----------
    ra_center_deg : float
        Center RA in degrees.
    dec_center_deg : float
        Center Dec in degrees.
    n : int
        Number of coordinates to generate.
    half_range_arcsec : float
        Maximum RA offset from center (in arcseconds).

    Returns
    -------
    coords : list of SkyCoord
        List of generated coordinates.
    """
    # Convert arcseconds to degrees
    half_range_deg = half_range_arcsec / 3600.0

    # Correction for Dec: RA offsets shrink by cos(dec)
    dec_rad = np.deg2rad(dec_center_deg)
    ra_offsets_deg = np.linspace(-half_range_deg, half_range_deg, n) / np.cos(dec_rad)

    # Create coordinates
    coords = [
        SkyCoord(ra=ra_center_deg + offset, dec=dec_center_deg, unit="deg")
        for offset in ra_offsets_deg
    ]

    return coords


def test_conesearch_oid_few_close_objects(db: PsqlDatabase):
    """Test conesearch_oid function

    This test inserts 10 objects with a closer distance than 30 arcsec,
    and then adds 10 more objects farther away than 30 arcsec.

    Then checks if the conesearch returns only the 10 close objects.

    Uses the generate_ra_coordinates function to generate the coordinates.
    That function takes a center RA coordinate and generates evenly spaced points along the axis.
    """
    # Prepare the database
    session: Session
    nobjects = 10
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

        coordinates = generate_ra_coordinates(45.0, 45.0, nobjects, 30.0)

        for i in range(nobjects - 1):
            session.add(
                Object(
                    oid=i,
                    tid=1,
                    sid=1,
                    meanra=coordinates[i].ra.deg.item(),  # type: ignore
                    meandec=coordinates[i].dec.deg.item(),  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        for i in range(nobjects):
            session.add(
                Object(
                    oid=i + 10,
                    tid=1,
                    sid=1,
                    meanra=coordinates[0].ra.deg.item() - 10,  # type: ignore
                    meandec=coordinates[-1].dec.deg.item() + 10,  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        all_objects = [row[0] for row in session.execute(select(Object))]
        assert len(all_objects) == nobjects * 2

    # Execute the conesearch
    conesearch = queries.conesearch_oid(db.session)
    result = conesearch((np.int64(123), 30.0 / 3600, 10))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10

    # Execute conesearch with more than 10 neighbors
    conesearch = queries.conesearch_oid(db.session)
    result = conesearch((np.int64(123), 30.0 / 3600, 20))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10


def test_conesearch_oid_all_are_close(db: PsqlDatabase):
    """Test conesearch_oid function

    This test inserts 20 objects with a closer distance than 30 arcsec.
    There are no other objects.

    Uses the generate_ra_coordinates function to generate the coordinates.
    That function takes a center RA coordinate and generates evenly spaced points along the axis.
    """
    # Prepare the database
    session: Session
    nobjects = 20
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

        coordinates = generate_ra_coordinates(45.0, 45.0, nobjects, 30.0)

        for i in range(nobjects - 1):
            session.add(
                Object(
                    oid=i,
                    tid=1,
                    sid=1,
                    meanra=coordinates[i].ra.deg.item(),  # type: ignore
                    meandec=coordinates[i].dec.deg.item(),  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        all_objects = [row[0] for row in session.execute(select(Object))]
        assert len(all_objects) == nobjects

    # Execute the conesearch
    conesearch = queries.conesearch_oid(db.session)
    result = conesearch((np.int64(123), 30.0 / 3600, 10))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10

    # Execute conesearch with 20 neighbors should return all 20 objects
    conesearch = queries.conesearch_oid(db.session)
    result = conesearch((np.int64(123), 30.0 / 3600, 20))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 20


def test_conesearch_oid_none_are_close(db: PsqlDatabase):
    """Test conesearch_oid function

    There are no objects other than the center.
    """
    # Prepare the database
    session: Session
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

    # Execute the conesearch
    conesearch = queries.conesearch_oid(db.session)
    result = conesearch((np.int64(123), 30.0 / 3600, 10))

    # Assert that the conesearch returns the only object
    assert len(result) == 1


def test_conesearch_coordinates_close_objects(db: PsqlDatabase):
    """Test conesearch_coordinates function

    This test inserts 10 objects with a closer distance than 30 arcsec,
    and then adds 10 more objects farther away than 30 arcsec.

    Then checks if the conesearch returns only the 10 close objects.

    Uses the generate_ra_coordinates function to generate the coordinates.
    That function takes a center RA coordinate and generates evenly spaced points along the axis.
    """
    # Prepare the database
    session: Session
    nobjects = 10
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

        coordinates = generate_ra_coordinates(45.0, 45.0, nobjects, 30.0)

        for i in range(nobjects - 1):
            session.add(
                Object(
                    oid=i,
                    tid=1,
                    sid=1,
                    meanra=coordinates[i].ra.deg.item(),  # type: ignore
                    meandec=coordinates[i].dec.deg.item(),  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        for i in range(nobjects):
            session.add(
                Object(
                    oid=i + 10,
                    tid=1,
                    sid=1,
                    meanra=coordinates[0].ra.deg.item() - 10,  # type: ignore
                    meandec=coordinates[-1].dec.deg.item() + 10,  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        all_objects = [row[0] for row in session.execute(select(Object))]
        assert len(all_objects) == nobjects * 2

    # Execute the conesearch
    # center at 45, 45 within 30 arcsec and 10 neighbors
    conesearch = queries.conesearch_coordinates(db.session)
    result = conesearch((45, 45, 30.0 / 3600, 10))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10

    # Execute conesearch with more than 10 neighbors
    conesearch = queries.conesearch_coordinates(db.session)
    result = conesearch((45, 45, 30.0 / 3600, 20))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10


def test_conesearch_coordinates_all_are_close(db: PsqlDatabase):
    """Test conesearch_coordinates function

    This test inserts 20 objects with a closer distance than 30 arcsec.
    There are no other objects.

    Uses the generate_ra_coordinates function to generate the coordinates.
    That function takes a center RA coordinate and generates evenly spaced points along the axis.
    """
    # Prepare the database
    session: Session
    nobjects = 20
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

        coordinates = generate_ra_coordinates(45.0, 45.0, nobjects, 30.0)

        for i in range(nobjects - 1):
            session.add(
                Object(
                    oid=i,
                    tid=1,
                    sid=1,
                    meanra=coordinates[i].ra.deg.item(),  # type: ignore
                    meandec=coordinates[i].dec.deg.item(),  # type: ignore
                    firstmjd=59000.0,
                    lastmjd=59001.0,
                    deltamjd=1.0,
                    n_det=1,
                    n_forced=1,
                    n_non_det=1,
                )
            )
        session.commit()

        all_objects = [row[0] for row in session.execute(select(Object))]
        assert len(all_objects) == nobjects

    # Execute the conesearch
    conesearch = queries.conesearch_coordinates(db.session)
    result = conesearch((45, 45, 30.0 / 3600, 10))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 10

    # Execute conesearch with 20 neighbors should return all 20 objects
    conesearch = queries.conesearch_coordinates(db.session)
    result = conesearch((45, 45, 30.0 / 3600, 20))

    # Assert that the conesearch returns only the 10 close objects
    assert len(result) == 20


def test_conesearch_coordinates_none_are_close(db: PsqlDatabase):
    """Test conesearch_coordinates function

    There are no objects other than the center.
    """
    # Prepare the database
    session: Session
    with db.session() as session:
        center = Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        )
        session.add(center)
        session.commit()

    # Execute the conesearch
    conesearch = queries.conesearch_coordinates(db.session)
    result = conesearch((45, 45, 30.0 / 3600, 10))

    # Assert that the conesearch returns the only object
    assert len(result) == 1
