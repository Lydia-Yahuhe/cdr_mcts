import pymongo
import numpy as np
from tqdm import tqdm

from fltsim.geom import Point2D
from fltsim.model import Waypoint, Routing, Aircraft, aircraftTypes, FlightPlan, DataSet, ConflictSceneInfo


def load_waypoint(db):
    wpts = {}
    cursor = db['Waypoint'].find()
    for pt in cursor:
        wpt = Waypoint(id=pt['id'], location=Point2D(pt['point']['lng'], pt['point']['lat']))
        wpts[wpt.id] = wpt

    cursor = db["Airport"].find()
    for pt in cursor:
        wpt = Waypoint(id=pt['id'], location=Point2D(pt['location']['lng'], pt['location']['lat']))
        wpts[wpt.id] = wpt

    return wpts


def load_routing(db, wpts):
    ret = {}
    cursor = db['Routing'].find()
    for e in cursor:
        wptList = [wpts[e["departureAirport"]]]
        for wptId in e['waypointList']:
            wptList.append(wpts[wptId])
        wptList.append(wpts[e["arrivalAirport"]])
        r = Routing(e['id'], wptList)
        ret[r.id] = r

    return ret


def load_aircraft(db):
    ret = {}
    cursor = db['Aircraft'].find()
    for e in cursor:
        info = Aircraft(id=e['id'], aircraftType=aircraftTypes[e['aircraftType']])
        ret[info.id] = info

    return ret


def load_flight_plan(db, aircraft, routes):
    ret = {}
    cursor = db['FlightPlan'].find()
    for e in cursor:
        a = aircraft[e['aircraft']]

        fpl = FlightPlan(
            id=e['id'],
            RFL=0,
            routing=routes[e['routing']],
            startTime=e['startTime'],
            aircraft=a,
            alt=e['flightLevel']
        )

        ret[fpl.id] = fpl

    return ret


def load_data_set():
    connection = pymongo.MongoClient('localhost')
    database = connection['admin']

    wpts = load_waypoint(database)
    aircrafts = load_aircraft(database)
    routes = load_routing(database, wpts)
    fpls = load_flight_plan(database, aircrafts, routes)

    connection.close()
    return DataSet(wpts, routes, fpls, aircrafts)


routings = load_data_set().routings
database = pymongo.MongoClient('localhost')['admin']


# 数据库加载train_data
def load_train_data():
    # scenes = load_data(database['train_data'])
    # return load_data(database['test_data'])
    return load_data(database['train_data_new'], shuffle=False, all_=True)


# 数据库加载test_data
def load_test_data():
    return load_data(database['test_data'])


# 数据库加载validate_data
def load_validate_data():
    # return load_data(database['validate_data'])
    return load_data(database['test_data_new'], shuffle=True, all_=True)


def load_data(collection, shuffle=False, all_=False):
    scenes = []
    data = list(collection.find())
    for i in tqdm(range(len(data)), desc='Load Data'):
        e: dict = data[i]
        conflict_ac, clock, pos = e['conflict_ac'], e['time'], e['pos']

        fpl_list = []
        for f in e['fpl_list']:
            # aircraft
            ac = Aircraft(id=f['aircraft'], aircraftType=aircraftTypes[f['type']])

            # routing
            routing = routings[f['route']]
            wpt_list = routing.waypointList[f['startLeg']:]
            routing = Routing(id=routing.id, waypointList=wpt_list, start=f['startLeg'])

            # fpl
            fpl = FlightPlan(id=f['id'], aircraft=ac, routing=routing, startTime=f['start'],
                             RFL=f['RFL'], alt=f['alt'])
            fpl_list.append(fpl)

        if not all_ and len(conflict_ac) < 5:
            continue

        scenes.append(dict(id=e['id'], time=clock, conflict_ac=conflict_ac, pos=pos,
                           fpl_list=fpl_list, origin=e['fpl_list']))

    if shuffle:
        np.random.shuffle(scenes)
    return scenes
