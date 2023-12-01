# The Hidden Leaf
 A command-line interface program in Python that simulates a plant shop. 

 # Required Dependencies
 ### PostgreSQL
 
 PostgreSQL is utilized as the DBMS and requires that the psycopg2 package is installed in the same directory as the files. 

 Install psycopg2 by running the following: 

    pip install psycopg2

 In the system.py file, the variables to connect to the database (line 31) must be changed to connect to your postgres database. 

 ### Argon2-cffi

 Passwords are hashed before being stored in the database and requires that argon2-cffi is installed in the same directory as the files. 

 Run the following command to install argon2:

    pip install argon2-cffi

 # Run Program 
 Make sure all files are in the same directory before running.
 
 Run the following command in the terminal to start the program: 
 
    python main.py

## Authors
 Kiara Vasquez 
 
 Anushka Chinoy
