from flask import Blueprint,flash, get_flashed_messages, redirect, url_for,render_template,request,session
from .models import User,TTData
from . import db
import pandas as pd
from pathlib import Path
from sqlalchemy import select,delete

# Define Blueprint -----------------------------------------------Blueprint-----------
tt_DELETEdata = Blueprint('tt_DELETEdata',__name__)

# First Sheet...........................................................................
DEPARTMENTS = ["Civil Engineering","Electrical Engineering","Mechanical Engineering"]
SEMESTERS = ["s1","s2","s3","s4","s5","s6","s7","s8"]
data_holder={}
weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
slots = ["FN-Slot1","FN-Slot2","FN-Slot3","FN-Slot4","AN-Slot5", "AN-Slot6","AN-SlotX"]
OPTIONS = ["byFaculty","byWeekday_Slot","byLTPR","bySubject","All"]
"""
class FromOption:
    def __init__(self, department,semester):
        self.department = department
        self.semester = semester
    def get_entries(self):
        if self.department and self.semester:
            self.entries = (
                TTData.query
                .filter_by(dept_a=self.department,semester=self.semester, )
                .order_by(TTData.id)
                .all()
            )
    print("end of parent class")
class FacultyList(FromOption):
    def __init__(self,department,semester,option_read):
        super().__init__(department,semester)
        self.option_read = option_read
    def child_method(self):
        if data_holder.get("option") == self.option_read:
            self.faculty_list = []
            for entry in self.entries:
                if entry.emp_code:
                    self.faculty_list.append(entry.emp_code)     
            if not self.faculty_list:
                flash("!!! No ENTRY is assigned for faculty/faculties", "danger")
            return list(set(self.faculty_list))
        print(f"Hello, my name is {self.first_name} {self.last_name}.")
"""
def view_tt():
    pass
def get_faculty_list(department,semester):
    if department and semester and data_holder.get("option")=="byFaculty":
        entries = (
            TTData.query
            .filter_by(dept_a=department, semester=semester)
            .order_by(TTData.id)
            .all()
        )
        faculty_list = []
        for entry in entries:
            if entry.emp_code:
                faculty_list.append(entry.emp_code)
        if not faculty_list:
            flash("!!! No ENTRY is assigned for faculty/faculties", "danger")
        return list(dict.fromkeys(faculty_list))
    return []

def get_weekday_list(department,semester):
    if department and semester and data_holder.get("option")=="byWeekday_Slot":
        entries = (
            TTData.query
            .filter_by(dept_a=department, semester=semester)
            .order_by(TTData.id)
            .all()
        )
        weekday_list = []
        for entry in entries:
            if entry.weekday:
                weekday_list.append(entry.weekday)
        if not weekday_list:
            flash("!!! No ENTRY is assigned for weekdays", "danger")
        return list(dict.fromkeys(weekday_list))
    return []

def get_slot_list(department,semester):
    if department and semester and data_holder.get("weekday") in weekdays:
        entries = (
            TTData.query
            .filter_by(dept_a=department, semester=semester, weekday=data_holder.get("weekday"))
            .order_by(TTData.id)
            .all()
        )
        slot_list = []
        for entry in entries:
            if entry.slot:
                slot_list.append(entry.slot)
        if not slot_list:
            flash("!!! No ENTRY is assigned for weekdays", "danger")
        return list(dict.fromkeys(slot_list))
    return []
def get_ltpr_list(department,semester):
    if department and semester and data_holder.get("option") == "byLTPR":
        entries = (
            TTData.query
            .filter_by(dept_a=department, semester=semester, ltpr=data_holder.get("ltpr"))
            .order_by(TTData.id)
            .all()
        )
        ltpr_list = []
        for entry in entries:
            if entry.ltpr:
                ltpr_list.append(entry.slot)
        if not ltpr_list:
            flash("!!! No ENTRY is assigned for weekdays", "danger")
        return list(dict.fromkeys(ltpr_list))
    return []

def get_item_option():
    if request.form.get("option") == "by Faculty":
        stmt = select(TTData.subject).where(TTData.emp_code != data_holder.get("emp_code"),
            TTData.ltpr == data_holder.get("ltpr"),TTData.dept_a == data_holder.get("dept_a"),
            TTData.semester == data_holder.get("semester"))
        results = db.session.execute(stmt).all()

