from flask import Blueprint,flash, get_flashed_messages, redirect, url_for,render_template,request,session
from .models import User,TTData
from . import db
import pandas as pd
from pathlib import Path
from sqlalchemy import select,delete
"""
<<Reference Materials for db usage>>
---
# Get conditional id and email
stmt = select(User.id,User.email).where(User.id > 5)
result = db.session.execute(stmt).all
---
# Select with Filter
1. email = User.querry.with_entries(User.email).filter_by(id=1).first()
2. data = User.querry.with_entries(User.id,User.email).filter(User.email.like(%gmail%)).all()
---
# Get as dictinary
users = User.querry.with_entries(User.id,User.email).all()
data = [{"id":u.id,"email":u.email} for u in users]
"""
# Define Blueprint -----------------------------------------------Blueprint-----------
tt_entry = Blueprint('tt_entry',__name__)

# Data for tt_parent_dept --------------------------------------------------------------
# First Sheet...........................................................................
DEPARTMENTS=["Civil Engineering","Electrical Engineering","Mechanical Engineering"]
lock_dropdown = [False,True,True,True,True,True,True,True,True,True]
sel_one = [None,'','','','','','']
data_holder={}

# Data for tt_assigned class -----------------------------------------------------------
# Second Sheet..........................................................................
global df_dept
facutly_filemap = {"Civil Engineering":"CE",
        "Mechanical Engineering":"ME",
         "Electrical Engineering":"EE"
        }

ODDEVEN=["Odd","Even"]

# Third Sheet.........from semester; select Practical or L/T/P/R .........................
def ltpr_pulldown(cur_sheet_):
    global data_holder, ltpr_list, semester_list,tt_users
    ltpr_list = []
    dept_ = data_holder.get("dept_a")                                           #or data_holder.get("parent_dept")
    if not dept_:
        return ltpr_list

    semester_list = semester_numbers(data_holder.get("odd_even", "Odd"))
    if cur_sheet_ not in semester_list:
        return ltpr_list

    script_dir = Path(__file__).parent
    file_path_cur = script_dir / "static" / f"curiculam_{facutly_filemap.get(dept_, 'CE')}.xlsx"
    if not file_path_cur.exists():
        return ltpr_list

    df_curiculam = pd.read_excel(file_path_cur, sheet_name=cur_sheet_, engine="openpyxl")
    df_curi_active = df_curiculam[df_curiculam["Select"] != 0]
    df_curi_lab = df_curi_active[df_curi_active["P"] != 0]

    users = TTData.query.filter_by(dept_a = data_holder.get("dept_a"), semester = cur_sheet_,
                ltpr="Practical").all()
    selected_lab_list = [row.subject for row in users if row.subject]
    if len(df_curi_lab.Code.tolist()) > len(set(selected_lab_list)):
        ltpr_list = ["Practical"]
    else:
        ltpr_list = ["Lecture", "Tutorial", "Practical", "Projects"]
    return ltpr_list

# Third Sheet.........from ltpr; select L/T/P/R and get SUBJECT list ...................................
code_list=[]
modified_list=[]
def subject_pulldown(ltpr_):
    global code_list, count_list, modified_list,ltpr_list,data_holder
    dept_ = data_holder.get("dept_a")                                        #or data_holder.get("parent_dept")
    semester = data_holder.get("semester")
    if not dept_ or not semester:
        return []

    script_dir = Path(__file__).parent
    file_path_cur = script_dir / "static" / f"curiculam_{facutly_filemap.get(dept_, 'CE')}.xlsx"
    if not file_path_cur.exists():
        return []

    df_curiculam = pd.read_excel(file_path_cur, sheet_name=semester, engine="openpyxl")
    df_curi_active = df_curiculam[df_curiculam["Select"] != 0]

