import mysql.connector
from mysql.connector import Error
import base64
from PIL import Image
import io 

class Database:
    def __init__(self, host_name, user_name, user_password, db_name):
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.db_name = db_name

    def create_server_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password,
                database=self.db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")
        return connection
    
    def execute_query(self, connection, query, args):
        cursor = connection.cursor()
        try:
            if(args!=None):cursor.execute(query, args)
            elif(args==None):cursor.execute(query)
            connection.commit()
            print("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    # use it to get data from tables
    def read_query(self, connection, query):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            print("Query successful")
            return result
        except Error as err:
            print(f"Error: '{err}'")

# password = open('database\password', 'r').readline()
# connection = create_server_connection("localhost", "root", password, "project2")

# file = open('database\images\image1.png', 'rb').read()
# file = base64.b64encode(file)

# q = 'INSERT INTO projectTwo VALUES(%s, %s, %s, %s, %s)'
# args = ('2314214', 'Loam', 'sfdgdsfg', file, 'product')

# cur = connection.cursor()
# cur.execute(q, args)
# connection.commit()

# q = "SELECT image from projectTwo where ID = 2314214;"
# data = read_query(connection, q)
# image = data[0][0]
# binary_data = base64.b64decode(image)
# image = Image.open(io.BytesIO(binary_data))
# image.show()

