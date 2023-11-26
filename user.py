class User:
    def __init__(self, username, password, fname, lname, email, phone=None, loggedIn=False):
        self.username = username
        self.password = password 
        self.fname = fname
        self.lname = lname 
        self.email = email 
        self.phone = phone
        self.loggedIn = loggedIn
        self.Cart = self.Cart()  # create a cart for the user

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

    class Cart:
        def __init__(self):
            self.items = []


        # class to represent items in cart
        class CartItem: 
            def __init__(self, itemID, itemName, price, qty):
                self.itemID = itemID
                self.itemName = itemName
                self.price = price
                self.qty = qty


        def isEmpty(self):
            if not self.items:
                return True
            else:
                return False


        # function to add item to cart
        def addItem(self, itemID, itemName, price, qty):
            # check if item is already in cart
            existingItem = False
            if not self.isEmpty():
                for item in self.items: 
                    if item.itemID == itemID:
                        existingItem = True
            if existingItem:
                print("\nItem Already In Cart\n")
            else:
                self.items.append(self.CartItem(itemID, itemName, price, qty))
                print("\nItem Added To Cart\n")
        


        # function to view cart
        def viewCart(self):
            if self.isEmpty():
                print("No items in cart. \n")
            else:
                totalPrice = 0
                for item in self.items:
                    print(f"Name: {item.itemName}\nPrice: ${item.price}\nQuantity: {item.qty}\n")
                    totalPrice += item.price * item.qty
                print(f"Total Price: ${totalPrice}\n")


        # function to remove item from cart
        def removeItem(self, itemName):
            for item in self.items:
                if item.itemName == itemName:
                    self.items.remove(item)


        # function to update item quantity
        def updateItem(self, itemName, new_qty):
            for item in self.items:
                if item.itemName == itemName:
                    item.qty = new_qty 


        # function to print receipt
        def printReceipt(self, items):
            totalPrice = 0
            print("{:<10} {:<15} {:<10} {:<10}".format('Item ID', 'Item Name', 'Price', 'Quantity'))
            print("{:<10} {:<15} {:<10} {:<10}".format('-------', '---------', '-----', '--------'))
            for item in items:
                print("{:<10} {:<15} {:<10} {:<10}".format(item.itemID, item.itemName, item.price, item.qty))
                totalPrice += item.price * item.qty
            print(f"\nTotal Price: ${totalPrice}\n")