# Case of Practical
    if ltpr_ == "Practical":
        df_curi_ = df_curi_active[df_curi_active["P"] != 0]
        code_list = df_curi_.Code.tolist()
        count_list_student = df_curi_.Number.tolist()
        count_list=[]
        for i in range(len(count_list_student)):
            if count_list_student[i] <= 20:
                count_list.append(1)
            elif count_list_student[i] <= 40:
                count_list.append(2)
            elif count_list_student[i] <= 50:
                count_list.append(3)                 
            else:
                count_list.append(4)
        users = TTData.query.filter_by(dept_a = data_holder.get("dept_a"),semester=data_holder.get("semester"),
                    ltpr=data_holder.get("ltpr")).all()
        db_code_ = [row.subject for row in users if row.subject]
        db_code_setlist = list(set(db_code_))
        if len(db_code_)==0:
            modified_list = code_list
        else:
            code_full = [] 
            for i in range(len(db_code_setlist)):
                code = code_list[code_list.index(db_code_setlist[i])]
                count = count_list[code_list.index(db_code_setlist[i])]
                code_count = 0    
                for j in range(len(db_code_)):
                    if code == db_code_[j]:
                        code_count = code_count + 1   
                if count <= code_count:
                    code_full.append(code)
                new_code_list = list(set(code_list) - set(code_full))   
            stmt = select(TTData.emp_code,TTData.subject).where(TTData.emp_code==data_holder.get("emp_code"),                                            
                    TTData.ltpr==data_holder.get("ltpr"),TTData.dept_a==data_holder.get("dept_a"),
                    TTData.semester==data_holder.get("semester"))  
            result = db.session.execute(stmt).first()     
            if result == None:
                modified_list = new_code_list
            else:
                for subject in result:
                    modified_list = list(set(new_code_list)-set([subject]))

# Case of Tutorial
    elif ltpr_ == "Tutorial":
        df_curi_ = df_curi_active[df_curi_active["T"] != 0]
        code_list = df_curi_.Code.tolist()
        count_list_student = df_curi_.Number.tolist()
        count_list=[]
        for i in range(len(count_list_student)):
            if count_list_student[i] <= 30:
                count_list.append(1)
            elif count_list_student[i] <= 50:
                count_list.append(2)
            else:
                count_list.append(3)
        users = TTData.query.filter_by(dept_a = data_holder.get("dept_a"),semester=data_holder.get("semester"),
                    ltpr=data_holder.get("ltpr")).all()
        db_code_ = [row.subject for row in users if row.subject]
        db_code_setlist = list(set(db_code_))
        if len(db_code_)==0:
            modified_list = code_list                                                 
        else:
            code_full = []                                                         # All codes selected
            for i in range(len(db_code_setlist)):
                code = code_list[code_list.index(db_code_setlist[i])]
                count = count_list[code_list.index(db_code_setlist[i])]
                code_count = 0     
                for j in range(len(db_code_)):
                    if code == db_code_[j]:
                        code_count = code_count + 1   
                if count <= code_count:
                    code_full.append(code)
                new_code_list = list(set(code_list) - set(code_full))
            print(new_code_list,code_full)

            stmt = select(TTData.emp_code,TTData.subject).where(TTData.emp_code==data_holder.get("emp_code"),                                            
                    TTData.ltpr==data_holder.get("ltpr"),TTData.dept_a==data_holder.get("dept_a"),
                    TTData.semester==data_holder.get("semester"))  
            result = db.session.execute(stmt).first()
            if result == None:
                modified_list = new_code_list
            else:
                for subject in result:
                    modified_list = list(set(new_code_list)-set([subject]))
