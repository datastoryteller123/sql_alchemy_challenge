
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_


from flask import Flask, jsonify

#################################################
# Engine/Session Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f'Available Routes: <br/>'
        f'Precipitation: //api/v1.0/precipitation<br/>'
        f'List of Stations: /api/v1.0/stations<br/>'
        f'One Year Temperature Observation: /api/v1.0/tobs<br/>'
        f'Temperature Statistics from Start Date: /api/v1.0/<start><br/>' 
        f'Temperature Statistics from Start to End Date: /api/v1.0/<start>/<end><br/>'
    )

@app.route('//api/v1.0/precipitation')

def precipitation():
        
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).\
            order_by(measurement.date).all()

    session.close()
    
    prcp_list = []

    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route('//api/v1.0/stations')

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations = {}
    results = session.query(station.station, station.name).all()
    for st,name in results:
        stations[st] = name
    
    session.close()
    return jsonify(stations)

@app.route('//api/v1.0/tobs')

def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    measurement_columns = (measurement.date, measurement.prcp)
    precip_date = session.query(*measurement_columns).\
        filter(measurement.date >= query_date).all()
    
    session.close()

    tobs_list = []

    for date, tobs in precip_date:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route('//api/v1.0/<start>')
def temp_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_list = []

    results = session.query(
        measurement.date,\
            func.min(measurement.tobs),\
            func.avg(measurement.tobs),\
            func.max(measurement.tobs)),\
        filter(measurement.date>= start).\
        group_by(measurement.date).all()
    

    session.close()


    for date, min, avg, max in results:
        start_dict = {}
        start_dict['Date'] = date
        start_dict['Tmin'] = min
        start_dict['TAVG'] = avg
        start_dict['TMAX'] = max
        start_list.append(start_dict)

    return jsonify(start_list)

@app.route('//api/v1.0/<start>/<end>')

def temp_start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(
            measurement.date,\
                func.min(measurement.tobs),\
                func.avg(measurement.tobs),\
                func.max(measurement.tobs)),\
            filter(and_(measurement.date>= start, measurement.date<= end)).\
            group_by(measurement.date).all()
    

    session.close()

    start_end_list = []

    for date, min, avg, max in results:
        start_end_dict = {}
        start_end_dict['Date'] = date
        start_end_dict['Tmin'] = min
        start_end_dict['TAVG'] = avg
        start_end_dict['TMAX'] = max
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)

