from django.shortcuts import render
from django.http import HttpResponse
import mysql.connector
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import jwt

JWT_SECRET = "KFJ4nKcDErTVBAK8ATQ1GdoMZrqtsiuX"
dataBase = mysql.connector.connect(
    host ="localhost",
    user ="root",
    passwd ="MySQL123!",
    database = "todo_app"
)
print("Connected")

def home(request):
    return HttpResponse("Server running successfully!")


@api_view(['POST'])
def login(request):
    if request.method == "POST":
        body = json.loads(json.dumps(request.data))
        response = HttpResponse()
        if 'email' not in body.keys() or 'password' not in body.keys():
            response.status_code = 400
            response.content = "Bad Request"
            return response
        email = body["email"]
        password = body["password"]
        cursorObj = dataBase.cursor()
        query = "SELECT userID FROM user where email=%s and password=%s;"
        cursorObj.execute(query,(email,password))
        results = cursorObj.fetchall()
        
        if(len(results) > 0):
            response.status_code = 200
            token = jwt.encode({"userID":str(results[0][0])}, JWT_SECRET, algorithm="HS256")
            response.content = "JWT = " + token
        else:
            response.status_code = 404
            response.content = "User Not Found"
        return response
    else:
        return methodNotAllowed()

@api_view(['POST'])
def addTask(request):
    if request.method == "POST":
        response = HttpResponse()
        if 'Authorization' not in request.headers.keys():
            response.status_code = 404
            response.content = 'Token not found' 
            return response
        
        encoded_jwt = request.headers['Authorization']
        token = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])

        body = json.loads(json.dumps(request.data))
        
        if 'userID' not in token.keys():
            response.status_code = 401
            response.content = 'Unauthorized' 
            return response
        userID = token['userID']

        createdDate = str(datetime.datetime.now())

        bodyKeys = body.keys()
        if 'task' not in bodyKeys:
            response.status_code = 400
            response.content = 'task description is missing' 
            return response
        if 'priorityID' not in bodyKeys:
            response.status_code = 400
            response.content = 'Priority ID is missing' 
            return response
        taskDescription = body['task']
        priorityID = body['priorityID']
        statusID = 1
        if 'dueDate' in bodyKeys:
            dueDate = body['dueDate']
        else:
            dueDate = None
        
        query = "INSERT INTO task (description, userID, priorityID, statusID, createdDate, dueDate) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (taskDescription, userID, priorityID, statusID, createdDate, dueDate)
        cursorObj = dataBase.cursor()
        cursorObj.execute(query, val)
        dataBase.commit()

        response.status_code = 200
        response.content = 'Added Successfully' 
        return response
    else:
        return methodNotAllowed()

@api_view(['GET'])
def getAllTasks(request):
    if request.method == "GET":
        response = HttpResponse()
        if 'Authorization' not in request.headers.keys():
            response.status_code = 404
            response.content = 'Token not found' 
            return response
        
        encoded_jwt = request.headers['Authorization']
        token = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        if 'userID' not in token.keys():
            response.status_code = 401
            response.content = 'Unauthorized' 
            return response
        userID = token['userID']

        params = json.loads(json.dumps(request.GET))
        keys = params.keys()

        cursorObject = dataBase.cursor()
  
        query = "SELECT taskID, description, dueDate, createdDate, taskPriority.priority, taskStatus.status FROM task JOIN taskPriority ON task.priorityID = taskPriority.priorityID JOIN taskStatus ON task.statusID = taskStatus.statusID WHERE userID=%s "
        val = [userID]

        if 'priorityID' in keys:
            priorityID = params['priorityID']
            query += "AND task.priorityID = %s "
            val.append(priorityID)
        
        if 'dueDateBreached' in keys:
            dueDate = params['dueDateBreached']
            now = str(datetime.datetime.now())
            if dueDate == 'True':
                query += "AND task.dueDate<'"+now+"' "
            else:
                query += "AND task.dueDate>='"+now+"' "

        query += "ORDER BY "
        if 'sortBy' in keys:
            sortBy = params['sortBy']
            if sortBy == 'dueDate':
                query += "dueDate DESC"
            elif sortBy == 'priority':
                query += "task.priorityID"
            else:
                query += "taskID DESC"
        else:
            query += "taskID DESC"

        cursorObject.execute(query, val)
        
        result = cursorObject.fetchall()
        tasks = []
        format_string = '%Y-%m-%d %H:%M:%S'
        for record in result:
            if type(record[2]) == datetime.datetime:
                temp = {"taskID":record[0], "description":record[1], "dueDate":record[2].strftime(format_string), "createdDate": record[3].strftime(format_string), "priority":record[4], "status":record[5]}
            else:
                temp = {"taskID":record[0], "description":record[1], "dueDate":None, "createdDate": record[3].strftime(format_string), "priority":record[4], "status":record[5]}
            tasks.append(temp)

        response.status_code = 200
        response.content = list([tasks])
        response.headers['Content-Type'] = 'application/JSON'
        return response
    else:
        return methodNotAllowed()

