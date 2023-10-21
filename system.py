import psycopg2

class System:
    # connect to local db 
    conn = psycopg2.connect(database = "TheHiddenLeaf", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "postgres",
                            port = 5432)

    # Open a cursor to perform database operations
    cur = conn.cursor()
    
    # create plants table and commit to db
    plants = """CREATE TABLE plants(
        plantID CHAR(3) PRIMARY KEY,
        name VARCHAR(25),
        price NUMERIC(2, 2),
        discount NUMERIC(3, 2) DEFAULT NULL,
        qty INTEGER,
        type VARCHAR(25),
        species VARCHAR(50),
        duration VARCHAR(15),
        description TEXT); """

    cur.execute(plants)

    # create plantcare table and commit to db
    plantCare = """CREATE TABLE plantCare(
        careID CHAR(3) PRIMARY KEY,
        plantID CHAR(3) REFERENCES Plants ON DELETE CASCADE,
        maintenance VARCHAR(10),
        sunlight VARCHAR(20),
        water INTEGER);"""
    
    cur.execute(plantCare)

    # create customers table and commit to db
    customers = """CREATE TABLE customers(
        username VARCHAR(50) PRIMARY KEY,
        password VARCHAR(8),
        fname VARCHAR(50),
        lname VARCHAR(50),
        email VARCHAR(100),
        phone CHAR(10) DEFAULT NULL);"""

    cur.execute(customers)  

    # create orders table and commit to db
    orders = """CREATE TABLE orders(
        orderID CHAR(4) PRIMARY KEY,
        plantID CHAR(3) REFERENCES plants,
        username VARCHAR(50) REFERENCES customers,
        qty INTEGER,
        date TIMESTAMP(0));"""

    cur.execute(orders)

    # close connection with db
    conn.commit()
    cur.close()
    conn.close()