import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')

def get_pg_connection(): 
    return psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="ecommerce_db",
    user="postgres",      # or admin
    password=POSTGRES_PASSWORD
)

