# Import dependencies
import requests
import json
import pandas as pd

## Connecting to the database
import mysql.connector as mysql
from decimal import Decimal
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from pandas.io import sql

url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

def extract_transform_load(): 

    db = mysql.connect(
        host = "127.0.0.1",
        user = "root",
        passwd = "root"
    )
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS natural_disasterdb")
    cursor.execute("CREATE DATABASE IF NOT EXISTS natural_disasterdb")
    cursor.execute("USE natural_disasterdb")

    # cursor.execute("DROP TABLE IF EXISTS earthquakes")
    # cursor.execute("DROP TABLE IF EXISTS tornadoes")
    # cursor.execute("DROP TABLE IF EXISTS hail")
    # cursor.execute("DROP TABLE IF EXISTS wind")
    # cursor.execute("DROP TABLE IF EXISTS tsunamis")
    # cursor.execute("DROP TABLE IF EXISTS volcanoes")

    engine = create_engine('mysql+pymysql://root:root@127.0.0.1/natural_disasterdb', echo=False)

    # Response
    response = requests.get(url).json()

    # Write json file from api call
    with open('all_earthquakes.json', 'w') as json_file:  
        json.dump(response, json_file)

    with open('all_earthquakes.json', 'r') as JSON:
        dict = json.load(JSON)
    
    earthquake_dict = []
    earthquakes = response["features"]
    
    def is_valid(r):
        return (
        r["properties"]['mag'] != None and
        r["properties"]['place'] != None and
        r["properties"]['time'] != None and
        r["properties"]['tz'] != None and
        r["properties"]['url'] != None and
        r["properties"]['tsunami'] != None and
        r["properties"]['ids'] != None and
        r["properties"]['type'] != None and
        r["properties"]['title'] != None and
        r["geometry"]['coordinates'][0] != None and
        r["geometry"]['coordinates'][1] != None and
        r["geometry"]['coordinates'][2] != None)

    def create_dict(r):
        return {
        "magnitude": r["properties"]['mag'],
        "place": r["properties"]['place'],
        "time": r["properties"]['time'],
        "timezone": r["properties"]['tz'],
        "url": r["properties"]['url'],
        "tsunami": r["properties"]['tsunami'],
        "ids": r["properties"]['ids'],
        "specific_type": r["properties"]['type'], 
        "geometry": r["properties"]['title'],
        "lat": r["geometry"]['coordinates'][0],
        "lng": r["geometry"]['coordinates'][1],
        'depth': r["geometry"]['coordinates'][2]
        }

    for r in earthquakes:
        if is_valid(r):
            transformed_dict = create_dict(r)
            earthquake_dict.append(transformed_dict)

            # cleans up the ids column removes commas
    for i in earthquake_dict: 
        value = i["ids"]
        formated_value = value.replace(',', '')
        i["ids"] = formated_value

    ## creating an instance of 'cursor' class which is used to execute the 'SQL' statements in 'Python'


    #################################################
    # CREATE TABLES
    #################################################
    cursor.execute("CREATE TABLE IF NOT EXISTS earthquakes (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, magnitude VARCHAR(255), place VARCHAR(255), time VARCHAR(255), timezone VARCHAR(255), url VARCHAR(255), tsunami INT(1), ids VARCHAR(255), specific_type VARCHAR(255), geometry VARCHAR(255), country_de varchar(80), lng DECIMAL(10, 6), lat DECIMAL(10,6), depth DECIMAL(6,2)) ENGINE=InnoDB")
    
    # Create table tornadoes table
    cursor.execute("CREATE TABLE IF NOT EXISTS tornadoes (tb_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, id INT(11), year INT(4), month INT(4), day  INT(4), date VARCHAR(255), time VARCHAR(255), timezone INT(2), state VARCHAR(255), state_fips INT(2), state_nbr INT(4), mag INT(2), injuries INT(4), deaths INT(4), damage DECIMAL(20, 10), crop_loss DECIMAL(20, 10) ,s_lat DECIMAL(10, 6), s_lng DECIMAL(10, 6), e_lat DECIMAL(10, 6), e_lng DECIMAL(10, 6), length_traveled DECIMAL(10, 6), width INT(5), nbr_states_affected INT(2), sn INT(2), sg INT(2), fa INT(4), fb INT(4), fc INT(4), fd INT(4), fe INT(2)) ENGINE=InnoDB")
    
    # Create table hail table
    cursor.execute("CREATE TABLE IF NOT EXISTS hail (tb_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, id INT(11), year INT(4), month INT(4), day  INT(4), date VARCHAR(255), time VARCHAR(255), timezone INT(2), state VARCHAR(255), state_fips INT(2), state_nbr INT(4), mag DECIMAL(5,2), injuries INT(4), deaths INT(4), damage DECIMAL(15, 1), crop_loss DECIMAL(15, 1), s_lat DECIMAL(10, 6), s_lng DECIMAL(10, 6), e_lat DECIMAL(10, 6), e_lng DECIMAL(10, 6), fa INT(4)) ENGINE=InnoDB")
    
    # Create table earthquake wind
    cursor.execute("CREATE TABLE IF NOT EXISTS wind (tb_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, id INT(11), year INT(4), month INT(4), day  INT(4), date VARCHAR(255), time VARCHAR(255), timezone INT(2), state VARCHAR(255), state_fips INT(2), state_nbr INT(4), mag DECIMAL(5,2), injuries INT(4), deaths INT(4), damage DECIMAL(15, 1), crop_loss DECIMAL(15, 1), s_lat DECIMAL(10, 6), s_lng DECIMAL(10, 6), e_lat DECIMAL(10, 6), e_lng DECIMAL(10, 6), fa INT(4), mag_type VARCHAR(255))ENGINE=InnoDB")
    
    # Create table tsunamis table
    cursor.execute("CREATE TABLE IF NOT EXISTS tsunamis (tb_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, year INT(4), month INT(4), day  INT(4), hour INT(4), min INT(4), second INT(4), validity VARCHAR(255), source VARCHAR(255), earthquake_mag DECIMAL(5,2), country VARCHAR(255), name VARCHAR(255), lat DECIMAL(10, 6), lng DECIMAL(10, 6), water_height DECIMAL(10,2), tsunami_mag_lida DECIMAL(4,1), tsunami_intensity DECIMAL(4,1), death_nbr INT(8), injuries_nbr INT(8), damage_mill DECIMAL(10,3), damage_code INT(2), house_destroyed INT(8), house_code INT(2))ENGINE=InnoDB")
    
    # Create table volcanoes table
    cursor.execute("CREATE TABLE IF NOT EXISTS volcanoes (tb_id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, year INT(4), month INT(4), day  INT(4), tsu INT(4), eq INT(4), name VARCHAR(255), location VARCHAR(255), country VARCHAR(255), lat DECIMAL(10, 6), lng DECIMAL(10, 6), elevation DECIMAL(8,2), type VARCHAR(255), volcanic_index INT(2), fatality_cause VARCHAR(255), death INT(6), death_code INT(1), injuries INT(6), injuries_code INT(1), damage DECIMAL(8, 4), damage_code INT(1), houses INT(5), houses_code INT(1))ENGINE=InnoDB")

    #################################################
    # LOAD EARTHQUAKE TABLE
    #################################################
    earthquake_values = []
    def r_listify(v):
        return v["magnitude"], v["place"], v["time"], v["timezone"], v["url"], v["tsunami"], v["ids"], v["specific_type"],  v["geometry"], v["lng"], v["lat"], v["depth"]

    for v in earthquake_dict:
        entry_tuple = r_listify(v)
        earthquake_values.append(entry_tuple) 
    
    ## defining the Query
    query = "INSERT INTO earthquakes (magnitude, place, time, timezone, url, tsunami, ids, specific_type, geometry, lng, lat, depth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    ## storing values in a variable
    values = earthquake_values

    ## executing the query with values
    cursor.executemany(query, values)
    
    #country_de column: use case statement to decode geometry column
    cursor.execute("update earthquakes set country_de =\
      case when trim(upper(substring_index(geometry, ',', -1))) = 'AL' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'AK' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'AZ' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'AR' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'CA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'CO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'CT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'DE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'DC' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'FL' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'GA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'HI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ID' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'IL' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'IN' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'IA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'KS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'KY' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'LA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ME' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MD' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MN' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NV' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NH' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NJ' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NM' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NY' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NC' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ND' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OH' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OK' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OR' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'PA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'RI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'SC' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'SD' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'TN' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'TX' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'UT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'VT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'VA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WV' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WY' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'PR' then 'United States'     \
           when trim(upper(substring_index(geometry, ',', -1))) = 'ALABAMA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ALASKA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ARIZONA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ARKANSAS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'CALIFORNIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'COLORADO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'CONNECTICUT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'DELAWARE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'DISTRICT OF COLUMBIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'FLORIDA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'GEORGIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'HAWAII' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'IDAHO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'ILLINOIS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'INDIANA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'IOWA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'KANSAS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'KENTUCKY' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'LOUISIANA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MAINE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MARYLAND' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MASSACHUSETTS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MICHIGAN' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MINNESOTA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MISSISSIPPI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MISSOURI' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'MONTANA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEBRASKA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEVADA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEW HAMPSHIRE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEW JERSEY' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEW MEXICO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NEW YORK' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NORTH CAROLINA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'NORTH DAKOTA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OHIO' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OKLAHOMA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'OREGON' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'PENNSYLVANIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'RHODE ISLAND' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'SOUTH CAROLINA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'SOUTH DAKOTA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'TENNESSEE' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'TEXAS' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'UTAH' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'VERMONT' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'VIRGINIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WASHINGTON' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WEST VIRGINIA' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WISCONSIN' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'WYOMING' then 'United States'\
           when trim(upper(substring_index(geometry, ',', -1))) = 'PUERTO RICO' then 'United States' \
           when trim(upper(substring_index(geometry, ',', -1))) = 'MX' then 'Mexico'\
           when geometry like '%Off the coast of Oregon%' then 'Off the coast of Oregon'\
           when geometry like '%Carlsberg Ridge%' then 'Carlsberg Ridge'\
           when geometry like '%South of the Fiji Islands%' then 'South of the Fiji Islands'\
           when geometry like '%Kuril Islands%' then 'Kuril Islands'\
           when geometry like '%Fiji region%' then 'Fiji region'  \
           when geometry like '%Northern Mid-Atlantic Ridge%' then 'Northern Mid-Atlantic Ridge'  \
           when geometry like '%Southern Mid-Atlantic Ridge%' then 'Southern Mid-Atlantic Ridge'\
           when geometry like '%West Chile Rise%' then 'West Chile Rise'\
           when geometry like '%Central Mid-Atlantic Ridge%' then 'Central Mid-Atlantic Ridge'\
           when geometry = 'M 3.7 - Gulf of Alaska' then 'Gulf of Alaska'\
           when geometry = 'M 4.0 - Banda Sea' then 'Banda Sea'\
           when geometry = 'M 4.2 - North Atlantic Ocean' then 'North Atlantic Ocean'\
           when geometry = 'M 4.3 - Western Indian-Antarctic Ridge' then 'Western Indian-Antarctic Ridge'\
           when geometry = 'M 4.4 - Central East Pacific Rise' then 'Central East Pacific Rise'\
           when geometry = 'M 4.4 - North of Svalbard' then 'North of Svalbard'\
           when geometry = 'M 4.4 - Off the coast of Central America' then 'Off the coast of Central America'\
           when geometry = 'M 4.4 - Reykjanes Ridge' then 'Reykjanes Ridge'\
           when geometry = 'M 4.5 - Mid-Indian Ridge' then 'Mid-Indian Ridge'\
           when geometry = 'M 4.5 - Southern East Pacific Rise' then 'Southern East Pacific Rise'\
           when geometry = 'M 4.6 - Greenland Sea' then 'Greenland Sea'\
           when geometry = 'M 4.6 - North of Ascension Island' then 'North of Ascension Island'\
           when geometry = 'M 4.6 - Northern East Pacific Rise' then 'Northern East Pacific Rise'\
           when geometry = 'M 4.7 - South Shetland Islands' then 'South Shetland Islands'\
           when geometry = 'M 4.7 - Southeast of Easter Island' then 'Southeast of Easter Island'\
           when geometry = 'M 4.9 - Bouvet Island region' then 'Bouvet Island region'\
           when geometry = 'M 5.0 - Prince Edward Islands region' then 'Prince Edward Islands region'\
           when geometry = 'M 5.0 - Southeast Indian Ridge' then 'Southeast Indian Ridge'\
           when geometry = 'M 5.0 - Vanuatu region' then 'Vanuatu region'\
           when geometry = 'M 5.1 - South of the Kermadec Islands' then 'South of the Kermadec Islands'\
           when geometry = 'M 5.2 - Pacific-Antarctic Ridge' then 'Pacific-Antarctic Ridge'\
    else trim(substring_index(geometry, ',', -1))\
    end")  

    ## to make final output we have to run the 'commit()' method of the database object
    db.commit()
    print(cursor.rowcount, "records inserted")

    #################################################
    # LOAD SIGNIFICANT EARTHQUAKE TABLE
    #################################################
    #-----------------------------------------------
    # earthquakes_ngdc table
    #-----------------------------------------------
    # read CSV file
    eq_ngdc_column_names = \
    [  'earthquake_id'
    ,'tsunami_fl'
    ,'year_nr'
    ,'month_nr'
    ,'day_nr'
    ,'hour_nr'
    ,'minute_nr'
    ,'second_nr'
    ,'focal_depth_nr'
    ,'mag_nr'
    ,'mag_mw_nr'
    ,'mag_ms_nr'
    ,'mag_mb_nr'
    ,'mag_ml_nr'
    ,'mag_mfa_nr'
    ,'mag_unk_nr'
    ,'mmi_int_nr'
    ,'country_de'
    ,'state_de'
    ,'location_de'
    ,'lat'
    ,'lng'
    ,'region_cd'
    ,'deaths_nr'
    ,'deaths_de'
    ,'missing_nr'
    ,'missing_de'
    ,'injuries_nr'
    ,'injuries_de'
    ,'dollar_damage_millions_nr'
    ,'dollar_damage_millions_de'
    ,'houses_destroyed_nr'
    ,'houses_destroyed_de'
    ,'houses_damaged_nr'
    ,'houses_damaged_de'
    ,'total_deaths_nr'
    ,'total_deaths_de'
    ,'total_missing_nr'
    ,'total_missing_de'
    ,'total_injuries_nr'
    ,'total_injuries_de'
    ,'total_damage_millions_dollars_nr'
    ,'total_damage_de'
    ,'total_houses_destroyed_nr'
    ,'total_houses_destroyed_de'
    ,'total_houses_damaged_nr'
    ,'total_houses_damaged_de'
    ]

    eq_ngdc_df = pd.read_csv('resources/earthquakes_ngdc.csv', header = 0, names = eq_ngdc_column_names)
    #print(eq_ngdc_df)

    #create_engine moved to config.py to allow different configurations
    engine.execute(f"drop table if exists earthquakes_ngdc")


    with engine.connect() as conn, conn.begin():
        eq_ngdc_df.to_sql('earthquakes_ngdc', conn, index=True)

    print('Table EARTHQUAKES_NGDC loaded.')
    print('==============================================')
    print('*** PYTHON LOOKUP TABLE SCRIPT COMPLETED ***')

    # LOAD DATA INTO PANDAS FROM CSV FILES
    df_tornadoes = pd.read_csv('resources/1950-2017_torn.csv')
    df_hail = pd.read_csv('resources/1955-2017_hail.csv')
    df_wind = pd.read_csv('resources/wind.csv')
    df_tsunami = pd.read_csv('resources/tsunami.csv')
    df_volcanoes = pd.read_csv('resources/volcano.csv')

    # LOADING TORNADOES DATA INTO TABLE
    df_tornadoes.to_sql('tornadoes', con=engine, if_exists='append', index = False, index_label = "id")
    # LOADING HAIL DATA INTO TABLE
    df_hail.to_sql('hail', con=engine, if_exists='append', index = False, index_label = "id")
    # LOADING WIND DATA INTO TABLE
    df_wind.to_sql('wind', con=engine, if_exists='append', index = False, index_label = "id")
    # LOADING TSUNAMI DATA INTO TABLE
    df_tsunami.to_sql('tsunamis', con=engine, if_exists='append', index = False, index_label = "tb_id")
    # LOADING VOLCANO DATA INTO TABLE
    df_volcanoes.to_sql('volcanoes', con=engine, if_exists='append', index = False, index_label = "tb_id")


extract_transform_load()