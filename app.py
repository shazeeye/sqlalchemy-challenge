import numpy as np
import pandas as pd 
import datetime as dt 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc 
from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)




#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    
    return (
        f"<h1>Climate Analysis</h1><br/><br/>"
        f"Available Routes:<br/>"
        """<a href="/api/v1.0/precipitation">/api/v1.0/precipitation (Precipitation for the previous year)</a><br/>"""
        """<a href="/api/v1.0/stations">/api/v1.0/stations (List of stations)</a><br/>"""
        """<a href="/api/v1.0/tobs">/api/v1.0/tobs (Temperature observations for the previous year for station USC00519281)</a><br/>"""
        """<a href="/api/v1.0/&lt;date&gt;">/api/v1.0/<date>(Temperature statistics for given date; provide date in URL in YYYY-MM-DD format where it says 'date')</a><br/>"""
        """<a href="/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;">/api/v1.0/<start_date>/<end_date>(Temperature statistics for given date range; provide start and end date in URL in YYYY-MM-DD format where it says 'start date' and 'end_date')</a><br/>"""
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date from the last data point in the database
    latestdate=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date 1 year ago from the last data point in the database
    yearago = dt.date(2017, 8, 23) - dt.timedelta(days=365.25)
    
    
    # Perform a query to retrieve the date and precipitation scores
    lastyear_precipitation=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=yearago).all()
    
    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    all_station_prcp = []

    for row in lastyear_precipitation:
        row_dict = {}
        row_dict["date"] = row.date
        row_dict["precipitation"] = row.prcp
        all_station_prcp.append(row_dict)
    #Return the JSON representation of your dictionary.

    return jsonify(all_station_prcp)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    
    names_stations=session.query(Measurement.station).group_by(Measurement.station).order_by(Measurement.station).all()
    
    # Create a dictionary from the row data and append to a list of stations
    
    all_station = []

    for row in names_stations:
        row_dict = {}
        row_dict["station name"] = row.station
        all_station.append(row_dict)

    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def temp_obs():
    """Return a list of temperature observation in the station with highest number of observations"""
    station_count = session.query(Measurement.station, func.count(Measurement.station).label('count')).group_by(Measurement.station).order_by(desc('count')).all()
    mostactivestation=station_count[0][0]
    #Query the last 12 months of temperature observation data for this station
    
    yearago = dt.date(2017, 8, 23) - dt.timedelta(days=365.25)
    station_temp_count = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station==mostactivestation).filter(Measurement.date >= yearago).all()
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    
    all_temp_obs = []
    
    for row in station_temp_count:
        row_dict = {}
        row_dict["date"] = row.date
        row_dict["temperature observation for USC00519281"] = row.tobs
        all_temp_obs.append(row_dict)

    return jsonify(all_temp_obs)


@app.route("/api/v1.0/<date>")
def temp_info(date):
    """Return minimum, maximum and average temperature for all dates higher than date"""
    temp_info=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()


    # Create a dictionary from the row data and append to a list 
    all_temp_info = []
    
    for row in temp_info:
        row_dict = {}
        row_dict["minimum temperature"] = row[0]
        row_dict["maximum temperature"] = row[2]
        row_dict["average temperature"] = row[1]
        all_temp_info.append(row_dict)

    return jsonify(all_temp_info)
"""Return minimum, maximum and average temperature for all dates from start to end date"""
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_information(start_date, end_date):
    temp_information=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    all_temp_information = []
        
    for row in temp_information:
        row_dict = {}
        row_dict["minimum temperature"] = row[0]
        row_dict["maximum temperature"] = row[2]
        row_dict["average temperature"] = row[1]
        all_temp_information.append(row_dict)

    return jsonify(all_temp_information)

if __name__ == '__main__':
    app.run(debug=True)