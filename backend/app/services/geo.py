from geoalchemy2.elements import WKTElement
from sqlalchemy import ColumnElement, func

from app.models.pharmacy import Pharmacy


def point(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def distance_km_expr(lat: float, lng: float) -> ColumnElement[float]:
    """SQL expression: distance in km from (lat, lng) to Pharmacy.geom."""
    return func.ST_Distance(Pharmacy.geom, point(lat, lng)) / 1000.0