# Case of Lecture
    elif ltpr_ == "Lecture":
        df_curi_ = df_curi_active[df_curi_active["L"] != 0]
        code_list = df_curi_.Code.tolist()
        count_list = df_curi_.L.tolist()
        users = TTData.query.filter_by(dept_a = data_holder.get("dept_a"),semester=data_holder.get("semester"),
                    ltpr=data_holder.get("ltpr")).all()
        db_code_ = [row.subject for row in users if row.subject]
        db_code_setlist = list(set(db_code_))
        if len(db_code_)==0:
            modified_list = code_list                                                  
        else:
            code_full = []
            for i in range(len(db_code_setlist)):
                code = code_list[code_list.index(db_code_setlist[i])]
                count = count_list[code_list.index(db_code_setlist[i])]
                code_count = 0     
                for j in range(len(db_code_)):
                    if code == db_code_[j]:
                        code_count = code_count + 1   
                if count <= code_count:
                    code_full.append(code)
                new_code_list = list(set(code_list) - set(code_full))        
            stmt = select(TTData.subject).where(TTData.emp_code != data_holder.get("emp_code"),
                    TTData.ltpr == data_holder.get("ltpr"),TTData.dept_a == data_holder.get("dept_a"),
                    TTData.semester == data_holder.get("semester"))
            results = db.session.execute(stmt).all()
            if results == None:
                modified_list = new_code_list
            else:
                code_list_notme = [r[0] for r in results]
                code_set_notme = list(set(code_list_notme))
                print(code_list_notme,code_set_notme,code_full,"Final step")
                for i in range(len(code_set_notme)):
                    if code_set_notme[i] not in code_full:
                        new_code_list = list(set(new_code_list) - set([code_set_notme[i]]))
                modified_list = new_code_list
    elif ltpr_ == "Projects":
        #stmt = delete(TTData).where(TTData.id==17)
        #db.session.execute(stmt)
        #db.session.commit()
        df_curi_ = df_curi_active[df_curi_active["R"] != 0]
        code_list = df_curi_.Code.tolist()
        modified_list = [code for code in code_list]
    else:
        modified_list = []
    return modified_list

# Data for tt_week_slot class -----------------------------------------------------------
# Fourth Sheet................Weekday and Slot..........................................
global day_lock,slot_lock,weekdays,slots
day_lock = [True,True,True,True,True]
slot_lock = [True,True,True,True,True,True,True]
weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
slots = ["FN-Slot1","FN-Slot2","FN-Slot3","FN-Slot4","AN-Slot5", "AN-Slot6","AN-SlotX"]
# Fourth Sheet................Radio Button ON/OFF..........................................
def weekday_radioButtons():
    global day_lock_ref,day_lock,slot_matrix,lock_weekday,lock_slot,slot_lock
    global lock_day_,lock_slot_
    day_lock = [False,False,False,False,False]
    slot_matrix = {}
    for i in range(len(weekdays)):
        stmt = select(TTData.slot).where(TTData.weekday == weekdays[i],
            TTData.dept_a == data_holder["dept_a"],TTData.semester == data_holder["semester"])
        slot_row_sub = db.session.execute(stmt).all()
        # get faculty engagement
        stmt = select(TTData.slot).where(TTData.weekday == weekdays[i],
            TTData.emp_code == data_holder["emp_code"])
        slot_row_faculty = db.session.execute(stmt).all()
        total_slot_inday = [rs[0] for rs in slot_row_sub] + [rf[0] for rf in slot_row_faculty]
        if len(list(set(total_slot_inday))) >= 6:
            day_lock[i]=True
        daily_slot = list(set(total_slot_inday))                                     
        slot_matrix.update({weekdays[i]:daily_slot})
    print(slot_matrix)
    if request.form.get("day") in weekdays:
        for i in range(len(weekdays)):
            if i != weekdays.index(request.form.get("day")):
                day_lock[i] = True
    return day_lock
def slot_radioButtons():
    global slot_lock,slot_list,lock_save,slot_matrix,day_lock,lock_slot
    global data_holder,lock_day_,lock_slot_
    print(data_holder.get("weekday"))
    if data_holder.get("weekday") not in weekdays:
        print(data_holder.get("weekday"), "Data inside slot Radio Button")
        slot_lock = [False, False, False, False, False, False, False]
        if data_holder.get("ltpr") == "Practical":
            slot_lock = [True, True, False, True, False, True, True]
            print(request.form.get("day"))
        if request.form.get("day") in weekdays:
            slot_list = slot_matrix.get(request.form.get("day"))
            for i in range(len(slot_list)):
                slot_lock[slots.index(slot_list[i])] = True        
        print(slot_lock,"calculated Slot lock")
        return slot_lock
    return
