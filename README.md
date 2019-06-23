## About Sparkify
A music streaming startup, Sparkify, has grown their user base and song database and wants to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

Sparkify wants to analyze how the Sparkify app is used by their users to gain insights on the songs their users are listening to. Having the song play data in a analytical data warehouse enables them to analyze the data easily and quickly.


## Project Goals
Build an ETL pipeline that extracts Sparkify's data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights from song plays in the app.


## Project Summary
The goal of this project was to design the tables in a data warehouse (Redshift) for song play analysis and build an ETL pipeline to populate these tables from log data and songs data provided on AWS S3.

The input datasets were json files containing songs and artists information and log files containing events arising from Sparkify's customers playing songs in the Sparkify application.

This project involved working with Amazon Web Services and learning how to launch a Redshift Cluster and connect to it remotely to perform ETL and ananylis and populate tables using data in S3.

### Schema Design
For the ETL pipeline, created two staging tables in Redshift to hold the data before transforming the data into a suitable form for analysis.
  - staging_events - contains the data from the log_data files on S3. The columns in the table map one one one with the columns in log files.
  - staging_songs - contains the data from the song_data files on S3. The columns in the table map one on one with the attributes in the song data files.

To analyze song plays by Sparkify's customers, created a database with star schema design composed of the following tables
  - songplays : A Transactional fact table that records facts about a song play by a Sparkify customer. Populated from staging events and staging songs.
  - songs - Dimension table representing songs data. Populated from staging_songs table.
  - artists - Dimension table capturing artists data. Populated from staging_songs table.
  - time - Dimension table capturing time information related to song plays. Populated by transforming the timestamp information log data in staging_events table.
  - users - Dimension table capturing data on Sparkify's users. Populated from the users information in staging_events table.

| Table Name   | Table Columns | Distribution Style | Dist Key | Sort Key       |
| :----------- | :------------ | :----------------- | :------- | :------------- |
| songplays | songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent  | Key | artist_id | location |
| songs   | song_id, title, artist_id, year, duration  | Key | artist_id | title
| artists | artist_id, artist_name, artist_location, artist_latitude, artist_longitude | Key | artist_id |  artist_name|
| users   | user_id, first_name, last_name, gender, level | All | None | Level |
| time    | time_id, start_time, hour, day, week, month, year, weekday | Even| None | start_time |   


I chose artist_id as the distribution key on songplays, songs and artists to make queries related to finding insights on which artists more performant.

The users table has 105 records so it is a good fit for distributing on every node, so I went with the dist style All.

The time table can be evenly distributed as the data contained in that table is different by only days.  So there is not much benefit on distributing on a day dimension.

### ETL
Source data for songs and log files was made available through S3 at these two locations -   
- Song Data - s3://udacity-dend/song_data  
- Log Data - s3://udacity-dend/log_data

There were two types of files -
- Song Dataset - Each file in in json and contains information about a single song. They are arranged in a folder structure based on the song's tracking id.
- Log Dataset - The log files in the dataset are partitioned by year and month. They are named as YYYY-MM-DD-events.json. These files contain the data for a song play event. Each record contains the timestamp of the event, the user who is playing the song, session id of the user, location of the user, type of user - paid/free,  song played by the user, artist for the song, length of the song etc. A valid song play event is the one with page=NextSong.


## Process
Perform ETL by populating the staging tables (stagng_events, staging_songs) by bulk loading data from the S3 files using Redhsift's COPY commands.

Transform the data in staging tables to make them suitable for songplay analysis. As part of this step, the five tables for analysis are populated from the data in staging_songs and staging_events tables.

All credentials required for connecting to S3 and to Reshift cluster are specified through dwh.cfg configuration file.


## Project Files
  - dwh.cfg - Contains the connection information for Redshift cluster, S3 location for data file sand IAM role used by the Redshift cluster to pull data from S3.
  - sql_queries.py : contains the sql queries for
    - creating and dropping staging and analysis tables
    - copy queries for loading data from S3 to Redshift
    - insert queries for populating the analysis tables.
  - create_tables.py  - contains helper methods for calling the individual queries from sql_queries.py for creating and dropping tables. This is useful for restting the state of the database.
  - etl.py - contains code for ETL process to load data in staging tables and insert data into analysis tables.


## Running the scripts
  Before running etl.py, wipe out the tables in Sparkfy database and recreate the dimension and fact tables and the database. Use  python create_tables.py to do this.

  Next run python etl.py to load data into staging tables from S3 and populate the analysis tables.

## Queries
### Number of songs played by day by artist  
select t.year, t.month, t.day, a.artist_name, count(*) as num_songs_played_per_day_by_artist
from songplays sp
inner join time t on sp.start_time=t.start_time
inner join artists a on sp.artist_id=a.artist_id
group by t.year, t.month, t.day, a.artist_name
order by num_songs_played_per_day_by_artist desc;   

Most popular artist is Dwight Yoakam and users listened to him 5 times on Nov 15, 2018.

### Top 5 locations where Sparkify app is used
select location, count(*) as cnt_songs_played_by_location
from songplays
group by location
order by cnt_songs_played_by_location desc limit 5;

- San Francisco-Oakland-Hayward, CA, 691  
- Portland-South Portland, ME, 665  
- Lansing-East Lansing, MI, 557  
- Chicago-Naperville-Elgin, IL_IN_WI, 475  
- Atlanta-Sandy Springs-Roswell, GA, 456


### Top 5 Paid Users
select u.first_name, u.last_name, count(*) as count_songplays_by_user
from songplays sp
inner join users u on sp.user_id=u.user_id
where sp.level='paid'
group by u.first_name, u.last_name  
order by count_songplays_by_user desc limit 5;

- Chloe	Cuevas, 	689  
- Tegan	Levine, 	665  
- Kate	Harrell,	557  
- Lily	Koch, 	    463  
- Aleena Kirby, 	397  

### Top 5 Free Users
select u.first_name, u.last_name, count(*) as count_songplays_by_user
from songplays sp
inner join users u on sp.user_id=u.user_id
where sp.level='free'
group by u.first_name, u.last_name
order by count_songplays_by_user desc limit 5;

- Ryan	Smith,	 114
- Lily	Burns,	 56
- Jayden Fox, 55
- Ava Robinson,	53
- Aiden	Hess,	45

### Top 10 popular songs
select s.title, a.artist_name, count(*) as num_popular_songs
from songplays sp
inner join songs s on sp.song_id=s.song_id
inner join artists a on sp.artist_id=a.artist_id
group by s.title, a.artist_name
order by num_popular_songs desc limit 10;

|title | 	artist_name|	num_popular_songs |
|------|-----|-----|
You're The One| 	Dwight Yoakam| 	37 |
Catch You Baby (Steve Pitron & Max Sanna Radio Edit)|Lonnie Gordon|9 |
I CAN'T GET STARTED| Ron Carter|9 |
Nothin' On You [feat. Bruno Mars] (Album Version)|B.o.B|8 |
Hey Daddy (Daddy's Home)|Usher featuring Jermaine Dupri|6 |
Hey Daddy (Daddy's Home)|Usher|	6 |
Up Up & Away|Kid Cudi|	5|
Make Her Say|	Kid Cudi / Kanye West / Common|	5 |
Up Up & Away|	Kid Cudi / Kanye West / Common|	5 |
Make Her Say|	Kid Cudi|	5 |
