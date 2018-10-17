import sqlite3


class DBHelper:
    
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
    
    def setup(self):
        
        #Restaurabt Table
        tblrest  = "CREATE TABLE IF NOT EXISTS restaurant (name text, phone text, lat text, long text)"
        nameidx  = "CREATE INDEX IF NOT EXISTS nameIndex ON restaurant (name ASC)"
        phoneidx = "CREATE INDEX IF NOT EXISTS phoneIndex ON restaurant (phone ASC)"
        latidx   = "CREATE INDEX IF NOT EXISTS latIndex ON restaurant (lat ASC)"
        longidx  = "CREATE INDEX IF NOT EXISTS longIndex ON restaurant (long ASC)"
        
        #Menu Table
        tblmenu  = "CREATE TABLE IF NOT EXISTS menu (name text, price text, size text, type text)"
        mnameidx  = "CREATE INDEX IF NOT EXISTS nameIndex ON menu (name ASC)"
        priceidx = "CREATE INDEX IF NOT EXISTS priceIndex ON menu (price ASC)"
        sizeidx   = "CREATE INDEX IF NOT EXISTS sizendex ON menu (size ASC)"
        typeidx   = "CREATE INDEX IF NOT EXISTS typeIndex ON menu (type ASC)"


        #Reservations Table
        reservartionsListTable = "CREATE TABLE IF NOT EXISTS ReservationsList (" \
            "Reservation_Id integer PRIMARY KEY, " \
                "Customer_Name text NOT NULL, " \
                    "Reservation_Date text," \
                        "Reservation_Hour text, " \
                            "Table_Id integer)"
        tblresv = "CREATE TABLE IF NOT EXISTS RestaurantTables (" \
            "Table_Id integer PRIMARY KEY, " \
            "Size integer NOT NULL, " \
            "Window BOOL)"
    

        #tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text)"
        #itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        #ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        #self.conn.execute(tblstmt)
        self.conn.execute(tblrest)
        self.conn.execute(tblmenu)
        self.conn.execute(reservartionsListTable)
        self.conn.execute(tblresv)


        #self.conn.execute(itemidx)
        #self.conn.execute(ownidx)
        self.conn.execute(nameidx)
        self.conn.execute(phoneidx)
        self.conn.execute(longidx)
        self.conn.execute(latidx)
        self.conn.execute(mnameidx)
        self.conn.execute(priceidx)
        self.conn.execute(sizeidx)
        self.conn.execute(typeidx)

        self.conn.commit()
    
    def create_restaurant(self, name, phone, lat, long):
        stmt = "INSERT INTO restaurant (name, phone, lat, long) VALUES (?, ?, ?, ?)"
        args = (name, phone, lat, long)
        self.conn.execute(stmt, args)
        self.conn.commit()
        res = "none"
    
    def get_restaurant(self, data):
        t=0
        for row in self.conn.execute("SELECT * FROM restaurant"):
            if row:
                res = row
                t=1

        if data == "name" and t==1:
            return res[0]
        elif data == "phone" and t==1:
            return res[1]
        elif data == "latitude" and t==1:
            return res[2]
        elif data == "longtitude" and t==1:
            return res[3]
        else:
            return "0"


    #Reservations methods
    def get_freetables(self,reservationDate,reservationHour):

        free_tables = "SELECT Table_Id FROM RestaurantTables WHERE Table_Id NOT IN (SELECT Table_Id FROM ReservationsList WHERE Reservation_Date = (?) AND Reservation_Hour = (?)) ;"
        args = (reservationDate, reservationHour)
        
        result = self.conn.execute(free_tables, args)
        freetables = []
        for value in result:
            freetables.append(value)
        
        return [x[0] for x in freetables]

    def add_reservation(self,customerName,reservationDate,table_ID,reservationHour):
    
        stmt = "INSERT INTO ReservationsList (Customer_Name,Reservation_Date,Table_ID,Reservation_Hour) VALUES (?,?,?,?)"
        args = (customerName,reservationDate,table_ID,reservationHour)
        self.conn.execute(stmt, args)
        self.conn.commit()
        
        
        stmt2 = "SELECT MAX(Reservation_ID) FROM ReservationsList"
        result = self.conn.execute(stmt2)
        for value in result:
            print("ID:",value)
        return str(value)
            
    def cancel_reservation(self, reservation_Id):
        stmt = "DELETE FROM ReservationsList WHERE Reservation_ID = (?)"
        args = (reservation_Id, )
        self.conn.execute(stmt, args)
        self.conn.commit()
    
    
    def get_List(self):
        stmt = "SELECT * FROM ReservationsList"
        result = self.conn.execute(stmt)
        reservationsList = []
        for value in result:
            reservationsList.append(value)
        return reservationsList
    
    
    
    def add_table(self, tableid, size, window):
        stmt = "INSERT INTO RestaurantTables (Table_Id, Size, Window) VALUES (?, ?, ?)"
        args = (tableid, size, window)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def add_menu(self, name, size, price, type):
        stmt = "INSERT INTO menu (name, size, price, type) VALUES (?, ?, ?, ?)"
        args = (name, size, price, type)
        self.conn.execute(stmt, args)
        self.conn.commit()
#
#    def delete_item(self, item_text, owner):
#        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
#        args = (item_text, owner )
#        self.conn.execute(stmt, args)
#        self.conn.commit()
#    
#    def get_items(self, owner):
#        stmt = "SELECT description FROM items WHERE owner = (?)"
#        args = (owner, )
#        return [x[0] for x in self.conn.execute(stmt, args)]