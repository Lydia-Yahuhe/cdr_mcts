from math import *
from rtree import index
import math

R = 6371393.0  # m
DEG_RADIAN = pi / 180.0
RADIAN_DEG = 180.0 / pi
G0 = 0.982
epsilon = 7.0 / 3 - 4.0 / 3 - 1.0
KM2M = 1000.0
M2KM = 1.0 / KM2M


def search_100_km(points, pos):
    lst = []
    for p in points:
        if distance(pos, p) <= 100 * KM2M:
            lst += [(p[0]-110)/30, (p[1]-35)/15]

    lst += [0.0 for _ in range(4)]
    return lst[:4]


def distance_point2d(d0, d1):
    lng0 = radians(d0.lng)
    lat0 = radians(d0.lat)
    lng1 = radians(d1.lng)
    lat1 = radians(d1.lat)
    dlng = lng0 - lng1
    dlat = lat0 - lat1
    tmp1 = sin(dlat / 2)
    tmp2 = sin(dlng / 2)
    a = tmp1 * tmp1 + cos(lat0) * cos(lat1) * tmp2 * tmp2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def distance(c0, c1):
    lng0 = c0[0] * DEG_RADIAN
    lat0 = c0[1] * DEG_RADIAN
    lng1 = c1[0] * DEG_RADIAN
    lat1 = c1[1] * DEG_RADIAN
    dlng = lng0 - lng1
    dlat = lat0 - lat1
    tmp1 = sin(dlat / 2)
    tmp2 = sin(dlng / 2)
    a = tmp1 * tmp1 + cos(lat0) * cos(lat1) * tmp2 * tmp2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def bearing_point2d(d0, d1):
    lng0 = radians(d0.lng)
    lat0 = radians(d0.lat)
    lng1 = radians(d1.lng)
    lat1 = radians(d1.lat)
    dlng = lng1 - lng0
    coslat1 = cos(lat1)
    tmp1 = sin(dlng) * coslat1
    tmp2 = cos(lat0) * sin(lat1) - sin(lat0) * coslat1 * cos(dlng)
    return (atan2(tmp1, tmp2) * RADIAN_DEG) % 360


def bearing(c0, c1):
    lng0 = c0[0] * DEG_RADIAN
    lat0 = c0[1] * DEG_RADIAN
    lng1 = c1[0] * DEG_RADIAN
    lat1 = c1[1] * DEG_RADIAN
    dlng = lng1 - lng0
    coslat1 = cos(lat1)
    tmp1 = sin(dlng) * coslat1
    tmp2 = cos(lat0) * sin(lat1) - sin(lat0) * coslat1 * cos(dlng)
    return (atan2(tmp1, tmp2) * RADIAN_DEG) % 360


def intersection(a0, a1):
    c = (a0 - a1) % 360
    if c > 180:
        return c - 360
    return c


def move_point2d(src, course, dist):
    lng1 = radians(src.lng)
    lat1 = radians(src.lat)
    r = dist / R
    course = radians(course)
    cosR = cos(r)
    sinR = sin(r)
    sinLat1 = sin(lat1)
    cosLat1 = cos(lat1)

    lat2 = asin(sinLat1 * cosR + cosLat1 * sinR * cos(course))
    lng2 = lng1 + atan2(sin(course) * sinR * cosLat1, cosR - sinLat1 * sin(lat2))
    src.lng = degrees(lng2)
    src.lat = degrees(lat2)


def destination(src, course: float, dist: float):
    lng1 = src[0] * DEG_RADIAN
    lat1 = src[1] * DEG_RADIAN
    r = dist / R
    course = course * DEG_RADIAN
    cosR = cos(r)
    sinR = sin(r)
    sinLat1 = sin(lat1)
    cosLat1 = cos(lat1)

    lat2 = asin(sinLat1 * cosR + cosLat1 * sinR * cos(course))
    lng2 = lng1 + atan2(sin(course) * sinR * cosLat1, cosR - sinLat1 * sin(lat2))
    return lng2 * RADIAN_DEG, lat2 * RADIAN_DEG


def make_bbox(pos, ext=(0, 0, 0)):
    return (pos[0] - ext[0], pos[1] - ext[1], pos[2] - ext[2],
            pos[0] + ext[0], pos[1] + ext[1], pos[2] + ext[2])


def make_bbox_2d(pos, ext=(0, 0)):
    return (pos[0] - ext[0], pos[1] - ext[1],
            pos[0] + ext[0], pos[1] + ext[1])


def position_in_bbox(bbox, p):
    check = range(10)
    x = int((p[0] - bbox[0]) / 0.1) in check
    y = int((p[1] - bbox[1]) / 0.1) in check
    z = int((p[2] - bbox[2]) / 300) in check
    return x+y+z >= 3


def build_rt_index(agents):
    p = index.Property()
    p.dimension = 3
    idx = index.Index(properties=p)
    for i, a in enumerate(agents):
        idx.insert(i, make_bbox(a[1:]))
    return idx


def mid_position(pos0, pos1):
    return (
        (pos0[0] - pos1[0]) / 2 + pos1[0],
        (pos0[1] - pos1[1]) / 2 + pos1[1],
        (pos0[2] - pos1[2]) / 2 + pos1[2])


def format_time(t):
    return '%02d:%02d:%02d:%02d' % (int(t / 24 / 3600), int(t / 3600) % 24, int(t / 60) % 60, int(t) % 60)


def equal(list_a, list_b):
    if len(list_a) != len(list_b):
        return False

    return sum([a not in list_b for a in list_a]) <= 0


def center(locations):
    x, y, z, length = 0, 0, 0, len(locations)
    sum_alt = 0
    for lon, lat, alt in locations:
        lon = radians(float(lon))
        lat = radians(float(lat))

        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)
        sum_alt += alt

    x = float(x / length)
    y = float(y / length)
    z = float(z / length)
    alt = float(sum_alt / length)

    return (degrees(atan2(y, x)), degrees(atan2(z, sqrt(x * x + y * y))), alt)


# 已知三个点的坐标，计算其三角形面积
def area(a, b, c):
    ab = distance(a, b)
    ac = distance(a, c)
    bc = distance(b, c)
    p = (ab + ac + bc) / 2
    S = math.sqrt(abs(p * (p - ab) * (p - ac) * (p - bc)))

    return S


# 已知三个点的坐标，计算a点到bc的距离
def high(a, b, c):
    S = area(a, b, c)
    return 2 * S / distance(b, c)


def generation(x, min_v, max_v):
    return (x - min_v) / (max_v - min_v)


def generation_point(point):
    return [generation(point[0], 72, 135),
            generation(point[1], 16, 55),
            generation(point[2], 6000, 12000)]
