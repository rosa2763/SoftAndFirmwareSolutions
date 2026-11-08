from flask import Blueprint,flash, get_flashed_messages, redirect, url_for,render_template,request,session
from .models import User,TTData
from . import db
import pandas as pd
from pathlib import Path
from sqlalchemy import select,delete

# Define Blueprint -----------------------------------------------Blueprint-----------
tt_display = Blueprint('tt_display',__name__)

# First Sheet...........................................................................
DEPARTMENTS = ["Civil Engineering","Electrical Engineering","Mechanical Engineering"]
SEMESTERS = ["s1","s2","s3","s4","s5","s6","s7","s8"]
data_holder={}
weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
slots = ["FN-Slot1","FN-Slot2","FN-Slot3","FN-Slot4","AN-Slot5", "AN-Slot6","AN-SlotX"]

def view_tt():
    department = data_holder.get("department")
    semester = data_holder.get("semester")
    tt_rows = 6
    tt_cols = 8
    tt_table = [["" for _ in range(tt_cols)] for _ in range(tt_rows)]
    ltpr_display=[["" for _ in range(tt_cols)] for _ in range(tt_rows)]
    tt_dataStore_lec = []
    tt_dataStore_tut = []
    tt_dataStore_lab = []
    print(department,semester)
    
    if department and semester:
        users = (
            TTData.query
            .filter_by(dept_a=department, semester=semester, )
            .order_by(TTData.id)
            .all()
        )
    #return department or "", semester or "",tt_table,ltpr_display
        """
        for user in users:
            print(user.weekday,user.slot)
            if user.weekday not in weekdays or user.slot not in slots:
                continue
            else:
            """
        for user in users:
            if user.ltpr=="Lecture":
                temp_store_lec={"ltpr":user.ltpr,"subject":user.subject,"faculty":user.emp_code,"weekday":user.weekday,"slot":user.slot}
                tt_dataStore_lec.append(temp_store_lec)
                #Fill Lecture
                ltpr_display[weekdays.index(user.weekday)+1][slots.index(user.slot)+1]="lecture"
                tt_table[weekdays.index(user.weekday)+1][slots.index(user.slot)+1]=f"{user.ltpr}, {user.subject}, {user.emp_code}"
            elif user.ltpr=="Tutorial":
                temp_store_tut={"ltpr":user.ltpr,"subject":user.subject,"faculty":user.emp_code,"weekday":user.weekday,"slot":user.slot}
                tt_dataStore_tut.append(temp_store_tut)           
            elif user.ltpr=="Practical":
                temp_store_lab={"ltpr":user.ltpr,"subject":user.subject,"faculty":user.emp_code,"weekday":user.weekday,"slot":user.slot}
                tt_dataStore_lab.append(temp_store_lab)
        #Fill Tutorial
        tut_sub_list=[]
        for temp_store_tut in tt_dataStore_tut:
            tut_sub_list.append(temp_store_tut["subject"])
        tut_sub_list=list(set(tut_sub_list))
        tut_name=[]
        tut_day=[]
        tut_slot=[]
        for i in range(len(tut_sub_list)):
            tut_name_sel="_"
            for temp_store_tut in tt_dataStore_tut:
                if tut_sub_list[i]==temp_store_tut["subject"]:
                    tut_day_sel=f"{temp_store_tut['weekday']}"
                    tut_slot_sel=f"{temp_store_tut['slot']}"
                    if tut_name_sel=="_":
                        tut_name_sel=f"{temp_store_tut['faculty']}"
                    else:
                        tut_name_sel=f"{temp_store_tut['faculty']}, {tut_name_sel}"
            tut_name.append(tut_name_sel)
            tut_day.append(tut_day_sel)
            tut_slot.append(tut_slot_sel)
        for i in range(len(tut_name)):
            ltpr_display[weekdays.index(tut_day[i])+1][slots.index(tut_slot[i])+1]="tutorial"
            tt_table[weekdays.index(tut_day[i])+1][slots.index(tut_slot[i])+1]=f"Tutorial, {tut_sub_list[i]}, {tut_name[i]}"
        #Fill Practical
        lab_sub_list=[]
        for temp_store_lab in tt_dataStore_lab:
            lab_sub_list.append(temp_store_lab["subject"])
        lab_sub_list=list(set(lab_sub_list))
        lab_name=[]
        lab_day=[]
        lab_slot=[]
        for i in range(len(lab_sub_list)):
            lab_name_sel="_"
            for temp_store_lab in tt_dataStore_lab:
                if lab_sub_list[i]==temp_store_lab["subject"]:
                    lab_day_sel=f"{temp_store_lab['weekday']}"
                    lab_slot_sel=f"{temp_store_lab['slot']}"
                    if lab_name_sel=="_":
                        lab_name_sel=f"{temp_store_lab['faculty']}"
                    else:
                        lab_name_sel=f"{temp_store_lab['faculty']},{lab_name_sel}"
            lab_name.append(lab_name_sel)
            lab_day.append(lab_day_sel)
            lab_slot.append(lab_slot_sel)
        #Remove double values in names and slots for the practical
        for i in range(len(lab_name)):
            lab_name[i]=list(set(lab_name[i].split(",")))     
        slot_index = []
        for slot_value in lab_slot:
            if slot_value == 'slot3' or slot_value == 'slot4':
                slot_index.append(3)
            else:
                slot_index.append(5)
        for i in range(len(lab_name)):
            ltpr_display[weekdays.index(lab_day[i])+1][slot_index[i]]="practical"
            tt_table[weekdays.index(lab_day[i])+1][slot_index[i]]=f"Practical, {lab_sub_list[i]}, {lab_name[i]}"
            """
                tt_table[weekdays.index(entry.weekday)][slots.index(entry.slot)].append({
                    "ltpr": entry.ltpr or "",
                    "subject": entry.subject or "",
                    "faculty": entry.emp_code or "",
                })
            elif entry.ltpr == "Tutorial":
            """
    print(tt_table)
    print
    print(ltpr_display)
    return department or "", semester or "",tt_table,ltpr_display
