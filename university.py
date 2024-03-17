import os
import time
from urllib.parse import parse_qs
from html import escape
import psycopg2




def wrapBody(body, title="Student Enrollment Directory"):
    return (
        "<html>\n"
        "<head>\n"
        f"<title>{title}</title>\n"
        '<link rel="stylesheet" type="text/css" href="/static/style.css">\n'  
        "</head>\n"
        "<body>\n"
        "<header>\n"
        f"<h1>{title}</h1>\n"  
        "</header>\n"
        f"{body}\n"
        "<hr>\n"
        f"<p>This page was generated at {time.ctime()}.</p>\n"
        "</body>\n"
        "</html>\n"
    )




def get_qs_post(env):
    try:
        request_body_size = int(env.get("CONTENT_LENGTH", 0))
    except (ValueError):
        request_body_size = 0
    request_body = env["wsgi.input"].read(request_body_size).decode("utf-8")
    post = parse_qs(request_body)
    return parse_qs(env["QUERY_STRING"]), post




def showAllStudents(conn):
    cursor = conn.cursor()
    sql = """
    SELECT id, name
    FROM student
    ORDER BY id ASC
    """
    cursor.execute(sql)
    body = """
    <h2>Student List</h2>
    <p>
    <table class="student-table" border=1>
      <tr>
        <td><font size=+1'><b>Student ID</b></font></td>
        <td><font size=+1'><b>Student Name</b></font></td>
        <td><font size=+1'><b>Delete</b></font></td>
        <td><font size=+1'><b>Enrollment Info</b></font></td>
      </tr>
    """
    for row in cursor:
        body += (
            "<tr>"
            f"<td>{row[0]}</td>"
            f"<td>{row[1]}</td>"
            f"<td><form method='POST'><input type='hidden' name='student_id' value='{row[0]}'><input type='submit' name='deleteStudent' value='Delete'></form></td>"
            f"<td><form method='POST'><input type='hidden' name='student_id' value='{row[0]}'><input type='submit' name='viewStudentInfo' value='View Enrollment Information'></form></td>"
            "</tr>\n"
        )
    body += "</table>"
    return body


def showAddStudentForm():
    return """
    <h2>Add Student</h2>
    <p>
    <FORM METHOD="POST">
    <table class="add-student">
        <tr>
            <td>Student ID</td>
            <td><INPUT TYPE="TEXT" NAME="student_id" VALUE=""></td>
        </tr>
        <tr>
            <td>Student Name</td>
            <td><INPUT TYPE="TEXT" NAME="student_name" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addStudent" value="Add Student">
            </td>
        </tr>
    </table>
    </FORM>
    """


def addStudent(conn, student_id, student_name):
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO student (id, name) VALUES (%s, %s)"
        params = (student_id, student_name)
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount > 0:
            status_message = "Add Student Succeeded."
        else:
            status_message = "Add Student Failed."
    except psycopg2.Error as e:
        conn.rollback()
        status_message = f"Failed to add student: {e}"
    body = f"<h2>{status_message}</h2>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Student List">'
    body += '</form>'
    return body


