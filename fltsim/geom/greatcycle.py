import math
from typing import Tuple

R = 6371393.0
DEG_RADIAN = math.pi / 180.0
RADIAN_DEG = 180.0 / math.pi
G0 = 0.982
epsilon = 7.0/3 - 4.0/3 - 1.0
KM2M = 1000.0
M2KM = 1.0 / KM2M


def distance(c0, c1):
    lng0 = c0[0] * DEG_RADIAN
    lat0 = c0[1] * DEG_RADIAN
    lng1 = c1[0] * DEG_RADIAN
    lat1 = c1[1] * DEG_RADIAN
    dlng = lng0 - lng1
    dlat = lat0 - lat1
    tmp1 = math.sin(dlat/2)
    tmp2 = math.sin(dlng/2)
    a = tmp1 * tmp1 + math.cos(lat0) * math.cos(lat1) * tmp2 * tmp2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def distance_lnglat(d0, d1):
    lng0 = math.radians(d0.lng)
    lat0 = math.radians(d0.lat)
    lng1 = math.radians(d1.lng)
    lat1 = math.radians(d1.lat)
    dlng = lng0 - lng1
    dlat = lat0 - lat1
    tmp1 = math.sin(dlat/2)
    tmp2 = math.sin(dlng/2)
    a = tmp1 * tmp1 + math.cos(lat0) * math.cos(lat1) * tmp2 * tmp2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def bearing_lnglat(d0, d1):
    lng0 = math.radians(d0.lng)
    lat0 = math.radians(d0.lat)
    lng1 = math.radians(d1.lng)
    lat1 = math.radians(d1.lat)
    dlng = lng1 - lng0
    coslat1 = math.cos(lat1)
    tmp1 = math.sin(dlng) * coslat1
    tmp2 = math.cos(lat0) * math.sin(lat1) - math.sin(lat0) * coslat1 * math.cos(dlng)
    return (math.atan2(tmp1, tmp2) * RADIAN_DEG)%360


def bearing(c0, c1):
    lng0 = c0[0] * DEG_RADIAN
    lat0 = c0[1] * DEG_RADIAN
    lng1 = c1[0] * DEG_RADIAN
    lat1 = c1[1] * DEG_RADIAN
    dlng = lng1 - lng0
    coslat1 = math.cos(lat1)
    tmp1 = math.sin(dlng) * coslat1
    tmp2 = math.cos(lat0) * math.sin(lat1) - math.sin(lat0) * coslat1 * math.cos(dlng)
    return (math.atan2(tmp1, tmp2) * RADIAN_DEG)%360


def intersection(a0, a1):
    c = (a0-a1)%360
    if c > 180:
        return c - 360
    return c


def to_vector(p) -> Tuple:
    lng = p[0]
    lat = p[1]
    cosLat = math.cos(lat)
    return (
        cosLat * math.cos(lng),
        cosLat * math.sin(lng),
        math.sin(lat)
    )


def from_vector(v: Tuple):
    lat = math.atan2(v[2], math.sqrt(v[0]*v[0] + v[1]*v[1]))
    lng = math.atan2(v[1], v[0])
    return (lng, lat)


def cross_product(v0, v1) -> Tuple:
    return (
        v0[1]*v1[2] - v0[2] * v1[1],
        v0[2]*v1[0] - v0[0] * v1[2],
        v0[0]*v1[1] - v0[1] * v1[0],
    )


def path_intersection_lnglat(p1, b1, p2, b2, p3): 
    lng1 = math.radians(p1.lng)
    lat1 = math.radians(p1.lat)
    lng2 = math.radians(p2.lng)
    lat2 = math.radians(p2.lat)
    dLat21 = lat2 - lat1
    dLng21 = lng2 - lng1
    th13 = math.radians(b1)
    th23 = math.radians(b2)
    cosLat1 = math.cos(lat1)
    cosLat2 = math.cos(lat2)
    sinLat1 = math.sin(lat1)
    sinLat2 = math.sin(lat2)
    
    delta12 = 2 * math.asin(math.sqrt(
        math.pow(math.sin(dLat21/2), 2)
        + cosLat1 * cosLat2 * math.pow(math.sin(dLng21/2), 2)
    ))
    cosD12 = math.cos(delta12)
    sinD12 = math.sin(delta12)
    print((sinLat2 - sinLat1 * cosD12) / (sinD12 * cosLat1))
    print(sinLat2, sinLat1, cosD12, sinD12, cosLat1)
    thA = math.acos(
        (sinLat2 - sinLat1 * cosD12) / (sinD12 * cosLat1)
    )
    thB = math.acos(
        (sinLat1 - sinLat2 * cosD12) / (sinD12 * cosLat2)
    )
    if math.sin(dLng21) > 0:
        th12 = thA
        th21 = 2 * math.pi - thB
    else:
        th12 = 2 * math.pi - thA
        th21 = thB
    af1 = th13 - th12
    af2 = th21 - th23

    cosAf1 = math.cos(af1)
    cosAf2 = math.cos(af2)
    sinAf1 = math.sin(af1)
    sinAf2 = math.sin(af2)

    af3 = math.acos( -cosAf1 * cosAf2 + sinAf1*sinAf2*cosD12)
    delta13 = math.atan2(
        sinD12 * sinAf1 * sinAf2,  
        cosAf2 + cosAf1 * math.cos(af3)
    )
    sinD13 = math.sin(delta13)
    cosD13 = math.cos(delta13)
    lat3 = math.asin(
        sinLat1 * cosD13 + cosLat1 * sinD13 * math.cos(th13)
    )
    dLng13 = math.atan2(
        math.sin(th13) * sinD13 * cosLat1,
        cosD13 - sinLat1 * math.sin(lat3)
    )
    lng3 = lng1 + dLng13
    p3.lng = math.degrees(lng3)
    p3.lat = math.degrees(lat3)


def move_lnglat(src, course, dist):
    lng1 = math.radians(src.lng)
    lat1 = math.radians(src.lat)
    r = dist / R
    course = math.radians(course)
    cosR = math.cos(r)
    sinR = math.sin(r)
    sinLat1 = math.sin(lat1)
    cosLat1 = math.cos(lat1)

    lat2 = math.asin(sinLat1 * cosR + cosLat1 * sinR * math.cos(course))
    lng2 = lng1 + math.atan2(math.sin(course) * sinR * cosLat1, cosR - sinLat1 * math.sin(lat2))
    src.lng = math.degrees(lng2)
    src.lat = math.degrees(lat2)


def destination(src, course: float, dist: float):
    lng1 = src[0] * DEG_RADIAN
    lat1 = src[1] * DEG_RADIAN
    r = dist / R
    course = course * DEG_RADIAN
    cosR = math.cos(r)
    sinR = math.sin(r)
    sinLat1 = math.sin(lat1)
    cosLat1 = math.cos(lat1)

    lat2 = math.asin(sinLat1 * cosR + cosLat1 * sinR * math.cos(course))
    lng2 = lng1 + math.atan2(math.sin(course) * sinR * cosLat1, cosR - sinLat1 * math.sin(lat2))
    return (lng2 * RADIAN_DEG, lat2 * RADIAN_DEG)
