import requests
import psycopg2
from psycopg2.extras import execute_batch
from functools import reduce


DB_USER = "postgres"
DB_PASSWORD = "oJ71Srz6Yc0E"
DB_DATABASE = "cowin_map"
RESOURCE_TABLE_NAME = "resources"
API_KEY = 'AIzaSyClGVndCtMIDvZ7GdE1fO5OPQL5XdtMvVM'
SHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/%s/values/Sheet1!A2:Q?key=%s'
PG_CONNECTION = None


def init():
    get_connection()


def get_connection():
    global PG_CONNECTION
    if PG_CONNECTION is not None and PG_CONNECTION.closed == 0:
        return PG_CONNECTION
    else:
        PG_CONNECTION = psycopg2.connect(
            user=DB_USER,
            dbname=DB_DATABASE,
            password=DB_PASSWORD,
        )
    return PG_CONNECTION


def close_connection():
    if PG_CONNECTION is not None and PG_CONNECTION.closed == 0:
        PG_CONNECTION.close()


def get(city=None, resource_name=None, bounding_points=[]):

    try:
        cursor = get_connection().cursor() 
        select_query = f"SELECT raw_obj FROM {RESOURCE_TABLE_NAME}"
        conditions = []
        query_params = ()

        if isinstance(city, str) and city.strip():
            city = city.strip().lower()
            conditions.append("city = %s")
            query_params += (city,)

        if isinstance(resource_name, str) and resource_name.strip():
            resource_name = resource_name.strip().lower()
            conditions.append("resource = %s")
            query_params += (resource_name,)

        if isinstance(bounding_points, list) and bounding_points:

            conditions.append(
                f"ST_CONTAINS(ST_ENVELOPE('LINESTRING({', '.join('%s %s' for _ in range(len(bounding_points)))})'), location)"
            )
            # conditions : [ ..., "ST_CONTAINS(ST_ENVELOPE('LINESTRING(%s %s, %s %s, ...)'))" ]
            
            query_params += reduce(lambda x, y: x+y, bounding_points)

        if conditions:
            select_query += " WHERE " + " AND ".join(conditions)

        cursor.execute(select_query, query_params)
        resources_info = cursor.fetchall()

        return resources_info

    finally:
        cursor.close() 


def upsert(city, resource_name, resources_info, google_sheet_id):

    try:

        city = city.strip().lower()
        resource_name = resource_name.strip().lower()

        connection = get_connection() 
        cursor = connection.cursor() 

        delete(city, resource_name=resource_name, cursor=cursor)
        
        database_values = []
        insert_query = f"INSERT INTO {RESOURCE_TABLE_NAME} (city, resource, google_sheet_id, location, raw_obj) VALUES (%s, %s, %s, ST_MakePoint(%s, %s), %s)"
        for resource_info in resources_info:

            latitude, longitude = get_lat_long(resource_info)

            database_values.append((
                city,
                resource_name,
                google_sheet_id,
                longitude,
                latitude,
                resource_info
            ))

        execute_batch(cursor, insert_query, database_values)

        connection.commit()

    finally:

        if cursor is not None:
            cursor.close()


def delete(city, resource_name=None, cursor=None):

    try:

        city = city.strip().lower()

        local_cursor = cursor
        if local_cursor is None:
            local_connection = get_connection()
            local_cursor = local_connection.cursor() 
        
        delete_query = f"DELETE FROM {RESOURCE_TABLE_NAME} WHERE city = %s"
        query_params = (city,)

        if resource_name is not None:
            resource_name = resource_name.strip().lower()
            delete_query += " AND resource = %s"
            query_params += (resource_name,)

        local_cursor.execute(delete_query, query_params)

        if cursor is None:
            local_connection.commit()

    finally:

        if cursor is None and local_cursor is not None:
            local_cursor.close()


def get_lat_long(resource_info):
    
    try:
        latitude = float(resource_info[2])
        longitude = float(resource_info[3])
        return latitude, longitude
    except:
        pass

    try:
        # example url: https://www.google.com/maps/place/Dr+V+Balaji+Dr+V+Seshiah+Diabetes+Care+and+Research+Institute/@13.0748233,80.2277722,17z/data=!3m1!4b1!4m5!3m4!1s0x3a5266872dc69d8b:0xca2c2747bed28ec9!8m2!3d13.0747514!4d80.2299576 
        url_location = resource_info[4].split('@')[1].split('z')[0].split(',')
        latitude = float(url_location[0])
        longitude = float(url_location[1])
        return latitude, longitude
    except:
        pass
    
    return None, None


def get_sheet_data(sheet_id, api_key):
    url = SHEET_URL % (sheet_id, api_key)
    resp = requests.get(url)

    if resp.status_code == 200:
        values = resp.json()['values']

        return values

    raise Exception(f"invalid link: {sheet_id}")
