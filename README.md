# Weather Underground Caching



### Objective
While weather underground has an API to allow you to get the current weather,
for data analysis purposes it is often desirable to has long term historical
data. This package provives a simple script, run from a cron entry, that can
capture and store weather data points to a database for long term archiving.

The package also will send a text message each time the daily accumulated
precipitation crosses a 1/4" threshold.

### Details
The focus of this implementation has been to acquire data from personal
weather stations. All these stations have an station identifier.

The file stations.txt lists the stations to be tracked and stored in the
database. This file should contain one station id per line.

### Configuration

The following environment variables need to be defined:

* **TWILIO\_ACCOUNT\_SID**, **TWILIO\_AUTH\_TOKEN**, **TWILIO\_FROM**, **TWILIO\_TO** are used for the sending of the rain threshold.
* **DATABASE\_URL** is used to configure the database used. This allows tests to easily reconfigure the database.

Define the station ids you want to track in stations.txt

**Note:** The current logging is set to papertrail and this will need to be changed for it to be useful for someone else.

### Future Work

The next step is to extract the data in a dataframe compatible way.