def deleteStudent(conn, student_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (student_id,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Student Succeeded."
    else:
        return "Delete Student Failed."


def showStudentInfo(conn, student_id):
    cursor = conn.cursor()
    sql_enrolled = """
    SELECT course
    FROM enrolled
    WHERE student = %s
    """
    cursor.execute(sql_enrolled, (student_id,))
    enrolled_courses = [row[0] for row in cursor.fetchall()]
    sql_majors_in = """
    SELECT dept
    FROM majors_in
    WHERE student = %s
    """
    cursor.execute(sql_majors_in, (student_id,))
    majors = [row[0] for row in cursor.fetchall()]
    body = f"<h2>Student Information for Student ID: {student_id}</h2>"
    body += '<p class="enrolled-title">Enrolled Courses:</p>'
    body += "<ul>"
    for course in enrolled_courses:
        body += f"<li>{course}</li>"
        body += f"<form method='POST' action='/view_course_details'><input type='hidden' name='course_name' value='{course}'><input type='submit' name='viewCourseDetails' value='View Course Details'></form>"
    body += "</ul>"
    # body += "<p>Majors:</p>"
    # body += "<ul>"
    # for major in majors:
    #     body += f"<li>{major}</li>"
    #     body += f"<form method='POST' action='/view_department'><input type='hidden' name='dept_name' value='{major}'><input type='submit' name='viewDepartment' value='View Department'></form>"
    # body += "</ul>"
    return body




def showCourseDetails(conn, course_name):
    cursor = conn.cursor()
    sql_course_details = """
    SELECT course.number, course.title, room.number
    FROM course
    INNER JOIN room ON course.room = room.number
    WHERE course.number = %s
    """
    cursor.execute(sql_course_details, (course_name,))
    course_details = cursor.fetchone()
    body = f"<h2>Course Details for Course: {course_name}</h2>"
    body += '<p class="enroll-info">'
    body += f"Course Number: {course_details[0]}<br>"
    body += f"Title: {course_details[1]}<br>"
    body += f"Room: {course_details[2]}<br>"
    body += "</p>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Student List">'
    body += '</form>'
    return body




def showDepartment(conn, dept_name):
    cursor = conn.cursor()
    sql_department_details = """
    SELECT name, office
    FROM department
    WHERE name = %s
    """
    cursor.execute(sql_department_details, (dept_name,))
    department_details = cursor.fetchone()
    body = f"<h2>Department Details for Department: {dept_name}</h2>"
    body += "<p>"
    body += f"Department Name: {department_details[0]}<br>"
    body += f"Office: {department_details[1]}<br>"
    body += "</p>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Student List">'
    body += '</form>'
    return body




























def showAllRooms(conn):
    cursor = conn.cursor()
    sql = """
    SELECT number, capacity
    FROM room
    ORDER BY number ASC
    """
    cursor.execute(sql)
    body = """
    <h2>Room List</h2>
    <table class="student-table" border=1>
      <tr>
        <td><font size=+1'><b>Room Number</b></font></td>
        <td><font size=+1'><b>Capacity</b></font></td>
        <td><font size=+1'><b>Delete</b></font></td>
        <td><font size=+1'><b>Update</b></font></td>
      </tr>
    """
    for row in cursor:
        room_number = row[0]
        capacity = row[1]
        body += (
            "<tr>"
            f"<td>{room_number}</td>"
            f"<td>{capacity}</td>"
            f"<td><form method='POST'><input type='hidden' name='room_number' value='{room_number}'><input type='submit' name='deleteRoom' value='Delete'></form></td>"
            f"<td><form method='GET' action='/'><input type='hidden' name='room_number' value='{room_number}'><input type='hidden' name='showUpdateRoomForm' value='true'><input type='submit' name='showUpdateRoomFormButton' value='Update'></form></td>"
            "</tr>\n"
        )
    body += "</table>"
    return body








def showAddRoomForm():
    return """
    <h2>Add Room</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Room Number</td>
            <td><INPUT TYPE="TEXT" NAME="room_number" VALUE=""></td>
        </tr>
        <tr>
            <td>Capacity</td>
            <td><INPUT TYPE="TEXT" NAME="capacity" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addRoom" value="Add Room">
            </td>
        </tr>
    </table>
    </FORM>
    """




def deleteRoom(conn, room_number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM room WHERE number = %s", (room_number,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Room Succeeded."
    else:
        return "Delete Room Failed."




def addRoom(conn, room_number, capacity):
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO room (number, capacity) VALUES (%s, %s)"
        params = (room_number, capacity)
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount > 0:
            status_message = "Add Room Succeeded."
        else:
            status_message = "Add Room Failed."
    except psycopg2.Error as e:
        conn.rollback()
        status_message = f"Failed to add room: {e}"
    body = f"<h2>{status_message}</h2>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Room List">'
    body += '</form>'
    return body




def getUpdateRoomForm(conn, room_number):
    cursor = conn.cursor()
    sql = """
    SELECT *
    FROM room
    WHERE number=%s
    """
    cursor.execute(sql, (room_number,))
    data = cursor.fetchall()
    (room_number, capacity) = data[0]
    return """
    <h2>Update Room</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Room Number</td>
            <td><INPUT TYPE="TEXT" NAME="room_number" VALUE="%s"></td>
        </tr>
        <tr>
            <td>Capacity</td>
            <td><INPUT TYPE="TEXT" NAME="capacity" VALUE="%s"></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="hidden" name="room_number" value="%s">
            <input type="submit" name="completeUpdateRoom" value="Update">
            </td>
        </tr>
    </table>
    </FORM>
    """ % (
        room_number,
        capacity,
        room_number
    )




def updateRoom(conn, room_number, capacity):
    cursor = conn.cursor()
    sql = "UPDATE room SET capacity=%s WHERE number=%s"
    params = (capacity, room_number)
    cursor.execute(sql, params)
    conn.commit()
    if cursor.rowcount > 0:
        return "Update Room Succeeded. <form action='/' method='GET'><input type='submit' value='Back to Room List'></form>"
    else:
        return "Update Room Failed."
   














def showAllCourses(conn):
    cursor = conn.cursor()
    sql = """
    SELECT number, title, room
    FROM course
    ORDER BY number ASC
    """
    cursor.execute(sql)
    body = """
    <h2>Course List</h2>
    <table class="student-table" border=1>
      <tr>
        <td><font size=+1'><b>Course Number</b></font></td>
        <td><font size=+1'><b>Title</b></font></td>
        <td><font size=+1'><b>Room</b></font></td>
        <td><font size=+1'><b>Delete</b></font></td>
        <td><font size=+1'><b>Update</b></font></td>
      </tr>
    """
    for row in cursor:
        course_number = row[0]
        title = row[1]
        room = row[2]
        body += (
            "<tr>"
            f"<td>{course_number}</td>"
            f"<td>{title}</td>"
            f"<td>{room}</td>"
            f"<td><form method='POST'><input type='hidden' name='course_number' value='{course_number}'><input type='submit' name='deleteCourse' value='Delete'></form></td>"
            f"<td><form method='GET' action='/'><input type='hidden' name='course_number' value='{course_number}'><input type='hidden' name='showUpdateCourseForm' value='true'><input type='submit' name='showUpdateCourseFormButton' value='Update'></form></td>"
            "</tr>\n"
        )
    body += "</table>"
    return body




def showAddCourseForm():
    return """
    <h2>Add Course</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Course Number</td>
            <td><INPUT TYPE="TEXT" NAME="course_number" VALUE=""></td>
        </tr>
        <tr>
            <td>Title</td>
            <td><INPUT TYPE="TEXT" NAME="title" VALUE=""></td>
        </tr>
        <tr>
            <td>Room</td>
            <td><INPUT TYPE="TEXT" NAME="room" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addCourse" value="Add Course">
            </td>
        </tr>
    </table>
    </FORM>
    """


def addCourse(conn, course_number, title, room):
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO course (number, title, room) VALUES (%s, %s, %s)"
        params = (course_number, title, room)
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount > 0:
            status_message = "Add Course Succeeded."
        else:
            status_message = "Add Course Failed."
    except psycopg2.Error as e:
        conn.rollback()
        status_message = f"Failed to add course: {e}"
    body = f"<h2>{status_message}</h2>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Course List">'
    body += '</form>'
    return body


def deleteCourse(conn, course_number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM course WHERE number = %s", (course_number,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Course Succeeded."
    else:
        return "Delete Course Failed."






def getUpdateCourseForm(conn, course_number):
    cursor = conn.cursor()
    sql = """
    SELECT *
    FROM course
    WHERE number=%s
    """
    cursor.execute(sql, (course_number,))
    data = cursor.fetchall()
    (course_number, title, room) = data[0]
    return """
    <h2>Update Course</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Course Number</td>
            <td><INPUT TYPE="TEXT" NAME="course_number" VALUE="%s"></td>
        </tr>
        <tr>
            <td>Title</td>
            <td><INPUT TYPE="TEXT" NAME="title" VALUE="%s"></td>
        </tr>
        <tr>
            <td>Room</td>
            <td><INPUT TYPE="TEXT" NAME="room" VALUE="%s"></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="hidden" name="course_number" value="%s">
            <input type="submit" name="completeUpdateCourse" value="Update">
            </td>
        </tr>
    </table>
    </FORM>
    """ % (
        course_number,
        title,
        room,
        course_number
    )




def updateCourse(conn, course_number, title, room):
    cursor = conn.cursor()
    sql = "UPDATE course SET title=%s, room=%s WHERE number=%s"
    params = (title, room, course_number)
    cursor.execute(sql, params)
    conn.commit()
    if cursor.rowcount > 0:
        return "Update Course Succeeded. <form action='/' method='GET'><input type='submit' value='Back to Course List'></form>"
    else:
        return "Update Course Failed."
















def showAllEnrollments(conn):
    cursor = conn.cursor()
    sql = """
    SELECT student.id, student.name, enrolled.course
    FROM student
    INNER JOIN enrolled ON student.id = enrolled.student
    ORDER BY student.id ASC
    """
    cursor.execute(sql)
    body = """
    <h2>Enrollment List</h2>
    <table class ="student-table" border=1>
      <tr>
        <td><font size=+1'><b>Student ID</b></font></td>
        <td><font size=+1'><b>Name</b></font></td>
        <td><font size=+1'><b>Course</b></font></td>
        <td><font size=+1'><b>Delete</b></font></td>
      </tr>
    """
    for row in cursor:
        student_id = row[0]
        student_name = row[1]
        course = row[2]
        body += (
            "<tr>"
            f"<td>{student_id}</td>"
            f"<td>{student_name}</td>"
            f"<td>{course}</td>"
            f"<td><form method='POST'><input type='hidden' name='student_id' value='{student_id}'><input type='hidden' name='course' value='{course}'><input type='submit' name='deleteEnrollment' value='Delete'></form></td>"
            "</tr>\n"
        )
    body += "</table>"
    return body




def showAddEnrollmentForm():
    return """
    <h2>Add Enrollment</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Student ID</td>
            <td><INPUT TYPE="TEXT" NAME="student_id" VALUE=""></td>
        </tr>
        <tr>
            <td>Course</td>
            <td><INPUT TYPE="TEXT" NAME="course" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addEnrollment" value="Add Enrollment">
            </td>
        </tr>
    </table>
    </FORM>
    """


def addEnrollment(conn, student_id, course):
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO enrolled (student, course) VALUES (%s, %s)"
        params = (student_id, course)
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount > 0:
            status_message = "Add Enrollment Succeeded."
        else:
            status_message = "Add Enrollment Failed."
    except psycopg2.Error as e:
        conn.rollback()
        status_message = f"Failed to add enrollment: {e}"
    body = f"<h2>{status_message}</h2>"
    body += '<form action="/" method="GET">'
    body += '<input type="submit" value="Go back to Enrollment List">'
    body += '</form>'
    return body




def deleteEnrollment(conn, student_id, course):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM enrolled WHERE student = %s AND course = %s", (student_id, course))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Enrollment Succeeded."
    else:
        return "Delete Enrollment Failed."








































   














def application(env, start_response):
    qs, post = get_qs_post(env)


    body = ""
    try:
        conn = psycopg2.connect(
            host="postgres",
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
    except psycopg2.Warning as e:
        print(f"Database warning: {e}")
        body += "Check logs for DB warning"
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        body += "Check logs for DB error"
    if "student_id" in post and "deleteStudent" in post:
        student_id = post["student_id"][0]
        deleteStudent(conn, student_id)
        start_response("302 Found", [("Location", "/")])
        return []
    if "room_number" in post and "deleteRoom" in post:
        room_number = post["room_number"][0]
        deleteRoom(conn, room_number)
        start_response("302 Found", [("Location", "/")])
        return []
    if "course_number" in post and "deleteCourse" in post:
        course_number = post["course_number"][0]
        deleteCourse(conn, course_number)
        start_response("302 Found", [("Location", "/")])
        return []
    if "student_id" in post and "deleteEnrollment" in post:
        student_id = post["student_id"][0]
        course = post["course"][0]
        deleteEnrollment(conn, student_id, course)
        start_response("302 Found", [("Location", "/")])
        return []




   
    if "student_id" in post and "viewStudentInfo" in post:
        student_id = post["student_id"][0]
        body += showStudentInfo(conn, student_id)
    elif "course_name" in post and "viewCourseDetails" in post:
        course_name = post["course_name"][0]
        body += showCourseDetails(conn, course_name)
    elif "dept_name" in post and "viewDepartment" in post:
        dept_name = post["dept_name"][0]
        body += showDepartment(conn, dept_name)
    elif "student_id" in post and "student_name" in post:
        student_id = post["student_id"][0]
        student_name = post["student_name"][0]
        if "addStudent" in post:
            body += addStudent(conn, student_id, student_name)


    elif "room_number" in post and "capacity" in post:
        room_number = post["room_number"][0]
        capacity = post["capacity"][0]
        if "addRoom" in post:
            body += addRoom(conn, room_number, capacity)
        elif "completeUpdateRoom" in post:
            body += updateRoom(conn, room_number, capacity)
   


    elif "course_number" in post and "title" in post and "room" in post:
        course_number = post["course_number"][0]
        title = post["title"][0]
        room = post["room"][0]
        if "addCourse" in post:
            body += addCourse(conn, course_number, title, room)
        elif "completeUpdateCourse" in post:
            body += updateCourse(conn, course_number, title, room)




    elif "student_id" in post and "course" in post:
        student_id = post["student_id"][0]
        course = post["course"][0]
        if "addEnrollment" in post:
            body += addEnrollment(conn, student_id, course)




    else:
        if "showUpdateRoomForm" in qs:
            room_number = qs.get("room_number")[0]
            body += getUpdateRoomForm(conn, room_number)
        elif "showUpdateCourseForm" in qs:  
            course_number = qs.get("course_number")[0]  
            body += getUpdateCourseForm(conn, course_number)  
        else:
            body += showAllStudents(conn)
            body += showAddStudentForm()
            # body += showAllRooms(conn)
            # body += showAddRoomForm()
            # body += showAllCourses(conn)
            # body += showAddCourseForm()
            body += showAllEnrollments(conn)
            body += showAddEnrollmentForm()
            body += showAllCourses(conn)
            body += showAddCourseForm()
            body += showAllRooms(conn)
            body += showAddRoomForm()

    start_response("200 OK", [("Content-Type", "text/html")])
    return [wrapBody(body, title="Student Enrollment Directory").encode("utf-8")]