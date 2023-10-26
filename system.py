import psycopg2
import os, sys


class System:
    def __init__(self):
        self.pages = {"Start": self.start,
                    "Login":self.login,
                    "Sign Up":self.signUp,
                    "Browse For Plants":self.browse,
                    "Exit": self.leaf
        }

        # connect to local db 
        self.conn = psycopg2.connect(database = "TheHiddenLeaf", 
                                user = "postgres", 
                                host= 'localhost',
                                password = "postgres",
                                port = 5432)

        # Open a cursor to perform database operations
        self.cur = self.conn.cursor()

        
        # create plants table and commit to db
        plants = """CREATE TABLE IF NOT EXISTS plants(
            plantID CHAR(3) PRIMARY KEY,
            name VARCHAR(25),
            price NUMERIC(2, 2),
            discount NUMERIC(3, 2) DEFAULT NULL,
            qty INTEGER,
            type VARCHAR(25),
            species VARCHAR(50),
            duration VARCHAR(15),
            description TEXT); """

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
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(8),
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
   
    # deconstructor for closing the db connection
    def __del__(self):
        self.conn.close()


    # function to clear the console
    def clearConsole(self):
        if os.name == 'nt':
            os.system('cls')
        else: 
            os.system('clear')



    """ NEW / MODIFIED FUNCTIONS """
    
    # function to exit the app
    def leaf(self):
        self.printTitle("The Hidden Leaf")
        sys.exit("Thank You For Shopping at The Hidden Leaf! Have a Nice Day!\n")


    # function to print the title of a page
    def printTitle(self, title):
        numDashes = 28 - len(title)
        oneSideDashes = (numDashes // 2) - 1
        print("===========================")
        print('='*oneSideDashes + ' ' + title + ' ' + '='*oneSideDashes)
        print("===========================\n")


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
        self.comingSoon(self.start)
    

    # function for the Sign Up page
    def signUp(self):
        self.printTitle("Sign Up")
        self.comingSoon(self.start)


    # function for browsing the plants (as a guest)
    def browse(self):
        self.printTitle("Browse For Plants")
        self.comingSoon(self.start)
    

    # function for welcome page
    def start(self):
        self.clearConsole()
        self.printTitle("The Hidden Leaf")
        options = ["Login", "Sign Up", "Browse For Plants", "Exit"]
        self.optionSelection(options)

    
