class User:
    def __init__(self, username, password, fname, lname, email, phone=None, loggedIn=False):
        self.username = username
        self.password = password 
        self.fname = fname
        self.lname = lname 
        self.email = email 
        self.phone = phone
        self.loggedIn = loggedIn

    def login(self, username, fname, lname, email):
        self.username = username
        self.fname = fname
        self.lname = lname
        self.email = email
        self.loggedIn = True
        

    def logout(self):
        pass