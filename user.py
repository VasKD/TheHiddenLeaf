class User:
    def __init__(self, username, password, fname, lname, email, phone=None, loggedIn=False):
        self.username = username
        self.password = password 
        self.fname = fname
        self.lname = lname 
        self.email = email 
        self.phone = phone
        self.loggedIn = loggedIn
        self.Cart = self.Cart() # create a cart for the user

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
        self.cart = None

    class CartItem:
        def __init__(self, itemID, itemName, price, qty):
            self.itemID = itemID
            self.itemName = itemName
            self.price = price
            self.qty = qty

    class Cart: 
        def __init__(self):
            self.items = []

        def addItem(self, itemID, itemName, price, qty):
            self.items.append(User.CartItem(itemID, itemName, price, qty))

        def removeItem(self, itemID):
            for item in self.items:
                if item.itemID == itemID:
                    self.items.remove(item)

        def updateItem(self, itemID, new_qty):
            for item in self.items:
                if item.itemID == itemID:
                    item.qty = new_qty 