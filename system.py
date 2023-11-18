import psycopg2
import os, sys, re
import getpass as gp
from user import User


class System:
    def __init__(self):
        self.pages = {"Start":self.start,
                    "Login":self.login,
                    "Sign Up":self.signUp,
                    "Browse For Plants":self.browse,
                    "Continue Browsing":self.browse,
                    "User Settings":self.settings,
                    "Email":self.email,
                    "Change Email":self.changeEmail,
                    "Phone":self.phone,
                    "Change Phone":self.changePhone,
                    "Return to Main Menu":self.start,
                    "Return to Settings":self.settings,
                    "Exit":self.leaf
        }

        # connect to local db 
        self.conn = psycopg2.connect(database = "TheHiddenLeaf", 
                                user = "postgres", 
                                host = 'localhost',
                                password = "postgres",
                                port = 5432)

        # Open a cursor to perform database operations
        self.cur = self.conn.cursor()

        
        # create plants table and commit to db
        plants = """CREATE TABLE IF NOT EXISTS plants(
            plantID CHAR(3) PRIMARY KEY,
            name VARCHAR(25),
            price NUMERIC(4, 2),
            discount NUMERIC(3, 2) DEFAULT NULL,
            qty INTEGER,
            type VARCHAR(25),
            species VARCHAR(50),
            duration VARCHAR(15),
            description TEXT,
            CHECK (discount < 1.00)); """

        self.cur.execute(plants)

        # create plantcare table and commit to db
        plantCare = """CREATE TABLE IF NOT EXISTS plantCare(
            careID CHAR(3) PRIMARY KEY,
            plantID CHAR(3) REFERENCES Plants ON DELETE CASCADE,
            maintenance VARCHAR(10),
            sunlight VARCHAR(20),
            water INTEGER);"""
        
        self.cur.execute(plantCare)

        # create customers table and commit to db
        customers = """CREATE TABLE IF NOT EXISTS customers(
            username VARCHAR(15) PRIMARY KEY,
            password VARCHAR(12),
            fname VARCHAR(50),
            lname VARCHAR(50),
            email VARCHAR(100),
            phone CHAR(10) DEFAULT NULL);"""

        self.cur.execute(customers)  

        # create orders table and commit to db
        orders = """CREATE TABLE IF NOT EXISTS orders(
            orderID CHAR(4) PRIMARY KEY,
            plantID CHAR(3) REFERENCES plants,
            username VARCHAR(50) REFERENCES customers,
            qty INTEGER,
            date TIMESTAMP(0));"""

        self.cur.execute(orders)

        # close connection with db -- needs to close when user logs off
        self.conn.commit()
    
        # create an instance of a user object
        self.user = User("guest", "", "", "", False)

   
    # deconstructor for closing the db connection
    def __del__(self):
        self.conn.close()


    # function to clear the console
    def clearConsole(self):
        if os.name == 'nt':
            os.system('cls')
        else: 
            os.system('clear')

    
    # function to exit the app
    def leaf(self):
        self.printTitle("The Hidden Leaf")
        sys.exit("Thank You For Shopping at The Hidden Leaf! Have a Nice Day!\n")


    # function to print the title of a page
    def printTitle(self, title):
        even = False
        if len(title) % 2 == 0:
            even = True
        if even:
            dashes = 28
        else: 
            dashes = 27
        numDashes = dashes - len(title)
        oneSideDashes = (numDashes // 2) - 1
        print("="*dashes)
        print('='*oneSideDashes + ' ' + title + ' ' + '='*oneSideDashes)
        print("="*dashes + "\n")


    # function to go back to the page passed to the function
    def goBack(self, back):
        self.printOptions(["Back"])
        selection = input("\nEnter your selection: ")
        validSelection = self.selectionValidation(selection, 1)
        if  not validSelection:
            self.clearConsole()
            print("\nPlease Enter a Valid Selection: \n")
            self.goBack(back)

        items = self.pages.items()
        
        for pair in items:
            if pair[1] == back: 
                option = pair[0]
                break

        self.clearConsole()
        return self.pages[option]()


    # function for incomplete pages
    def comingSoon(self, back):
        print("Coming Soon!\n")
        self.goBack(back)
            

    # function to print options
    def printOptions(self, options):
        for i in range(len(options)):
            print(f'[{i}] {options[i]}')        


    # function to perform validation for a selection
    def selectionValidation(self, selection, numOptions):
        isValid = False
        if selection.isnumeric():
            selection = int(selection)
            if selection <= numOptions and selection >= 0:
                isValid = True
        return isValid
            

    # function to perform selection for an option
    def optionSelection(self, options):
        numOptions = len(options)
        # print the options
        self.printOptions(options)

        # get input from user & validate it
        selection = input("\nEnter Your Selection: ")
        validSelection = self.selectionValidation(selection, numOptions)
        if validSelection:
            selection = int(selection)
        else:
            self.clearConsole()
            print("\nPlease Enter a Valid Selection: \n")
            self.optionSelection(options)

        # get the option the user selected
        option = options[selection]
        # clear the console
        self.clearConsole()
        # call the function matching the selected option
        return self.pages[option]()


    # function for the Login page
    def login(self):
        self.printTitle("Login")
        username = input("Enter Username: ")
        password = gp.getpass(prompt="Enter Password: ")
        validLogin, customer = self.authentication(username, password)
        # if the login is valid, set user object attributes to what's stored in the db
        if validLogin:
            self.user.login(username=customer[0],
                            fname=customer[2],
                            lname=customer[3],
                            email=customer[4],
                            phone=customer[5])
            # bring user to start page
            return self.start()
        else:
            # prompt user to try again
            self.clearConsole()
            print("\nPlease Enter a Valid Username and Password: \n")
            self.login()
    

    # function to authenticate user credentials
    def authentication(self, username, password):
        isValid = False
        # Insert authentication steps here
        self.cur.execute('SELECT username, password, fname, lname, email, phone FROM customers WHERE username = %s AND password = %s', (username, password))
        customer = self.cur.fetchone()
        if customer:
            isValid = True
        return isValid, customer


    # function to validate username
    def validateUsername(self, username):
        # check length of username
        if len(username) < 1 or len(username) > 15:
            print("\nUsername must be 1-15 Characters Long\n")
            return False 
        # check if username exists in the db
        self.cur.execute('SELECT * FROM Customers WHERE username = %s;', (username,))
        userExists = self.cur.fetchone()
        if userExists:
            print("\nUsername Already Exists\n")
            return False
        return True


    # function that checks the password is valid
    def validatePassword(self, password, confirmPass):
        # check if the passwords are the same
        if password != confirmPass:
            print("\nPlease Ensure the Passwords Match\n")
            return False
        # check length of password
        if len(password) < 8 or len(password) > 12:
            print("\nPassword Must Be 8-12 Characters Long\n")
            return False
        # check if it has a digit
        if not any(char.isdigit() for char in password):
            print("\nPassword Must Contain At Least One Digit\n")
            return False 
        if not any(char.isupper() for char in password):
            print("\nPassword Must Contain At Least One Capital Letter\n")
            return False
        if not re.search('[@_!#$%^&*()<>?|}{~:]', password):
            print("\nPassword Must Contain At Least One Special Character\n")
            return False
        return True

    
    # function to validate first and last name
    def validateName(self, fname, lname):
        if len(fname) < 1 or len(fname) > 50:
            print("\nFirst Name Must be 1-50 Characters Long\n")
            return False
        if len(lname) < 1 or len(lname) > 50:
            print("\nLast Name Must be 1-50 Characters Long\n")
            return False
        return True


    # function to validate email
    def validateEmail(self, email):
        regex = r'\b[a-zA-Z0-9._]+@[a-zA-Z0-9-.]+.[A-Za-z]\b'
        if not re.match(regex, email):
            print("\nPlease Enter A Valid Email Address\n")
            return False
        return True


    # function to valoidate phone number
    def validatePhone(self, phone):
        if phone == "":
            return True
        if not phone.isdigit():
            print("\nPhone Number Must Contain 10 Digits\n")
            return False
        if len(phone) < 10 or len(phone) > 10:
            print("Phone Number Must Contain 10 Digits\n")
            return False
        return True


    # function for the Sign Up page
    def signUp(self):
        self.printTitle("Sign Up")
        # prompt user to enter necessary info
        username = input("\nEnter Username: ")
        password = gp.getpass(prompt="Enter Password: ")
        confirmPass = gp.getpass(prompt="Confirm Password: ")
        fname = input("\nEnter First Name: ")
        lname = input("Enter Last Name: ")
        email = input("Enter Email Address: ")
        phone = input("Enter Phone Number (optional): ")
        
        # validate user input
        validUsername = self.validateUsername(username)
        validPass = self.validatePassword(password, confirmPass)
        validName = self.validateName(fname, lname)
        validEmail = self.validateEmail(email)
        validPhone = self.validatePhone(phone)
        
        # save the account to the db
        if validUsername and validPass and validEmail and validPhone and validName:
            self.cur.execute("INSERT INTO Customers (username, password, fname, lname, email, phone) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, fname, lname, email, phone))
            self.conn.commit()
            # bring user to login screen
            print("\nAccount Successfully Created\n")
            self.goBack(self.start)
        else: 
            print("\nAccount Creation Failed\n")
            return self.signUp()


    # function for browsing the plants
    def browse(self):
        # display in alphabetical order: Name and price 
        # Options: Sort by price, filter by type or duration
        self.printTitle("Browse For Plants")
        # query for name of each plant in the table
        self.cur.execute("SELECT name, plantid FROM Plants ORDER BY name")
        result = self.cur.fetchall()
        options = []
        # add each plant as an option
        for plant in result: 
            options.append(f"{plant[0]}")
            # dynamically update the pages table with plant menus
            if plant not in self.pages:
                # deleay execution of plantInfo until the user selects the plant
                self.pages[f"{plant[0]}"] = lambda plant=plant[0]: self.plantInfo(plant)
                self.pages[f"{plant[0]} Care"] = lambda plant=plant[1]: self.plantCare(plant)
        options.append("Return to Main Menu")
        self.optionSelection(options)


    # function to print plant info
    def plantInfo(self, plant):
        self.printTitle(f"{plant}")
        # query table for necessary info
        self.cur.execute("SELECT price, type, species, duration, description, discount FROM plants WHERE name = %s", (plant,))
        result = self.cur.fetchone()
        price = result[0]
        discount = result[5]
        if discount: 
            discountedPrice = round(price - (price * discount), 2)
            print(f"Discounted Price: ${discountedPrice}")
            info = ["Original Price: $", "Type: ", "Species: ", "Duration: ", "Description: "]
        else:
            info = ["Price: $", "Type: ", "Species: ", "Duration: ", "Description: "]
        # print info
        for i in range(5):
            print(f"{info[i]}{result[i]}")
        print("\n")
        options = [f"{plant} Care", "Add To Cart", "Continue Browsing"]
        self.optionSelection(options)


    # function to display plant care info
    def plantCare(self, plant):
        self.cur.execute("SELECT name FROM plants WHERE plantID = %s", (plant,))
        plantName = self.cur.fetchone()[0]
        self.printTitle(f"{plantName} Care")
        # query table for necessary info
        self.cur.execute("SELECT maintenance, sunlight, water FROM plantCare WHERE plantID = %s", (plant,))
        result = self.cur.fetchone()
        info = ["Maintenance: ", "Sunlight: ", "Water: "]
        # print info
        for i in range(3):
            print(f"{info[i]}{result[i]}")
        print("\n")
        self.pages["Return to Plant Info"] = lambda plant=plantName: self.plantInfo(plant)
        options = ["Return to Plant Info"]
        self.optionSelection(options)


    # function for user settings
    def settings(self):
        self.printTitle("User Settings")
        options = ["Email", "Phone", "Return to Main Menu"]
        self.optionSelection(options)


    # function that allows user to view email
    def email(self):
        self.printTitle("Email")
        # obtain email info from customers table
        self.cur.execute('SELECT email FROM customers WHERE username = %s', (self.user.username,))
        result = self.cur.fetchone()[0]

        # display current phone to user 
        print(f"Current Email: {result}\n")
        options = ["Change Email", "Return to Settings"]
        self.optionSelection(options)


    # function to change email
    def changeEmail(self):
        self.printTitle("Editing Email")
        email = input("Enter An Email: ")
        validEmail = self.validateEmail(email)
        if validEmail:
            self.cur.execute('UPDATE customers SET email = %s WHERE username = %s', (email, self.user.username))
            self.conn.commit()
            self.user.email = email
            print("\nEmail Has Been Successfully Updated\n")
        options = ["Return to Settings"]
        self.optionSelection(options)


    # function to view phone number 
    def phone(self):
        self.printTitle("Phone")

        # obtain phone info from customers table
        self.cur.execute('SELECT phone FROM customers WHERE username = %s', (self.user.username,))
        result = self.cur.fetchone()[0]

        # display current phone to user 
        print(f"Current Phone Number: {result if result.isdigit() else 'N/A'}\n")

        options = ["Change Phone", "Return to Settings"]
        self.optionSelection(options)


    # function to change phone number
    def changePhone(self):
        self.printTitle("Editing Phone")
        phone = input("Enter A Phone Number: ")
        validPhone = self.validatePhone(phone)
        if validPhone:
            self.cur.execute('UPDATE customers SET phone = %s WHERE username = %s', (phone, self.user.username))
            self.conn.commit()
            self.user.phone = phone
            print("\nPhone Number Has Been Successfully Updated\n")
        options = ["Return to Settings"]
        self.optionSelection(options)


    # function for welcome page
    def start(self):
        self.clearConsole()
        self.printTitle("The Hidden Leaf")
        if self.user.loggedIn:
            print(f"Welcome {self.user.fname}!\n")
            options = ["Browse For Plants", "User Settings", "Exit"]
            self.optionSelection(options)
        else:
            options = ["Login", "Sign Up", "Browse For Plants", "Exit"]
            self.optionSelection(options)