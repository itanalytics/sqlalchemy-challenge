# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Calculate the date one year from the last date in data set.
    recent_date = recent_date.split('-')
    recent_date = [int(recent_date[i]) for i in range(0,len(recent_date))]
    prior_year = dt.date(recent_date[0],recent_date[1], recent_date[2]) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()
    
    session.close()
    
    prcp_dict = dict(results)

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.id, Station.station).all()

    session.close()

    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    active_station = session.query(Station.id, Measurement.station, func.count(Measurement.tobs))\
    .filter(Station.station == Measurement.station)\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.tobs).desc()).first()[0]
    
    temps = session.query(Measurement.date, Measurement.tobs)\
    .filter(Station.station == Measurement.station)\
    .filter(Station.id == active_station).all()

    session.close()

    temp_list = list(np.ravel(temps))

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start=None, end=None):

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Calculate the date one year from the last date in data set.
    recent_date = recent_date.split('-')
    recent_date = [int(recent_date[i]) for i in range(0,len(recent_date))]
    
    if dt.date(recent_date[0],recent_date[1], recent_date[2]) >= start:

        stats = session.query(func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),1),func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

        session.close()

        temps = list(np.ravel(stats))
        
        return jsonify(temps)
    
    return jsonify({"error": f"Start date not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)