def save_tt(save_but, user_id):
    global lock_new_entry,data_holder
    if save_but == "save":
        new_ttData = TTData(
            emp_code = data_holder["emp_code"],
            dept_p = data_holder.get("parent_dept"),
            dept_a = data_holder.get("dept_a"),
            odd_even = data_holder.get("odd_even"),
            semester = data_holder.get("semester"),
            ltpr = data_holder.get("ltpr"),
            subject = data_holder.get("subject"),
            weekday = data_holder.get("weekday"),
            slot = data_holder.get("slot"),
            user_id = user_id,
            )
        #db.session.add(new_ttData)
        #db.session.commit() 
        if data_holder.get("ltpr")=="Practical":
            new_ttData = TTData(
            emp_code = data_holder["emp_code"],
            dept_p = data_holder.get("parent_dept"),
            dept_a = data_holder.get("dept_a"),
            odd_even = data_holder.get("odd_even"),
            semester = data_holder.get("semester"),
            ltpr = data_holder.get("ltpr"),
            subject = data_holder.get("subject"),
            weekday = data_holder.get("weekday"),
            slot = slots[slots.index(data_holder.get("slot"))+1],
            user_id = user_id,
            )
            #db.session.add(new_ttData)
            #db.session.commit()         
        lock_new_entry = False
        return True
    return False

def deptp_code_list(update, dept_ref=None):
    global lock_dept, lock_emp, lock_depta, lock_oddeven, lock_semester
    global lock_ltpr, lock_subject, lock_continue, emp_codes
    if update == "parent_dept":
        if dept_ref not in DEPARTMENTS:
            flash("< Select a valid department before continuing >", "success")
            return []
        data_holder.clear()
        data_holder["parent_dept"] = dept_ref
        lock_dept = True
        lock_emp = False
        lock_depta = True
        lock_oddeven = True
        lock_semester = True
        lock_ltpr = True
        lock_subject = True
        lock_continue = True
        emp_codes = dept_emp_code(dept_ref)
        return emp_codes
    elif update == "cancel":
        reset_tt_entry()
        return emp_codes
    else:
        return []

def reset_tt_entry():
    global lock_dept, lock_emp, lock_depta, lock_oddeven, lock_semester, lock_day_, lock_new_entry
    global lock_ltpr, lock_subject, lock_continue, emp_codes, subjects
    data_holder.clear()
    emp_codes = []
    subjects = []
    lock_dept = False
    lock_emp = True
    lock_depta = True
    lock_oddeven = True
    lock_semester = True
    lock_ltpr = True
    lock_subject = True
    lock_continue = True
    lock_day_ = False
    lock_new_entry = True

def dept_emp_code(dept_ref):  # Read faculty data from excel file to df_dept
    global empdept_list,empname_list
    if dept_ref not in facutly_filemap:
        empdept_list = []
        empname_list = []
        return empdept_list
    script_dir = Path(__file__).parent
    file_path = script_dir / "static" / "faculty_data.xlsx"
    df_dept=pd.read_excel(file_path,sheet_name=facutly_filemap[dept_ref],engine="openpyxl")
    empdept_list=[str(element) for element in df_dept["emp_code"].tolist()] #convert list to string
    empname_list=df_dept["nick_name"].tolist()
    return empdept_list

sem_list={"odd":["s1","s3","s5","s7"],
        "even":["s2","s4","s6","s8"]}
def semester_numbers(sem_ref):
    if sem_ref=="Odd":
        semester_list=sem_list["odd"]
    elif sem_ref=="Even":
        semester_list=sem_list["even"]
    else:
        semester_list = []
    return semester_list

def teacher_name(core):    
    global empdept_list,empname_list
    employee_codes = dept_emp_code(data_holder.get("parent_dept"))
    if core not in employee_codes:
        show_name = " "
    else:
        show_name = empname_list[empdept_list.index(core)]
    return show_name

