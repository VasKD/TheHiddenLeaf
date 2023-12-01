import psycopg2
import os, sys, re
import getpass as gp
from user import User


class System:
    def __init__(self):
        self.pages = {"Start":self.start,
                    "Login":self.login,
                    "Sign Up":self.signUp,
                    "Order History":self.orderHistory,
                    "Browse For Plants":self.browse,
                    "Remove Item":self.removeFromCart,
                    "Update Item": self.editCart,
                    "Continue Browsing":self.browse,
                    "View Cart":self.viewCart,
                    "Checkout": self.checkout,
                    "Place Order": self.placeOrder,
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
            orderID CHAR(4),
            plantID CHAR(3) REFERENCES plants,
            username VARCHAR(50) REFERENCES customers,
            qty INTEGER,
            date TIMESTAMP(0),
            CONSTRAINT orders_pk PRIMARY KEY(orderID, plantID));"""

        self.cur.execute(orders)


        # self.cur.execute("DROP FUNCTION get_orders(character varying);")
        # function that returns a table of orders for a specific user
        getOrders = """CREATE OR REPLACE FUNCTION get_orders(user_name VARCHAR)
            RETURNS TABLE(orderID CHAR(4), name VARCHAR(25), price NUMERIC(4,2), qty INTEGER, date TIMESTAMP(0)) AS $$
            BEGIN
                RETURN QUERY 
                SELECT orders.orderID, plants.name, plants.price, orders.qty, orders.date
                FROM orders JOIN plants ON orders.plantID = plants.plantID
                WHERE orders.username = user_name
                GROUP BY orders.orderID, plants.price, plants.name, orders.qty, orders.date
                ORDER BY orders.orderID;
            END; $$
            LANGUAGE plpgsql;"""

        self.cur.execute(getOrders)

        # check to see if trigger already exists
        self.cur.execute("SELECT 1 FROM pg_trigger WHERE tgname = 'update_inventory';")
        trigger = self.cur.fetchone()

        # trigger to update inventory whenever an order is placed
        if not trigger:
            updateInventory = """CREATE OR REPLACE FUNCTION update_inventory() RETURNS TRIGGER AS $$
                                BEGIN
                                    UPDATE plants SET qty = qty - NEW.qty WHERE plantID = NEW.plantID;
                                    RETURN NEW;
                                END; $$ LANGUAGE plpgsql;
            
                                CREATE TRIGGER update_inventory AFTER INSERT ON orders 
                                FOR EACH ROW EXECUTE PROCEDURE update_inventory();"""

            self.cur.execute(updateInventory)

        # close connection with db -- needs to close when user logs off
        self.conn.commit()
    
        # create an instance of a user object
        self.user = User("guest", "", "", "", False)

   
    # deconstructor for closing the db connection
    def __del__(self):
        self.conn.close()


# *********************************
# ******** CLASS FUNCTIONS ********
# *********************************


# *****************
# UTILITY FUNCTIONS
# *****************

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


    # function to validate numeric input
    def numericValidation(self, value):
        if value.isnumeric():
            return int(value)
        else:
            return "Invalid"


# **********************
# LOGIN/SIGNUP FUNCTIONS
# **********************


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
            self.clearConsole()
            return False 
        # check if username exists in the db
        self.cur.execute('SELECT * FROM Customers WHERE username = %s;', (username,))
        userExists = self.cur.fetchone()
        if userExists:
            self.clearConsole()
            print("\nUsername Already Exists\n")
            return False
        return True


    # function that checks the password is valid
    def validatePassword(self, password):  
        good = True  
        # check length of password
        if len(password) < 8 or len(password) > 12:
            print("\nPassword Must Be 8-12 Characters Long!")
            good = False
        # check if it has a digit
        if not any(char.isdigit() for char in password):
            if good:
                print("\n")
            print("Password Must Contain At Least One Digit!")
            good = False
        if not any(char.isupper() for char in password):
            if good:
                print("\n")
            print("Password Must Contain At Least One Capital Letter!")
            good = False
        if not re.search('[@_!#$%^&*()<>?|}{~:]', password):
            if good:
                print("\n")
            print("Password Must Contain At Least One Special Character!")
            good = False
        return good


    # function that checks the password initially provided matches the one confirmed
    def confirmPassword(self, password, confirmPass):
        if password != confirmPass:
            print("\nPlease Ensure the Passwords Match\n")
            return False
        else:
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
        regex = r'\b[a-zA-Z0-9_]+@[a-zA-Z0-9_-]+\.[a-z]{3}\b'
        if not re.match(regex, email):
            print("\nPlease Enter A Valid Email Address\n")
            return False
        return True


    # function to valoidate phone number
    def validatePhone(self, phone):
        good = True
        if phone == "":
            return good
        if not phone.isdigit():
            if good:
                print("\n")
            print("Phone Number Must Contain Digits Only!")
            good = False
        if len(phone) < 10 or len(phone) > 10:
            if good:
                print("\n")
            print("Phone Number Must Contain 10 Digits!")
            good = False
        return good


    # function for the Sign Up page
    def signUp(self):
        self.printTitle("Sign Up")
        # prompt user to enter necessary info
        print("Username must be 1-15 characters long")
        username = input("\nEnter Username: ")
        validUsername = self.validateUsername(username)
        # validate username
        if not validUsername:
            return self.signUp()

        # prompt user to enter password and confirm password
        print("\nPassword must have the following:\n ~ 8-12 characters\n ~ At least one digit\n ~ At least one capital letter\n ~ At least one special character\n")
        password = gp.getpass(prompt="Enter Password: ")
        validPass = self.validatePassword(password)
        while not validPass: 
            print("\n")
            password = gp.getpass(prompt="Enter Password: ")
            validPass = self.validatePassword(password)
        confirmPass = gp.getpass(prompt="Confirm Password: ")
        validConfirm = self.confirmPassword(password, confirmPass)
        while not validConfirm:
            confirmPass = gp.getpass(prompt="Confirm Password: ")
            validConfirm = self.confirmPassword(password, confirmPass)

        # validate name
        fname = input("\nEnter First Name: ")
        lname = input("Enter Last Name: ")
        validName = self.validateName(fname, lname)
        while not validName:
            fname = input("\nEnter First Name: ")
            lname = input("Enter Last Name: ")
            validName = self.validateName(fname, lname)

        # validate email
        email = input("Enter Email Address: ")
        validEmail = self.validateEmail(email)
        while not validEmail:
            email = input("Enter Email Address: ")
            validEmail = self.validateEmail(email)

        # validate phone number
        print("\nPhone Number should be entered as ten consecutive digits\n")
        phone = input("Enter Phone Number (optional): ")
        validPhone = self.validatePhone(phone)
        while not validPhone:
            print("\n")
            phone = input("Enter Phone Number (optional): ")
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


# *********************
# BROWSE/CART FUNCTIONS
# *********************


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
        options.append("View Cart")
        options.append("Return to Main Menu")
        self.optionSelection(options)


    # function to print plant info
    def plantInfo(self, plant):
        self.printTitle(f"{plant}")
        # query table for necessary info
        self.cur.execute("SELECT price, type, species, duration, description, discount, qty FROM plants WHERE name = %s", (plant,))
        result = self.cur.fetchone()
        qty = result[6]
        # check if plant is out of stock
        if qty == 0:
            print("Out of Stock\n")
            options = [f"{plant} Care", "Continue Browsing"]
        else: 
            self.pages["Add To Cart"] = lambda plant=plant: self.addToCart(plant)
            options = [f"{plant} Care", "Add To Cart", "Continue Browsing"]
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
        self.optionSelection(options)


    # function to add a plant to the cart
    def addToCart(self, plant):
        self.printTitle("Add To Cart")
        # query table for necessary info
        self.cur.execute("SELECT plantID, price, discount, qty FROM plants WHERE name = %s", (plant,))
        result = self.cur.fetchone()
        plantID = result[0]
        price = result[1]
        discount = result[2]
        print(f"Name: {plant}")
        if discount: 
            discountedPrice = round(price - (price * discount), 2)
            print(f"Discounted Price: ${discountedPrice}")
            print(f"Original Price: ${price}\n")
            price = discountedPrice
        else:
            print(f"Price: ${price}\n")        
        # prompt user to enter quantity
        qty = input("Enter Quantity: ")
        qty = self.numericValidation(qty)
        while qty == 'Invalid':
            print("\nInvalid Input. Please Enter A Numeric Quantity.")
            qty = input("Enter Quantity: ")
            qty = self.numericValidation(qty)
        # validate quantity
        if qty <= 0:
            self.clearConsole()
            print("\nPlease Enter A Value Greater Than 0\n")
            return self.addToCart(plant)
        elif qty > 5:
            self.clearConsole()
            print("\nLimit of 5 Plants\n")
            return self.addToCart(plant)
        elif qty > result[3]:
            self.clearConsole()
            print(f"\nLimited Stock: {result[3]} Available\n")
            return self.addToCart(plant)
        # add item to cart
        self.user.Cart.addItem(plantID, plant, price, qty)
        options = ["View Cart", "Continue Browsing"]
        self.optionSelection(options)


    # function to view cart
    def viewCart(self):
        self.printTitle("View Cart")
        if self.user.Cart.viewCart(): 
            options = ["Remove Item", "Update Item", "Checkout", "Continue Browsing"]
        else: 
            options = ["Continue Browsing"]
        self.optionSelection(options)


    # function to remove item
    def removeFromCart(self):
        self.printTitle("Editing Cart")
        self.user.Cart.viewCart()
        if not self.user.Cart.isEmpty():
            itemName = input("Enter the Name of the Item That You Want to Remove: ")
            if not self.user.Cart.findPlant(itemName):
                self.clearConsole()
                print("\nItem Not Found in Cart. Enter a Valid Name.\n")
                return self.removeFromCart()
            print("\n")
            self.user.Cart.removeItem(itemName)
            print(f"{itemName} Has Been Removed From Your Cart\n")
        options = ["View Cart", "Continue Browsing"]
        self.optionSelection(options)
        

    # function to update an item
    def editCart(self):
        self.printTitle("Editing Cart")
        self.user.Cart.viewCart()
        if not self.user.Cart.isEmpty():
            itemName = input("Enter the Name of the Item That You Want to Update: ")
            if not self.user.Cart.findPlant(itemName):
                self.clearConsole()
                print("\nItem Not Found in Cart. Enter a Valid Name.\n")
                return self.editCart()
            itemQty = input("Enter the New Quantity for This Item: ")
            print("\n")
            if itemQty == '0':
                self.user.Cart.removeItem(itemName)
                print(f"{itemName} Has Been Removed From Your Cart\n")
            else:
                self.user.Cart.updateItem(itemName, int(itemQty))
                print(f"{itemName} Has Been Updated\n")
        options = ["View Cart", "Continue Browsing"]
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


    # function to check out
    def checkout(self):
        self.printTitle("Checkout")
        if not self.user.loggedIn:
            if self.user.Cart.isEmpty():
                print("Cart is Empty\n")
                options = ["Continue Browsing"]
            else: 
                print("Login or Sign Up to Checkout\n")
                options = ["Login", "Sign Up", "Continue Browsing"]
        elif self.user.loggedIn:
            if self.user.Cart.isEmpty():
                print("Cart is Empty\n")
                options = ["Continue Browsing"]
            else:
                print("Please Review Your Cart Before Placing An Order\n")
                self.user.Cart.viewCart()
                options = ["View Cart", "Continue Browsing", "Place Order"]
        self.optionSelection(options)


    # function to place order
    def placeOrder(self):
        self.printTitle("Receipt")
        # check if cart is empty
        if self.user.Cart.isEmpty():
            print("Cart is Empty\n")
            options = ["Continue Browsing"]
            self.optionSelection(options)
        # check if user is logged in and cart is not empty
        elif not self.user.Cart.isEmpty():
            # get the number of entries in the orders table
            self.cur.execute("SELECT MAX(orderID) FROM orders")
            result = self.cur.fetchone()
            # if orderID is None, set orderID to 0001
            if result[0] == None:
                orderID = "0001"
            else:
                # increment orderID by 1
                orderID = str(int(result[0]) + 1).zfill(4)
            # get the date
            self.cur.execute("SELECT CURRENT_TIMESTAMP")
            date = self.cur.fetchone()[0]
            # get the username
            username = self.user.username
            # get the items in the cart
            items = self.user.Cart.items
            # insert each item into the orders table
            for item in items:
                self.cur.execute("INSERT INTO orders (orderID, plantID, username, qty, date) VALUES (%s, %s, %s, %s, %s)", (orderID, item.itemID, username, item.qty, date))
                self.conn.commit()

            # display the receipt
            self.user.Cart.printReceipt(items)

            # empty the cart
            self.user.Cart.items = []
            
            print("Order Has Been Placed\n")

            options = ["Continue Browsing"]
            self.optionSelection(options)


    # function to view past orders
    def orderHistory(self):
        self.printTitle("Order History")
        if self.user.loggedIn:
            # get the user's past orders from stored function
            self.cur.execute("SELECT * FROM get_orders(%s)", (self.user.username,))
            result = self.cur.fetchall()
            if not result:
                print("No Past Orders\n")
                options = ["Return to Main Menu"]
                self.optionSelection(options)
            else:
                currentOrder = result[0]
                # print the past orders
                print("{:^10} {:^15} {:^10} {:^10}  {:^10}".format('Order ID', 'Plant Name', 'Price', 'Quantity', 'Date'))
                print("{:^10} {:^15} {:^10} {:^10}  {:^10}".format('--------', '----------', '-----', '--------', '----'))
                for order in result:
                    if int(order[0]) > int(currentOrder[0]):
                        currentOrder = order
                        print("-"*62)
                    if order[0] == currentOrder[0]:
                        print("{:^10} {:^15} {:^10} {:^10} {:^15}".format(order[0], order[1], order[2], order[3], order[4].strftime('%Y-%m-%d')))               
                print("-"*62)
                print("\n")
                options = ["Return to Main Menu"]
                self.optionSelection(options)


# ******************
# SETTINGS FUNCTIONS
# ******************


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
        email = input("Enter A New Email: ")
        validEmail = self.validateEmail(email)
        while not validEmail:
            email = input("Enter A New Email: ")
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
        print("\nPhone Number Should Be Entered As Ten Consecutive Digits\n")
        phone = input("Enter A New Phone Number: ")
        validPhone = self.validatePhone(phone)
        while not validPhone:
            print("\n")
            phone = input("Enter A Phone Number: ")
            validPhone = self.validatePhone(phone)
        if validPhone:
            self.cur.execute('UPDATE customers SET phone = %s WHERE username = %s', (phone, self.user.username))
            self.conn.commit()
            self.user.phone = phone
            print("\nPhone Number Has Been Successfully Updated\n")

        options = ["Return to Settings"]
        self.optionSelection(options)


# **************
# START FUNCTION
# **************


    # function for welcome page
    def start(self):
        self.clearConsole()
        self.printTitle("The Hidden Leaf")
        if self.user.loggedIn:
            print(f"Welcome {self.user.fname}!\n")
            options = ["Browse For Plants", "Order History", "User Settings", "Exit"]
            self.optionSelection(options)
        else:
            options = ["Login", "Sign Up", "Browse For Plants", "Exit"]
            self.optionSelection(options)