@api_view(['POST'])
def editTask(request):
    if request.method == "POST":
        response = HttpResponse()
        if 'Authorization' not in request.headers.keys():
            response.status_code = 404
            response.content = 'Token not found' 
            return response
        
        encoded_jwt = request.headers['Authorization']
        token = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        if 'userID' not in token.keys():
            response.status_code = 401
            response.content = 'Unauthorized' 
            return response
        userID = token['userID']

        body = json.loads(json.dumps(request.data))
        keys = body.keys()
        if 'description' not in keys and 'dueDate' not in keys and 'priorityID' not in keys:
            response.status_code = 400
            response.content = 'Bad Request' 
            return response
        
        query = "UPDATE task SET "
        val = []

        if 'description' in keys:
            query += "description=%s, "
            val.append(body['description'])
        if 'dueDate' in keys:
            query += "dueDate=%s, "
            val.append(body['dueDate'])
        if 'priorityID' in keys:
            query += "priorityID=%s, "
            val.append(body['priorityID'])
        if 'taskID' not in keys:
            response.status_code = 400
            response.content = 'Bad Request: taskID is missing' 
            return response
        query = query[:len(query)-2] + " WHERE taskID = %s and userID = %s"
        val.append(body['taskID'])
        val.append(userID)

        cursorObject = dataBase.cursor()
        cursorObject.execute(query, val)

        response.status_code = 200
        response.content = 'Update Successfully'
        return response
    else:
        return methodNotAllowed()

@api_view(['POST'])
def completeTask(request):
    if request.method == "POST":
        response = HttpResponse()
        if 'Authorization' not in request.headers.keys():
            response.status_code = 404
            response.content = 'Token not found' 
            return response
        
        encoded_jwt = request.headers['Authorization']
        token = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        if 'userID' not in token.keys():
            response.status_code = 401
            response.content = 'Unauthorized' 
            return response
        userID = token['userID']
        params = json.loads(json.dumps(request.GET))
        if 'taskID' not in params.keys():
            response.status_code = 400
            response.content = 'Bad Request' 
            return response
        taskID = params['taskID']
        query = "UPDATE task SET statusID = CASE WHEN statusID = '1' THEN '2' WHEN statusID = '2' THEN '1' END WHERE taskID = %s AND userID = %s"
        val = [taskID, userID]
        cursorObject = dataBase.cursor()
        cursorObject.execute(query, val)
        response.status_code = 200
        response.content = "Updated Successfully"
        return response

    else:
        return methodNotAllowed()

@api_view(['POST'])
def cancelTask(request):
    if request.method == "POST":
        response = HttpResponse()
        if 'Authorization' not in request.headers.keys():
            response.status_code = 404
            response.content = 'Token not found' 
            return response
        
        encoded_jwt = request.headers['Authorization']
        token = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        if 'userID' not in token.keys():
            response.status_code = 401
            response.content = 'Unauthorized' 
            return response
        userID = token['userID']
        params = json.loads(json.dumps(request.GET))
        if 'taskID' not in params.keys():
            response.status_code = 400
            response.content = 'Bad Request' 
            return response
        taskID = params['taskID']
        query = "UPDATE task SET statusID = CASE WHEN statusID = '1' THEN '3' WHEN statusID = '3' THEN '1' END WHERE taskID = %s AND userID = %s"
        val = [taskID, userID]
        cursorObject = dataBase.cursor()
        cursorObject.execute(query, val)
        response.status_code = 200
        response.content = "Updated Successfully"
        return response

    else:
        return methodNotAllowed()

def methodNotAllowed():
    response = HttpResponse()
    response.status_code = 405
    response.content = "Method Not Allowed"
    return response

def closeDB():
    dataBase.close()
    return HttpResponse("Successfully Closed Connection!")