def bypass_slot():
    global data_holder,lock_weekday,day_lock,slot_lock,lock_new_entry,lock_disable_slot
    global lock_save,lock_reset
    if (data_holder.get("ltpr") not in {"Practical", "Tutorial"}
        or not all(data_holder.get(field) for field in ("subject", "dept_a", "semester"))
        ):
        return
    stmt = (
        select(TTData.weekday, TTData.slot,TTData.emp_code)
        .where(
            TTData.subject == data_holder["subject"],
            TTData.ltpr == data_holder["ltpr"],
            TTData.dept_a == data_holder["dept_a"],
            TTData.semester == data_holder["semester"],
            TTData.weekday.in_(weekdays),
            TTData.slot.in_(slots),
        )
        .order_by(TTData.id)
    )
    result = db.session.execute(stmt).first()
    if result is None:
        return
    data_holder["weekday"] = result.weekday
    data_holder["slot"] = result.slot
    day_lock = [True,True,True,True,True]
    slot_lock = [True,True,True,True,True,True,True]
    lock_weekday = True
    lock_new_entry = True
    lock_disable_slot = True
    lock_save = False
    lock_reset = True
    return
# -----------------------------------------------------------------------------------------
# HTML '/tt_view" to display the Time Table
# -----------------------------------------------------------------------------------------
def view_tt():
    department = data_holder.get("dept_a")
    semester = data_holder.get("semester")
    timetable = [[[] for _ in slots] for _ in weekdays]

    if department and semester:
        entries = (
            TTData.query
            .filter_by(dept_a=department, semester=semester)
            .order_by(TTData.id)
            .all()
        )
        for entry in entries:
            if entry.weekday not in weekdays or entry.slot not in slots:
                continue
            timetable[weekdays.index(entry.weekday)][slots.index(entry.slot)].append({
                "ltpr": entry.ltpr or "",
                "subject": entry.subject or "",
                "faculty": entry.emp_code or "",
            })

    return department or "", semester or "", timetable
# -----------------------------------------------------------------------------------------










