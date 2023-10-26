class User:
    def __init__(self, username, password, fname, lname, email, phone=None):
        self.username = username
        self.password = password 
        self.fname = fname
        self.lname = lname 
        self.email = email 
        self.phone = phone

    def login(self):
        pass

    def logout(self):
        pass