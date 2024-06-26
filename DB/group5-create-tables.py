import mysql.connector
import csv

#### create and connect DB ####
def createDB(db_use):
    mydb = mysql.connector.connect(
            host="localhost",
            user = "root",
            passwd = "" # insert user password
            )
    mycursor = mydb.cursor()
    mycursor.execute(f"DROP DATABASE IF EXISTS {db_use}")
    mycursor.execute(f"CREATE DATABASE {db_use}") # create database
    mydb.database = db_use # use database
    return mydb, mycursor

# create and conndect "project" DB
mydb, mycursor = createDB("project")

#### creating table ####

# customer
input_filename = 'customer.csv' # change path

mycursor.execute("DROP TABLE IF EXISTS customer")

mycursor.execute('''CREATE TABLE customer (customer_id VARCHAR(255),
                 location_number INT,
                 location_type CHAR(10),
                 latitude DECIMAL(10, 6),
                 longitude DECIMAL(10, 6),
                 PRIMARY KEY(customer_id, location_number))''')

f = open(input_filename, 'r')
rd = csv.reader(f)
next(rd,None)
for row in rd:
    latitude = 'NULL' if row[3] == '' else round(float(row[3]), 6)
    longitude = 'NULL' if row[4] == '' else round(float(row[4]), 6)
    mycursor.execute(f'''
    INSERT INTO customer (customer_id, location_number, location_type, latitude, longitude)
    VALUES ("{row[0]}", "{row[1]}", "{row[2]}", {latitude if latitude != 'NULL' else 'NULL'}, {longitude if longitude != 'NULL' else 'NULL'})
    ''')

mydb.commit()
f.close()


# category
input_filename = 'vendor_category.csv' # change path

mycursor.execute("DROP TABLE IF EXISTS category")

mycursor.execute('''CREATE TABLE category (vendor_tag_num INT PRIMARY KEY,
                 Major_category CHAR(25),
                 Sub_category CHAR(15))''')

f = open(input_filename, 'r')
rd = csv.reader(f)
next(rd,None)
for row in rd:
    mycursor.execute(f'INSERT INTO category (vendor_tag_num, Major_category, Sub_category) values ("{row[0]}","{row[1]}", "{row[2]}")')

mydb.commit()
f.close()

# vendors
input_filename = "vendors.csv" # change path

mycursor.execute("DROP TABLE IF EXISTS vendors")

mycursor.execute("DROP TABLE IF EXISTS vendors")

mycursor.execute('''
    CREATE TABLE vendors (
        vendor_id INT,
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        delivery_charge float(5),
        serving_distance INT,
        open_time TIME,
        end_time TIME,
        is_open BOOLEAN,
        preparation_time INT,
        discount_percentage DECIMAL(4, 2),
        vendor_rating float(5),
        PRIMARY KEY (vendor_id)
    )
''')

with open(input_filename, 'r') as f:
    rd = csv.reader(f)
    next(rd, None)
    for row in rd:
        mycursor.execute('''
            INSERT INTO vendors (vendor_id, latitude, longitude, delivery_charge, serving_distance, open_time, end_time, is_open, preparation_time, discount_percentage, vendor_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', row)

    mydb.commit()

# likes
input_filename = "likes.csv" # change path

mycursor.execute("DROP TABLE IF EXISTS likes")

mycursor.execute("CREATE TABLE likes (customer_id VARCHAR(10), vendor_id INT, `like` INT, PRIMARY KEY (customer_id, vendor_id))")

f = open(input_filename, 'r') # open likes.csv
rd = csv.reader(f)
next(rd,None) # skip columns' information
for row in rd: # insert each rows of csv
    mycursor.execute(f'INSERT INTO likes (customer_id,vendor_id,`like`) values ("{row[0]}","{int(row[1])}","1")')

mydb.commit() # close likes.csv
f.close()

# vendor_tag
input_filename = "vendor_tag.csv" # change path

mycursor.execute("DROP TABLE IF EXISTS vendor_tag")

mycursor.execute('''CREATE TABLE vendor_tag (id INT,
                 vendor_tag INT,
                 PRIMARY KEY (id, vendor_tag))''')

f = open(input_filename, 'r')
rd = csv.reader(f)
next(rd,None)

for row in rd:
    mycursor.execute(f'INSERT INTO vendor_tag (id, vendor_tag) values ("{row[0]}","{row[1]}")')

mydb.commit()
f.close()

mydb.close()