# -----------------------------------------------------------------------------------------
lock_dept = False
lock_semester = True
lock_option = True
lock_continue = True
lock_byFaculty = True
lock_byFacultyHide = True
lock_byWeekday = True
lock_byWeekdayHide = True
lock_bySlot = True
lock_bySlotHide = True
lock_byLtpr = True
lock_byLtprHide = True
# Data for tt_Flask routes class -----------------------------------------------------------
@tt_DELETEdata.route("/tt_deleteData",methods=["GET", "POST"])
def tt_deleteData():
    global data_holder,lock_dept,lock_semester,lock_option,lock_byFaculty,lock_byFacultyHide
    global lock_continue,lock_byWeekday,lock_byWeekdayHide,lock_bySlot,lock_bySlotHide
    global lock_byLtpr, lock_byLtprHide
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    username = session["username"]
    if request.method == "POST":
        flash("SELECT the Department and then the Semester", "info")
        if request.form.get("dept_but") == "dept":
            selected_dept = request.form.get("dept")
            if selected_dept in DEPARTMENTS:
                data_holder["dept"] = selected_dept
                lock_dept = True
                lock_semester = False
            else:
                flash("Select a valid department code from the list", "warning")
        elif request.form.get("dept_but") == "cancel":
            data_holder.pop("dept", None)
            data_holder.pop("semester", None)
            data_holder.pop("option", None)
            data_holder.pop("faculty", None)
            data_holder.pop("weekday", None)
            lock_dept = False
            lock_semester = True
            lock_option = True
            lock_byFacultyHide = True
            lock_byWeekdayHide = True
            lock_bySlotHide = True         
            flash("Department selected cancelled", "danger")

        elif request.form.get("semester_but") == "semester":
            selected_semester = request.form.get("semester")
            if selected_semester in SEMESTERS:
                data_holder["semester"] = selected_semester
                lock_dept = True
                lock_semester = True
                lock_option = False
                lock_byFacultyHide = True
                lock_byWeekdayHide = True
                lock_bySlotHide = True 
            else:
                flash("Select a valid semester code from the list", "warning")
        elif request.form.get("semester_but") == "cancel":
            data_holder.pop("semester", None)
            data_holder.pop("option", None)
            data_holder.pop("faculty", None)
            data_holder.pop("weekday", None)
            lock_dept = True
            lock_semester = False
            lock_option = True
            lock_byFacultyHide = True
            lock_byWeekdayHide = True
            lock_bySlotHide = True 
            flash("Semester selected cancelled", "danger")
        elif request.form.get("option_but") == "option":
            selected_option = request.form.get("option")
            if selected_option in OPTIONS:
                data_holder["option"] = selected_option
                lock_dept = True
                lock_semester = True
                lock_option = True
                data_holder.pop("faculty", None)
                data_holder.pop("weekday", None)
                lock_continue = True
                if selected_option == "byFaculty":
                    lock_byFaculty = False
                    lock_byFacultyHide = False
                    lock_byWeekday = True
                    lock_byWeekdayHide = True
                    lock_byLtpr = True
                    lock_byLtprHide = True   
                elif selected_option == "byWeekday_Slot":
                    lock_byFaculty = True
                    lock_byFacultyHide = True
                    lock_byWeekday = False
                    lock_byWeekdayHide = False 
                    lock_byLtpr = True
                    lock_byLtprHide = True   
                elif selected_option == "byLTPR":
                    lock_byFaculty = True
                    lock_byFacultyHide = True
                    lock_byWeekday = True
                    lock_byWeekdayHide = True 
                    lock_byLtpr = False
                    lock_byLtprHide = False                               
                else:
                    lock_byFaculty = True
                    lock_byFacultyHide = True               
                    lock_byWeekday = True
                    lock_byWeekdayHide = True
                    lock_byLtpr = True
                    lock_byLtprHide = True       
            else:
                flash("Select a valid option from the list", "warning")
        elif request.form.get("option_but") == "cancel":
            data_holder.pop("option", None)
            data_holder.pop("faculty", None)
            data_holder.pop("weekday", None)
            lock_dept = True
            lock_semester = True
            lock_option = False
            lock_byFaculty = True
            lock_byFacultyHide = True               
            lock_byWeekday = True
            lock_byWeekdayHide = True  
            flash("Selected option cancelled", "danger")     

        elif request.form.get("faculty_but") == "faculty":
            selected_faculty = request.form.get("faculty")
            data_holder["faculty"] = selected_faculty
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = False
            lock_continue = False
        elif request.form.get("faculty_but") == "cancel":
            data_holder.pop("faculty", None)
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            flash("Faculty option cancelled", "danger")

        elif request.form.get("weekday_but") == "weekday":
            selected_weekday = request.form.get("weekday")
            data_holder["weekday"] = selected_weekday
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = False
            lock_bySlot = False
            lock_bySlotHide =False
            #lock_continue = False
        elif request.form.get("weekday_but") == "cancel":
            data_holder.pop("weekday", None)
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = False
            lock_bySlot = True
            lock_bySlotHide = True
            #lock_continue = True
            flash("Weekday option cancelled", "danger")

        elif request.form.get("slot_but") == "slot":
            selected_slot = request.form.get("slot")
            data_holder["slot"] = selected_slot
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = True
            lock_bySlot = True
            lock_bySlotHide = True
            lock_byLtpr = False
            lock_byLtprHide =False
            #lock_continue = False
        elif request.form.get("slot_but") == "cancel":
            data_holder.pop("slot", None)
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = False
            lock_bySlot = True
            lock_bySlotHide = False    
            lock_byLtpr = True
            lock_byLtprHide =True
            #lock_continue = True
            flash("Slot option cancelled", "danger")

        elif request.form.get("ltpr_but") == "ltpr":
            selected_ltpr = request.form.get("ltpr")
            data_holder["ltpr"] = selected_ltpr
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = True
            lock_bySlot = True
            lock_bySlotHide = True
            lock_byLtpr = True
            lock_byLtprHide =False
            lock_continue = False
        elif request.form.get("ltpr_but") == "cancel":
            data_holder.pop("ltpr", None)
            lock_dept = True
            lock_semester = True
            lock_option = True
            lock_byFaculty = True
            lock_byFacultyHide = True
            lock_byWeekday = True
            lock_byWeekdayHide = True
            lock_bySlot = True
            lock_bySlotHide = False         
            lock_continue = True
            flash("Slot option cancelled", "danger")
   
        if request.form.get("end_but") == "cancel":
            data_holder={}
            lock_dept = False
            return redirect(url_for("main.dashboard"))
        elif request.form.get("end_but") == "view_tt":
            return redirect(url_for("tt_display.tt_dispView"))
  
    faculty_list = get_faculty_list(data_holder.get("dept"),data_holder.get("semester"))
    weekday_list = get_weekday_list(data_holder.get("dept"),data_holder.get("semester"))
    slot_list = get_slot_list(data_holder.get("dept"),data_holder.get("semester"))
    ltpr_list = get_ltpr_list(data_holder.get("dept"),data_holder.get("semester"))
    return render_template("tt_deleteData.html", 
        lock_dept = lock_dept, depts = DEPARTMENTS,selected_dept = data_holder.get("dept"),
        lock_semester = lock_semester, semesters = SEMESTERS,selected_semester = data_holder.get("semester"),
        lock_option = lock_option, options = OPTIONS,selected_option = data_holder.get("option"),
        lock_byFaculty = lock_byFaculty, lock_byFacultyHide=lock_byFacultyHide,
        faculties = faculty_list, selected_faculty=data_holder.get("faculty"),
        lock_byWeekday = lock_byWeekday, lock_byWeekdayHide=lock_byWeekdayHide,
        weekdays = weekday_list, selected_weekday=data_holder.get("weekday"),
        lock_bySlot = lock_bySlot,lock_bySlotHide = lock_bySlotHide,
        slots = slot_list, selected_slot=data_holder.get("slot"),
        lock_byLtpr = lock_byLtpr,lock_byLtprHide = lock_byLtprHide,
        ltprs = ltpr_list, selected_ltpr=data_holder.get("ltpr"),      

        lock_continue = lock_continue,
        username = username)

# HTML Routes....................................................................time_table..........
@tt_DELETEdata.route("/tt_deletedView", methods=["GET","POST"])
def tt_deletedView():
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    username = session["username"]
    department, semester,tt_table,ltpr_display = view_tt()
    department = department
    semester = semester
    return render_template("tt_deletedView.html",
        dept_sem=department,
        semester=semester,
        slots_rowCol=tt_table,
        ltpr=ltpr_display,
        username=username)
