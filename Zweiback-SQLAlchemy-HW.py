from matplotlib import style
import matplotlib.pyplot as plt

# import Flask 
from flask import Flask, jsonify, request
import numpy as np
import pandas as pd

# Create Flask app
app = Flask(__name__)


import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[5]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# In[6]:


# Use SQLAlchemy create_engine to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# In[7]:


# Use SQLAlchemy automap_base() to reflect the database tables into classes
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[8]:


# We can view all of the classes that automap found - keys are the column headings
Base.classes.keys()


# In[9]:


# Save a reference to each table/classes called Station and Measurement
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[10]:


# Create our session (link) from Python to the DB
session = Session(engine)


# In[11]:


#Choose start date and end date for trip. Vacation range is 3 - 15 days
Trip_Start_Date = '2019-07-01'
Trip_End_Date = '2019-07-15'


# # Exploratory Climate Analysis

# In[12]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results


# In[13]:


# Calculate the date 1 year ago from the last data point in the database
year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
print("Date one year ago from last data point in the database is:", year_ago_date)


# In[14]:


# Perform a query to retrieve the data and precipitation scores
# Select only the date and prcp values from the Measurement database
Last12prcp = session.query(Measurement.date, 
                         Measurement.prcp).\
                         filter(Measurement.date >= "2016-08-23").filter(Measurement.date <="2017-08-23").all()
Last12prcp


# In[15]:


# Save the query results as a Pandas DataFrame and set the index to the date column
#Last12prcp_df = pd.DataFrame(Last12prcp, columns=['date','percipitation'])
#Last12prcp_df.set_index('date', inplace=True)
#Last12prcp_df.head()


# In[16]:


# Save the query results as a Pandas DataFrame and set the index to the date column
Last12prcp_df = pd.DataFrame(Last12prcp)
Last12prcp_df['date'] = pd.to_datetime(Last12prcp_df['date'])
Last12prcp_df = Last12prcp_df.set_index('date')
Last12prcp_df.rename(columns = {'prcp': 'precipitation'}, inplace=True)
Last12prcp_df.head()


# In[17]:


# Plot the results using the DataFrame plot method
# Use Pandas Plotting with Matplotlib to plot the data
Last12prcp_df.plot(figsize=(20, 8),
                  sort_columns=True,
                  rot=45,
                  use_index=True,
                  title='Percipitation in Hawaii from 08-23-2016 to 08-23-2017',
                  legend=True,
                  fontsize=12,
                  grid=True,
                   
                  )
plt.xlabel("Date")
plt.show()
plt.savefig("Percipitation Analysis_12months.png")


# In[18]:


# Use Pandas to calculate and print the summary statistics for the precipitation data.
Last12prcp_df.describe()


# ### Station Analysis

# In[19]:


# Design a query to show how many stations are available in this dataset?
NumStations = session.query(Station.id).count()
NumStations


# In[20]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
station_rows = session.query(Measurement.station, Station.name, func.count(Measurement.station)).               filter(Measurement.station == Station.station).               group_by(Measurement.station).               order_by(func.count(Measurement.station).desc()).all()
station_rows


# In[21]:


# Using the station id from the previous query calculate the lowest temperature recorded, highest temperature recorded,
# and average temperature most active station?

most_active_station = station_rows[0][0]
station_calculations = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).                                    filter(Measurement.station == most_active_station).all()
station_calculations


# In[27]:


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram

highest_tobs = session.query(Measurement.station, Measurement.tobs).    filter(Measurement.station == most_active_station, Measurement.station == Station.station).    filter(Measurement.date >= year_ago_date).all()
highest_tobs


# In[59]:


#tobs_df = pd.DataFrame(highest_tobs, columns=['station', 'tobs'])
#tobs_df.set_index('station', inplace=True)
#tobs_df.head()


# In[87]:


# Plot the results in a Histogram
temp = [temp[0] for temp in highest_tobs]
plt.hist(temp, bins=12)
#tobs_df.plot.hist(highest_tobs, bins=12)
plt.title("Temperature Observations for Station for Most Active Station")
plt.xlabel("Temperatures")
plt.ylabel("Frequency")
plt.legend("tobs")
plt.show
plt.savefig("Station Temperatures.png")


# In[79]:


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))


# In[82]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
trip_startdate = dt.date(2018, 7, 1)
trip_enddate = dt.date(2018, 7, 15)
previous_year = dt.timedelta(days=365)
previous_year_temps = calc_temps(trip_startdate-previous_year, trip_enddate-previous_year)
print(previous_year_temps)

min_temp, avg_temp, max_temp = previous_year_temps[0]
print(min_temp, avg_temp, max_temp)


# In[114]:


# Option 2
# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)

yerr = max_temp - min_temp
fig, ax = plt.subplots(figsize=plt.figaspect(2.))
bar = ax.bar(1, avg_temp, yerr=yerr, align = "center", color='salmon')
# DAMITA COME BACK TO THIS
#ax.set(xticks=range(xpos),title = "Trip Avg Temp", ylabel = "Temp(F)")
plt.savefig("Temp Analysis 2017.png")
plt.show


# In[123]:


# Calculate the rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation

rainfall_station = session.query(Measurement.station, Station.name, func.sum(Measurement.prcp).label('precipitation')).filter(Measurement.station == Station.station, Measurement.date >= trip_startdate, Measurement.date <= trip_enddate).group_by(Measurement.station).order_by(func.sum(Measurement.prcp).desc()).all()
rainfall_station


# ## Optional Challenge Assignment

# In[124]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")


# In[127]:


# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip

# Use the start and end date to create a range of dates

# Stip off the year and save a list of %m-%d strings

# Loop through the list of %m-%d strings and calculate the normals for each date


# In[ ]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index


# In[ ]:


# Plot the daily normals as an area plot with `stacked=False`



# PART 2 STUFF

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f""
        f""
    )


@app.route("/api/v1.0/precipitation")
def precip():
    
    #RECREATES database session
    session = Session(engine)

    # write a query to return precipitation
    Last12prcp = session.query(Measurement.date, 
                         Measurement.prcp).\
                         filter(Measurement.date >= "2016-08-23").filter(Measurement.date <="2017-08-23").all()


    # replace all_names with the object that precipitation data is stored in
    return jsonify(Last12prcp)



@app.route("/api/v1.0/station")
def precip():
    
    #RECREATES database session
    session = Session(engine)

    # write a query to return station

    # replace all_names with the object that precipitation data is stored in
    return jsonify(station)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)

