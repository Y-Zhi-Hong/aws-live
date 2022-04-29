from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'




@app.route("/", methods=['GET', 'POST'])
def dashboard():
    return render_template('index.html')

@app.route("/employee", methods=['GET', 'POST'])
def allEmployee():
    return render_template('employee.html')

@app.route("/addEmployee", methods=['GET', 'POST'])
def addEmployee():
    return render_template('addEmployee.html')






@app.route("/addEmp", methods=['GET', 'POST'])
def addEmp():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
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
    hireDate = date.today()
    emp_image_file = request.files['image']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (employeeId, firstName, lastName, gender, dateOfBirth, 
        identityCardNumber, email, mobile, address, salary, department, hireDate, emp_image_file))
        db_conn.commit()
        emp_name = "" + firstName + " " + lastName
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(employeeId) + "_image_file"
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

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name, employeeId=employeeId)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