# HTML Routes....................................................................tt_data...........
lock_dept = False
lock_emp = True
lock_depta = True
lock_oddeven = True
lock_semester = True
lock_ltpr = True
lock_subject = True
lock_continue = True
emp_codes = []
subjects = []
# Data for tt_Flask routes class -----------------------------------------------------------
@tt_entry.route("/tt_data",methods=["GET", "POST"])
def tt_data():
    global lock_dept, lock_emp, lock_depta, lock_oddeven,lock_semester,slot_lock
    global lock_ltpr, lock_subject, lock_continue,emp_codes,subjects
    global lock_day_,lock_slot_,lock_home_reset_save,lock_save,lock_new_entry
    #global lock_weekday
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    username = session["username"]
    if request.method == "POST":
        flash("Identify the choice and SELECT before going for the next", "info")
        if request.form.get("save_but") == "new_entry":
            if not lock_new_entry:
                reset_tt_entry()
                return redirect(url_for("tt_entry.tt_data"))     
        elif "deptp_but" in request.form:
            emp_codes = deptp_code_list(
                request.form.get("deptp_but"),
                request.form.get("dept_p"),
            )
        elif request.form.get("emp_but") == "cancel":
            data_holder.pop("emp_code", None)
            data_holder.pop("dept_a", None)
            data_holder.pop("odd_even", None)
            data_holder.pop("semester", None)
            data_holder.pop("ltpr", None)
            data_holder.pop("subject", None)
            lock_emp = True
            lock_depta = True
            lock_oddeven = True
            lock_semester = True
            lock_ltpr = True
            lock_subject = True
            lock_continue = True
            flash("Department & Employee Code entry cancelled", "danger")
        elif request.form.get("emp_but") == "emp_value":
            selected_code = request.form.get("emp_code")
            if selected_code in emp_codes and data_holder.get("parent_dept"):
                data_holder["emp_code"] = selected_code
                data_holder.pop("dept_a", None)
                data_holder.pop("odd_even", None)
                data_holder.pop("semester", None)
                data_holder.pop("ltpr", None)
                data_holder.pop("subject", None)
                lock_emp = True
                lock_depta = False
                lock_oddeven = True
                lock_semester = True
                lock_ltpr = True
                lock_subject = True
                lock_continue = True
            else:
                flash("Select a valid employee code from the list", "warning")
        elif request.form.get("depta_but") == "cancel":
            data_holder.pop("dept_a", None)
            data_holder.pop("odd_even", None)
            data_holder.pop("semester", None)
            data_holder.pop("ltpr", None)
            data_holder.pop("subject", None)
            lock_depta = False
            lock_oddeven = True
            lock_semester = True
            lock_ltpr = True
            lock_subject = True
            lock_continue = True
            flash("Assigned Programme entry cancelled", "danger")
        elif request.form.get("depta_but") == "depta_value":
            selected_dept = request.form.get("dept_a")
            if selected_dept in DEPARTMENTS and data_holder.get("emp_code"):
                data_holder["dept_a"] = selected_dept
                data_holder.pop("odd_even", None)
                data_holder.pop("semester", None)
                data_holder.pop("ltpr", None)
                data_holder.pop("subject", None)
                lock_depta = True
                lock_oddeven = False
                lock_semester = True
                lock_ltpr = True
                lock_subject = True
                lock_continue = True
            else:
                flash("Select a valid Assigned programme/department", "warning")
        elif request.form.get("oddeven_but") == "cancel":
            data_holder.pop("odd_even", None)
            data_holder.pop("semester", None)
            data_holder.pop("ltpr", None)
            data_holder.pop("subject", None)
            lock_oddeven = False
            lock_semester = True
            lock_ltpr = True
            lock_subject = True
            lock_continue = True
            flash("Semester Odd/Even Semester entry cancelled", "danger")
        elif request.form.get("oddeven_but") == "oddeven_value":
            selected_odd_even = request.form.get("odd_even")
            if selected_odd_even in ODDEVEN and data_holder.get("dept_a"):
                data_holder["odd_even"] = selected_odd_even
                data_holder.pop("semester", None)
                data_holder.pop("ltpr", None)
                data_holder.pop("subject", None)
                lock_oddeven = True
                lock_semester = False
                lock_ltpr = True
                lock_subject = True
                lock_continue = True
            else:
                flash("Select Odd or Even semester from list", "warning")
        elif request.form.get("semester_but") == "cancel":
            data_holder.pop("semester", None)
            data_holder.pop("ltpr", None)
            data_holder.pop("subject", None)
            lock_semester = False
            lock_ltpr = True
            lock_subject = True
            lock_continue = True
            flash("Semester in Odd/Even entry cancelled", "danger")
        elif request.form.get("semester_but") == "semester_value":
            selected_semester = request.form.get("semester")
            if selected_semester in semester_numbers(data_holder.get("odd_even")):
                data_holder["semester"] = selected_semester
                data_holder.pop("ltpr", None)
                data_holder.pop("subject", None)
                lock_semester = True
                lock_ltpr = False
                lock_subject = True
                lock_continue = True
            else:
                flash("Select Semester in Odd or Even", "warning")
        elif request.form.get("ltpr_but") == "cancel":
            data_holder.pop("ltpr", None)
            data_holder.pop("subject", None)
            lock_ltpr = False
            lock_subject = True
            lock_continue = True
            flash("Select Lecture/Tutorial/Practical/Project-Seminar from the list", "danger")
        elif request.form.get("ltpr_but") == "ltpr_value":
            selected_ltpr = request.form.get("ltpr")
            if selected_ltpr in ltpr_pulldown(data_holder.get("semester")):
                data_holder["ltpr"] = selected_ltpr
                data_holder.pop("subject", None)
                lock_ltpr = True
                lock_subject = False
                lock_continue = True
            else:
                flash("Select Lecture/Tutorial/Practical/Project-Seminar", "warning")
        elif request.form.get("subject_but") == "cancel":
            data_holder.pop("subject", None)
            lock_subject = False
            lock_continue = True
            flash("Select subject code from the list", "danger")
        elif request.form.get("subject_but") == "subject_value":
            selected_subject = request.form.get("subject")
            #valid_subjects = subject_pulldown(data_holder.get("ltpr"))
            if selected_subject in subject_pulldown(data_holder.get("ltpr")):
                data_holder["subject"] = selected_subject
                lock_subject = True
                lock_continue = False
                slot_lock = [True,True,True,True,True,True,True]             
            else:
                flash("Select a valid Subject option if available", "warning")   
        if request.form.get("end_but") == "cancel":
            reset_tt_entry()
            return redirect(url_for("tt_entry.tt_data"))
        elif request.form.get("end_but") == "end_value":
            if all(
                data_holder.get(field)
                for field in ("parent_dept", "emp_code", "dept_a", "odd_even", "semester", "ltpr", "subject")
            ):
                data_holder.pop("weekday", None)
                data_holder.pop("slot", None)
                lock_day_ = False
                lock_slot_ = True
                slot_lock = [True,True,True,True,True,True,True]
                lock_save = True
                return redirect(url_for("tt_entry.tt_slot"))
            flash("< Complete all selections before continuing >", "success")
        flash("Verify the SELECTed entries & continue if ok, otherwise CANCEL/RESET for reentry", "info") 

    semesters = semester_numbers(data_holder.get("odd_even"))
    selected_semester = data_holder.get("semester")
    ltprs = ltpr_pulldown(selected_semester) if selected_semester else []
    subjects = subject_pulldown(data_holder.get("ltpr")) if data_holder.get("ltpr") else []
    selected_values = list(data_holder.values())

    return render_template("tt_data.html", 
        lock_dept=lock_dept,lock_emp=lock_emp,lock_depta=lock_depta,
        lock_oddeven=lock_oddeven,lock_semester=lock_semester,lock_ltpr=lock_ltpr,
        lock_subject=lock_subject,lock_continue=lock_continue,
        selected_dept=data_holder.get("parent_dept"),selected_emp_code=data_holder.get("emp_code"),
        selected_dept_a=data_holder.get("dept_a"),selected_odd_even=data_holder.get("odd_even"),
        selected_semester=selected_semester,selected_ltpr=data_holder.get("ltpr"),
        selected_subject=data_holder.get("subject"),chosen_sel = selected_values,
        keys = list(data_holder.keys()),values = selected_values,
        depts_p = DEPARTMENTS,emp_codes = emp_codes,depts_a = DEPARTMENTS,  
        odds_evens = ODDEVEN,semesters = semesters,ltprs = ltprs,
        subjects = subjects,
        username=username)

