from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion



def create_connection():
    return connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )


# db_conn = connections.Connection(
#     host=customhost,
#     port=3306,
#     user=customuser,
#     password=custompass,
#     db=customdb

# )
output = {}
table = 'employee'




@app.route("/", methods=['GET', 'POST'])
def dashboard():
    connection = create_connection()
    todayDate= datetime.today().strftime('%Y-%m-%d')

    coutAllEmployee="SELECT COUNT(*) FROM employee"
    countTodayCheckInEmployee ="SELECT count(*) FROM attendance WHERE date=%s AND check_in IS NOT NULL"
    countTodayCheckOutEmployee ="SELECT count(*) FROM attendance WHERE date=%s AND check_out IS NOT NULL"
    countTodayOnLeaveEmployee ="SELECT count(*) FROM attendance WHERE date=%s AND on_leave IS NOT NULL"
    countMale="SELECT COUNT(*) FROM employee WHERE gender='Male'"
    countFemale="SELECT COUNT(*) FROM employee WHERE gender='Female'"

# try:
    cursor = connection.cursor()
    cursor.execute(coutAllEmployee)
    totalEmployee = cursor.fetchone()
    cursor.execute(countTodayCheckInEmployee,todayDate)
    totalEmployeeCheckIn = cursor.fetchone()
    cursor.execute(countTodayCheckOutEmployee,todayDate)
    totalEmployeeCheckOut = cursor.fetchone()
    cursor.execute(countTodayOnLeaveEmployee,todayDate)
    totalEmployeeOnLeave = cursor.fetchone()
    cursor.execute(countMale)
    totalMale = cursor.fetchone()
    cursor.execute(countFemale)
    totalFemale = cursor.fetchone()
    connection.commit()
# except:
#     return str("Something went wrong")
# finally:
    connection.close()

    return render_template('index.html',totalEmployee=totalEmployee,totalEmployeeCheckIn=totalEmployeeCheckIn,
    totalEmployeeCheckOut=totalEmployeeCheckOut,totalEmployeeOnLeave=totalEmployeeOnLeave,todayDate=todayDate,
    totalMale=totalMale,totalFemale=totalFemale)

@app.route("/employee", methods=['GET', 'POST'])
def employee():

    connection = create_connection()
    getAllEmployee = "SELECT * FROM employee"
    coutAllEmployee="SELECT COUNT(*) FROM employee"
    countMale="SELECT COUNT(*) FROM employee WHERE gender='Male'"
    countFemale="SELECT COUNT(*) FROM employee WHERE gender='Female'"
    cursor = connection.cursor()

# try:
    cursor.execute(getAllEmployee)
    employeeData = cursor.fetchall()
    cursor.execute(coutAllEmployee)
    totalEmployee = cursor.fetchone()
    cursor.execute(countMale)
    totalMale = cursor.fetchone()
    cursor.execute(countFemale)
    totalFemale = cursor.fetchone()
    connection.commit()
# except:
#     return str("Something went wrong")
# finally:
    connection.close()
    return render_template('employee.html',employeeData=employeeData,totalEmployee=totalEmployee,totalMale=totalMale,totalFemale=totalFemale)

@app.route('/viewEmployee/<employeeId>')
def viewEmployee(employeeId):
    connection = create_connection()
    getEmployeeSql = "SELECT * FROM employee where id= %s"
    getEmployeePayrollSql="SELECT * FROM payroll WHERE employee_id=%s"
    getEmployeeAttendanceSql="SELECT * FROM attendance WHERE employee_id=%s"
    cursor = connection.cursor()

# try:
    cursor.execute(getEmployeeSql,(employeeId))
    employeeData = cursor.fetchone()
    cursor.execute(getEmployeePayrollSql,(employeeId))
    employeePayroll = cursor.fetchall()
    cursor.execute(getEmployeeAttendanceSql,(employeeId))
    employeeAttendance = cursor.fetchall()
    connection.commit()
# except:
#     return str("Something went wrong")
# finally:
    
    connection.close()
    return render_template('employeeProfile.html',employeeData=employeeData,employeePayroll=employeePayroll,employeeAttendance=employeeAttendance)

@app.route("/addEmployee", methods=['GET', 'POST'])
def addEmployee():
    return render_template('addEmployee.html')

@app.route('/editEmployee/<employeeId>', methods=['GET', 'POST'])
def editEmployee(employeeId):
    connection = create_connection()
    getEmployeeSql = "SELECT * FROM employee where id= %s"
    cursor = connection.cursor()
