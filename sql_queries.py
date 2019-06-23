import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')


# DROP TABLES
staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"


# CREATE TABLES
staging_events_table_create= ("""
create table if not exists staging_events(
   artist varchar(255),
   auth varchar(100),
   first_name varchar(50),
   gender char(1),
   item_in_session integer,
   last_name varchar(50),
   length decimal,
   level varchar(10),
   location varchar(255),
   method varchar(20),
   page varchar(50),
   registration bigint,
   session_id integer,
   song varchar(500),
   status integer,
   ts bigint sortkey,
   user_agent varchar(500),
   user_id integer
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs(
  num_songs INTEGER,
  artist_id varchar(50) sortkey,
  artist_latitude decimal,
  artist_longitude decimal,
  artist_location varchar(255),
  artist_name varchar(255),
  song_id varchar(50),
  title varchar(500),
  duration decimal,
  year integer
  );
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays(
    songplay_id integer identity(0,1) primary key not null,
    start_time timestamp,
    user_id integer NOT NULL,
    session_id integer,
    level varchar(10),
    song_id varchar(50) NOT NULL,
    artist_id varchar(50) distkey NOT NULL,
    location varchar(255),
    user_agent varchar(500),
	FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (song_id) REFERENCES songs (song_id),
    FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
	)
  	SORTKEY (location)
  ;
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users(
    user_id integer primary key not null,
    first_name varchar(50),
    last_name varchar(50),
    gender varchar(10),
    level varchar(10) not null sortkey
)
diststyle all;
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs(
    song_id varchar(50) primary key not null,
    title varchar(500) sortkey,
    artist_id varchar(50) distkey,
    year integer,
    duration decimal
);
""")

artist_table_create = ("""
CREATE TABLE if not exists artists(
    artist_id varchar(50) distkey primary key not null,
    artist_name varchar(255) sortkey,
    artist_location varchar(255),
    artist_latitude decimal,
    artist_longitude decimal
);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time(
    time_id  integer identity(0,1) primary key,
    start_time timestamp  sortkey not null,
    hour integer not null,
    day integer not null,
    week integer not null,
    month integer not null,
    year integer not null,
    weekday integer not null
)
diststyle even;
""")

# STAGING TABLES
staging_events_copy = ("""
copy staging_events
 from {} 
 iam_role {} 
 json {};
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
copy staging_songs
 from {} 
 iam_role {}
 json 'auto';
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'])


# FINAL TABLES
songplay_table_insert = ("""        
insert into songplays (start_time, user_id, session_id, level, song_id, artist_id, location, user_agent)
       (select distinct timestamp 'epoch' + ts/1000 * interval '1 second' as start_time, 
        user_id, session_id, level, stgs.song_id, stgs.artist_id, location, user_agent
        from staging_events stge 
        left outer join staging_songs stgs on stge.song = stgs.title and stge.artist = stgs.artist_name
        where stge.page='NextSong') ;        
""")

user_table_insert = ("""
insert into users(user_id, first_name, last_name, gender, level) 
(select distinct user_id, first_name, last_name, gender, level from staging_events where user_id is not null);
""")

song_table_insert = ("""
insert into songs(song_id, title, artist_id, year, duration) 
(select distinct song_id, title, artist_id, year, duration from staging_songs);
""")

artist_table_insert = ("""
insert into artists (artist_id, artist_name, artist_location, artist_latitude, artist_longitude) 
(select distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude from staging_songs); 
""")

time_table_insert = ("""
insert into time (start_time, hour, day, week, month, year, weekday) 
	(select distinct timestamp 'epoch' + ts/1000 * interval '1 second' as start_time, 
     date_part(hour, start_time) as hour,
	 date_part(day, start_time) as day,
     date_part(week, start_time) as week,
     date_part(month, start_time) as month, 
     date_part(year, start_time) as year,
     date_part(weekday, start_time) as weekday
	from staging_events
    where ts is not null 
);
""")

# QUERY LISTS
create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