# HTML Routes...........................................................................tt_slot..........
lock_day_ = False
lock_slot_ = True
lock_home_reset_save = [True,True,True]
lock_new_entry = True
@tt_entry.route("/tt_slot", methods=["GET","POST"])
def tt_slot():
    global data_holder,lock_new_entry
    global day_lock,slot_lock
    global lock_day_,lock_slot_,lock_home_reset_save
    global lock_dept
    #global day_lock_ref,slot_lock_ref
    if "username" not in session:
        return redirect(url_for("main.dashboard"))
    required_fields = (
        "parent_dept",
        "emp_code",
        "dept_a",
        "odd_even",
        "semester",
        "ltpr",
        "subject",
    )
    if not all(data_holder.get(field) for field in required_fields):
        flash("Complete all selections before continuing", "warning")
        return redirect(url_for("tt_entry.tt_data"))
    weekday_radioButtons()
    bypass_slot()
    slot_radioButtons()
    if request.method == "POST":
        if not data_holder.get("weekday") and not data_holder.get("slot"):
            lock_day_ = False
            lock_slot_ = True        
            day_value = request.form.get("day_but")
            if day_value == "weekday":
                if request.form.get("day") in weekdays:
                    data_holder["weekday"] = request.form.get("day")
                    lock_slot_ = False
                    lock_day_ = True
                else:          
                    flash("Weekday Radio Button not selected!! Select Weekday", "warning")
                    lock_day_ = False
                    lock_slot_ = True
        elif data_holder.get("weekday") in weekdays:
            lock_day_ = True
            lock_slot_ = False
            slot_value = request.form.get("slot_but")
            if slot_value == "slot":
                if request.form.get("slot") in slots:
                    data_holder["slot"] = request.form.get("slot")
                    lock_slot_ = True
                    lock_home_reset_save = [False,False,False]
                    print(lock_home_reset_save)
                else:
                    flash("Slot Radio Button not selected!! Re-enter Weekday and Slot", "warning")
                    data_holder.pop("weekday", None)
                    lock_day_ = False
                    lock_slot_ = True          
            elif slot_value == "reset":
                flash("Re-enter Weekday and Slot", "warning")
                data_holder.pop("weekday", None)
                lock_day_ = False 
                lock_slot_ = True
        hrs_action = request.form.get("home_reset_save_but") 
        if hrs_action == "save":
            if data_holder.get("weekday") in weekdays and data_holder.get("slot") in slots:
                user = User.query.filter_by(username=session["username"]).first()
                if user is None:
                    session.pop("username", None)
                    flash("Your account could not be found. Please sign in again", "danger")
                    return redirect(url_for("main.login"))
                save_tt("save", user.id)
                lock_new_entry = False
                lock_day_ = True
                lock_slot_ = True
                lock_home_reset_save = [True,True,True]
            else:
                flash("Select a weekday and time slot before saving", "info")
        elif hrs_action == "reset":
            lock_home_reset_save = [True,True,True]
            data_holder.pop("weekday", None)
            data_holder.pop("slot", None)
            lock_slot_ = True
            lock_day_ = False
            flash("Re-enter weekday and time slot to continue", "info")
        elif hrs_action == "home":
            lock_home_reset_save = [True,True,True]
            lock_day_ = True
            lock_slot_ = True
            reset_tt_entry()
            return redirect(url_for("tt_entry.tt_data"))
    exit_action = request.form.get("exit_but")
    if exit_action == "logout":
        lock_home_reset_save = [True,True,True]
        lock_day_ = True
        lock_slot_ = True
        reset_tt_entry()
        return redirect(url_for("main.logout"))
    elif exit_action == "new_entry":
        lock_home_reset_save = [True,True,True]
        lock_day_ = True
        lock_slot_ = True
        reset_tt_entry()
        return redirect(url_for("tt_entry.tt_data"))   
    chosen_sel = [
        data_holder.get("parent_dept", ""),
        data_holder.get("emp_code", ""),
        data_holder.get("dept_a", ""),
        data_holder.get("odd_even", ""),
        data_holder.get("semester", ""),
        data_holder.get("ltpr", ""),
        data_holder.get("subject", ""),
        data_holder.get("weekday", ""),
        data_holder.get("slot", ""),
    ]
    return render_template(
        "tt_slot.html",
        faculty=teacher_name(data_holder["emp_code"]),
        chosen_sel=chosen_sel,lock_day_ = lock_day_, lock_slot_ = lock_slot_,
        lock_home_reset_save = lock_home_reset_save,lock_new_entry=lock_new_entry,
        selected_day=data_holder.get("weekday"),selected_slot=data_holder.get("slot"),
        day_lock=day_lock, slot_lock=slot_lock,
        show_day_radios=not data_holder.get("weekday"),
        show_slot_radios=bool(data_holder.get("weekday")) and not bool(data_holder.get("slot")),
        username=session["username"],
    )
# HTML Routes....................................................................time_table..........
@tt_entry.route("/tt_view", methods=["GET","POST"])
def tt_view():
    department, semester, timetable = view_tt()
    return render_template("tt_view.html",
        dept_sem=department,semester=semester,
        weekdays=weekdays,slots=slots,
        timetable=timetable)