# try:
    cursor.execute(getEmployeeSql,(employeeId))
    employeeData = cursor.fetchone()
    connection.commit()
# except:
#     return str("Something went wrong")        
# finally:
    connection.close()

    return render_template('editEmployee.html',employeeData=employeeData)

@app.route('/deleteEmployee/<employeeId>', methods=['GET', 'POST'])
def deleteEmployee(employeeId):
    connection = create_connection()
    deleteEmployeeSql = "DELETE FROM employee where id= %s"
    cursor = connection.cursor()
# try:
    cursor.execute(deleteEmployeeSql,(employeeId))
    connection.commit()
# except:
#     return str("Something went wrong")
# finally:
    connection.close()
    return render_template('deleteEmployee.html',employeeId=employeeId)







@app.route("/addemp", methods=['POST'])
def AddEmp():
    connection = create_connection()
    employeeId = request.form['employeeId']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    gender = request.form['gender']
    dateOfBirth = request.form['dateOfBirth']
    identityCardNumber = request.form['identityCardNumber']
    email = request.form['email']
    mobile = request.form['mobile']
    address = request.form['address']
    salary = request.form['salary']
    department = request.form['department']
    hireDate = datetime.today().strftime('%Y-%m-%d')


    emp_image_file = request.files['image']
    split_tup = os.path.splitext(emp_image_file.filename)
    file_extension = split_tup[1]
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = connection.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (employeeId, firstName, lastName, gender, dateOfBirth, 
        identityCardNumber, email, mobile, address, salary, department, emp_image_file, hireDate))
        # cursor.execute(insert_sql)
        connection.commit()
        emp_name = "" + firstName + " " + lastName
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(employeeId) + "_image_file"+file_extension
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            update_sql = "UPDATE employee set image = %s WHERE id=%s"
            cursor = connection.cursor()
            cursor.execute(update_sql, (object_url,employeeId))
            connection.commit()


        except Exception as e:
            print("running expection")
            print(e)
            return str(e)

    finally:
        print("running finally")
        
        connection.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name, employeeId=employeeId)

@app.route("/editEmp", methods=['POST'])
def editEmp():
    connection = create_connection()
    employeeId = request.form['employeeId']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    gender = request.form['gender']
    dateOfBirth = request.form['dateOfBirth']
    identityCardNumber = request.form['identityCardNumber']
    email = request.form['email']
    mobile = request.form['mobile']
    address = request.form['address']
    salary = request.form['salary']
    department = request.form['department']
    hireDate = request.form['hireDate']
    currentEmployeeId = request.form['currentEmployeeId']

    emp_image_file = request.files['image']
    split_tup = os.path.splitext(emp_image_file.filename)
    file_extension = split_tup[1]
   

    if emp_image_file.filename == "":
        updateEmployeeSql = "UPDATE employee set id= %s,first_name= %s,last_name= %s,gender= %s,date_of_birth= %s,identity_card_number= %s,email= %s,mobile= %s,address= %s,salary= %s,department= %s,hire_date= %s WHERE id=%s"
        cursor = connection.cursor()
        
        try:
            cursor.execute(updateEmployeeSql, (employeeId, firstName, lastName, gender, dateOfBirth,identityCardNumber, email, mobile, address, salary, department, hireDate,currentEmployeeId))
            emp_name = "" + firstName + " " + lastName
            connection.commit()
        finally:
            connection.close()
        return render_template('editEmpOutput.html', name=emp_name, employeeId=employeeId)

    else:
        updateEmployeeSql = "UPDATE employee set id= %s,first_name= %s,last_name= %s,gender= %s,date_of_birth= %s,identity_card_number= %s,email= %s,mobile= %s,address= %s,salary= %s,department= %s,image= %s,hire_date= %s WHERE id=%s"
        cursor = connection.cursor()


    try:
        cursor.execute(updateEmployeeSql, (employeeId, firstName, lastName, gender, dateOfBirth, 
        identityCardNumber, email, mobile, address, salary, department, emp_image_file, hireDate,currentEmployeeId))
        # cursor.execute(insert_sql)
        connection.commit()
        emp_name = "" + firstName + " " + lastName
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(employeeId) + "_image_file"+ file_extension
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            update_sql = "UPDATE employee set image = %s WHERE id=%s"
            cursor = connection.cursor()
            cursor.execute(update_sql, (object_url,employeeId))
            connection.commit()


        except Exception as e:
            print("running expection")
            print(e)
            return str(e)

    finally:
        print("running finally")
        
        connection.close()

    print("all modification done...")
    return render_template('editEmpOutput.html', name=emp_name, employeeId=employeeId)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
