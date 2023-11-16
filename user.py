class User:
    def __init__(self, username, password, fname, lname, email, phone=None, loggedIn=False):
        self.username = username
        self.password = password 
        self.fname = fname
        self.lname = lname 
        self.email = email 
        self.phone = phone
        self.loggedIn = loggedIn

    def login(self, username, fname, lname, email, phone):
        self.username = username
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone
        self.loggedIn = True     

    def logout(self):
        self.username = "guest"
        self.fname = ""
        self.lname = ""
        self.loggedIn = False 

    class Cart: 
        def __init__(self, itemID, itemName, price, qty):
            self.itemID = itemID