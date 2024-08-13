import oracledb
import os

user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
dsn = os.getenv("DB_DSN")

print("Oracledb version:", oracledb.__version__)

connection=oracledb.connect(
     user=user,
     password=password,
     dsn=dsn)

print("Connection successful")

from dotenv import load_dotenv
load_dotenv()
import os
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
dsn = os.getenv("DB_DSN")
COMPARTMENT_OCID = os.getenv("COMPARTMENT_OCID")

print("The database user name is:", username)

try: 
    conn23c = oracledb.connect(user=username, password=password, dsn=dsn)
    print("Connection successful!")
except Exception as e:
    print("Connection failed!")
