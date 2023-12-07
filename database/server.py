from database import *
import random
import os
import re
from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)
 
host = 'localhost'
root = 'root'
# password = open('database\password', 'r').readline()
password = '21nhkumCa&'
databse_name = 'project3'
db = Database(host,root,password,databse_name)
connection = db.create_server_connection()

# generate ID in given length
def ID_generator(length):
    result=''
    for i in range(length):
        result += f'{random.randint(0,9)}'
    return result
def addTenant(id, name, phone, email, apartment_number):
    args = (int(id), name, phone, email, apartment_number)
    query = 'INSERT INTO tenant VALUES(%s, %s, %s, %s, CURRENT_TIMESTAMP, NULL, %s)'
    db.execute_query(connection, query, args)
def getTenantByEmail(email):
    query = f'''
            SELECT * FROM tenant WHERE email='{email}';
            '''
    return db.read_query(connection, query)

def addRequest(request_id, apartNum, area, description, image_path, tenant_id):
    args = (int(request_id),int(apartNum), area, description, image_path, int(tenant_id))
    query = 'INSERT INTO request VALUES(%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, "pending", %s)'
    db.execute_query(connection, query, args)
def completeRequest(request_id, status):
    query = f'''
            UPDATE request
            SET status='{status}'
            WHERE ID={request_id};
             '''
    db.execute_query(connection, query, None)
def checkoutTenant(id):
    query = f'''
            UPDATE tenant
            SET check_out=CURRENT_TIMESTAMP
            WHERE ID={id};
            '''
    db.execute_query(connection, query, None)
def getAllItems():
    return db.read_query(connection, 'select * from request;')
def getItemById(id):
    return db.read_query(connection, f'SELECT * from request where ID ={id};')
def getRequestByApartNum(num):
    return db.read_query(connection, f'SELECT * from request where apartment_number={num};')
def getRequestByFilter(area, status, dateFrom, dateTo):
    query = f'''
            SElECT * FROM request WHERE area='{area}' AND status='{status}' 
                AND DATE(request_time) BETWEEN '{dateFrom}' AND '{dateTo}';
            '''
    return db.read_query(connection, query)
def getRequestByDateRange(dateFrom, dateTo):
    query = f'''
            SElECT * FROM request WHERE DATE(request_time) BETWEEN '{dateFrom}' AND '{dateTo}';
            '''
    return db.read_query(connection, query)

def searchItem(value):
    query = f'''
            SELECT * FROM projectTwo
            WHERE name LIKE '%{value}%'
            OR category LIKE '%{value}%';'''
    return db.read_query(connection, query)

# Manager Section
def getAllTenants():
    return db.read_query(connection, 'select * from tenant')
def deleteTenant(id):
    query = f'DELETE FROM tenant where ID={id};'
    db.execute_query(connection, query, None)
def getTenantByID(ID):
    query = f'''
            SELECT * FROM tenant WHERE ID={ID};
            '''
    return db.read_query(connection, query)
def updateTenant(id, name, phone, email, apartNum):
    query = f'''UPDATE tenant 
                SET name='{name}', phone_number='{phone}', email='{email}', apartment_number={apartNum}
                WHERE ID={id};'''
    db.execute_query(connection, query, None)

def checkAllDigit(str):
    nonDigit = re.compile(r"[^0-9]")
    return bool(nonDigit.search(str))
    

class Requests():
    def __init__(self, requests):
        self.requests = requests
    def getRequests(self):
        return self.requests
    def setRequests(self, requests):
        self.requests = requests
# Product class
list_requests = Requests(None)

class Tenants():
    def __init__(self, tenants):
        self.tenants = tenants
    def getTenants(self):
        return self.tenants
    def setTenants(self, tenants):
        self.tenants = tenants
tenants_list = Tenants(None)

# variables
area = ['Bathroom', 'Bedroom', 'Living Room', 'Kitchen', 'Outdoor']
status = ['pending', 'completed']


# MT
@app.route('/MT_page')
def MTpage():
    if(list_requests.getRequests() == None): 
        list_requests.setRequests(getAllItems())
    requests = list_requests.getRequests()
    sortBy = ['Apartment #', 'Area', 'Date', 'Status']
    return render_template('MT_page.html', requests = requests, sortBy = sortBy, area=area, status=status)
@app.route('/refresh', methods=['POST', 'GET'])
def refresh():
    list_requests.setRequests(None)
    return redirect('/MT_page')

#Manager
@app.route('/Manager')
def directManager():
    if(tenants_list.getTenants() == None): 
        tenants_list.setTenants(getAllTenants())
    tenants = tenants_list.getTenants()
    sortBy = ['ID', 'Name']
    return render_template('manager_page.html', tenants=tenants, sortBy=sortBy)