# -----------------------------------------------------------------------------------------
lock_dept = False
lock_semester = True
lock_continue = True
# Data for tt_Flask routes class -----------------------------------------------------------
@tt_display.route("/tt_dispData",methods=["GET", "POST"])
def tt_dispData():
    global lock_dept,lock_semester,data_holder
    global lock_ltpr, lock_subject, lock_continue,emp_codes,subjects
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    username = session["username"]
    if request.method == "POST":
        flash("SELECT the Department and then the Semester", "info")
        if request.form.get("dept_but") == "department":
            selected_dept = request.form.get("department")
            if selected_dept in DEPARTMENTS:
                data_holder["department"] = selected_dept
                lock_dept = True
                lock_semester = False
                lock_continue = True
            else:
                flash("Select a valid department code from the list", "warning")
        elif request.form.get("dept_but") == "cancel":
            data_holder.pop("department", None)
            lock_dept = False
            lock_semester = True
            lock_continue = True
            flash("Department selected cancelled", "danger")
        elif request.form.get("semester_but") == "cancel":
            data_holder.pop("semester", None)
            lock_dept = True
            lock_semester = False
            lock_continue = True
            flash("Semester selected cancelled", "danger")
        elif request.form.get("semester_but") == "semester":
            selected_semester = request.form.get("semester")
            if selected_semester in SEMESTERS:
                data_holder["semester"] = selected_semester
                lock_dept = True
                lock_semester = True
                lock_continue = False
            else:
                flash("Select a valid semester code from the list", "warning")
        if request.form.get("end_but") == "cancel":
            data_holder.pop("department", None)
            data_holder.pop("semester", None)
            lock_dept = False
            lock_semester = True
            lock_continue = True                      
            return redirect(url_for("tt_display.tt_dispData"))
        elif request.form.get("end_but") == "view_tt":
            return redirect(url_for("tt_display.tt_dispView"))
    return render_template("tt_dispData.html", 
        lock_dept = lock_dept,
        departments = DEPARTMENTS,
        selected_dept = data_holder.get("department"),
        lock_semester = lock_semester,
        semesters = SEMESTERS,
        selected_semester = data_holder.get("semester"),
        lock_continue = lock_continue,
        username = username)

# HTML Routes....................................................................time_table..........
@tt_display.route("/tt_dispView", methods=["GET","POST"])
def tt_dispView():
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    username = session["username"]
    department, semester,tt_table,ltpr_display = view_tt()
    department = department
    semester = semester
    return render_template("tt_dispView.html",
        dept_sem=department,
        semester=semester,
        slots_rowCol=tt_table,
        ltpr=ltpr_display,
        username=username)