@app.route('/refresh_manager_page', methods=['POST', 'GET'])
def refresh_manager_page():
    tenants_list.setTenants(None)
    return redirect('/Manager')

# Handle adding tenant
@app.route('/add_item')
def add_item():
    return render_template('add_item.html')
@app.route('/add', methods=['POST', 'GET'])
def tenant():
    id = ID_generator(9)
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    apartment_number = request.form.get("apartNum")
    addTenant(id, name, phone, email, apartment_number)
    tenants_list.setTenants(None)
    return redirect('/Manager')


# Tenant Login
@app.route('/Tenant')
def directTenant():
    return render_template('tenant_login.html')
@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email')
    tenant = getTenantByEmail(email)
    if(len(tenant) <= 0):
        return render_template('tenant_login.html')
    return render_template('request.html', tenant=tenant, area=area)
@app.route('/requests/<tenant_id>', methods=['POST', 'GET'])
def requests(tenant_id):
    tenant = getTenantByID(int(tenant_id))
    tenant = tenant[0]
    tenant = tenant[:1] + tenant[-1:]
    apartNum = tenant[-1]
    request_id = ID_generator(5)
    area = request.form.get("area")
    description = request.form.get("description")
    image = request.files['imageFile']
    if(image != None):
        image.filename = f'database\static\images\{request_id}.png'
        image.save(image.filename)
        file_path = f'images/{request_id}.png'
    else: file_path = None
    addRequest(request_id, apartNum, area, description, file_path, tenant_id)
    tenant = getTenantByID(int(tenant_id))
    return render_template('request.html', tenant=tenant)


# Handle Deleting tenant
@app.route('/delete/<id>')
def delete(id):
    deleteTenant(int(id))
    # os.remove(f'database\static\images\{id}.png')
    tenants_list.setTenants(None)
    return redirect('/Manager')
# Handle Updating items
@app.route('/update/<id>', methods=['POST'])
def update(id):
    if(len(id) > 5):
        name = request.form.get("name")
        phone_number = request.form.get("phone")
        email = request.form.get("email")
        apartment_number = request.form.get("apartNum")
        updateTenant(int(id), name, phone_number, email, apartment_number)
        tenants_list.setTenants(None)
        relode = '/Manager'
    else:
        status = request.form.get("status")
        completeRequest(int(id), status)
        list_requests.setRequests(None)
        relode = '/MT_page'
    return redirect(relode)
# Checkout Tenant
@app.route('/checkout/<id>', methods=['POST'])
def checkout(id):
    checkoutTenant(id)
    return redirect('/Manager')
# display item
@app.route('/view/<id>')
def display(id):
    tenant = None
    request = None
    if len(id) > 5: tenant = getTenantByID(int(id))
    else: request = getItemById(int(id))
    return render_template('view.html', request=request, tenant=tenant, status=status)

# Handle search
@app.route('/search', methods=['POST', 'GET'])
def search():
    value = request.form.get("searchID")
    if len(value) > 5:
        if checkAllDigit(value): tenant = getTenantByEmail(value)
        else: tenant = getTenantByID(int(value))
        tenants_list.setTenants(tenant)
        relode = "/Manager"
    else:
        requests = getRequestByApartNum(int(value))
        list_requests.setRequests(requests)
        relode = "/MT_page"
    return redirect(relode)
# Handle sorting
@app.route('/sorting', methods=['POST', 'GET'])
def sort():
    sortBy = request.form.get('sortBy')
    requests = list_requests.getRequests()
    if sortBy == 'Apartment #': sorted_List = sorted(requests, key=lambda x: x[1])
    elif sortBy == 'Area': sorted_List = sorted(requests, key=lambda x: x[2])
    elif sortBy == 'Date': sorted_List = sorted(requests, key=lambda x: x[4])
    elif sortBy == 'Status': sorted_List = sorted(requests, key=lambda x: x[6])
    else: sorted_List = requests
    list_requests.setRequests(sorted_List)
    return redirect('/MT_page')

# Filter
@app.route('/filter', methods=['POST', 'GET'])
def filter():
    selectedArea = request.form.get('area')
    status = request.form.get('status')
    dateFrom = request.form.get('dateFrom')
    dateTo = request.form.get('dateTo')
    # if(dateFrom and dateTo): requests = getRequestByDateRange(dateFrom, dateTo)
    # else: request = getAllItems()
    # requests = selectedArea
    requests = getRequestByFilter(selectedArea, status, dateFrom, dateTo)
    list_requests.setRequests(requests)
    return redirect('/MT_page')

if __name__ == '__main__':
    app.run(debug=True)