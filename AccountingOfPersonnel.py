from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from forms import LoginForm, ReceiptForm,NewDepartmentForm,NewSubdivisionForm, NewPositionForm
from accounting_personnelDB import User, Subdivision, Department,Position, Worksheet
from datetime import date, datetime
from sqlalchemy import func

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


@app.route('/',methods=['POST','GET'])
def start_page():
    form = LoginForm(request.form)
    conn = db.engine.connect()
    if request.method == 'POST' and form.validate():
        login_form = form.login.data
        password_form = form.password.data
        if db.session.query(User).filter_by(login = login_form).scalar() != None:
            if db.session.query(User).filter_by(password = password_form) != None:
                session['curent_admin'] = login_form
                conn.close()
                return redirect(url_for('main_page'))
    return render_template('startPage.html')


@app.route('/MainPage')
def main_page():
    worksheet_query = db.session.query(Worksheet,Position,Department,Subdivision)\
    .join(Position)\
    .filter(Worksheet.position_id == Position.id)\
    .join(Department)\
    .filter(Worksheet.department_id == Department.id)\
    .join(Subdivision)\
    .filter(Subdivision.id == Department.subdivision_id)\
    .filter(Worksheet.date_of_dismissal == None)

    # print(worksheet_query)

    # works = db.session.query(Worksheet)\
    # .filter(Worksheet.name == 'Krelcov U.A.').first()
    # print(works.date_of_dismissal)
    return render_template('MainPage.html',worksheet_html=worksheet_query)

@app.route('/DissmisalPage')
def dissmisal_page():
    worksheet_query = db.session.query(Worksheet,Position,Department,Subdivision)\
    .join(Position)\
    .filter(Worksheet.position_id == Position.id)\
    .join(Department)\
    .filter(Worksheet.department_id == Department.id)\
    .join(Subdivision)\
    .filter(Subdivision.id == Department.subdivision_id)\
    .filter(Worksheet.date_of_dismissal != None)

    return render_template('dissmisal_page.html', worksheet_html=worksheet_query)


@app.route('/addSubdivision',methods=['GET','POST'])
def add_Subdivision():
    form = NewSubdivisionForm(request.form)
    conn = db.engine.connect()
    if request.method == 'POST' and form.validate():
        subdivision_name = form.subdivision.data
        cypher_name = form.cypher.data

        if db.session.query(Subdivision).filter_by(name= subdivision_name).scalar() == None:
            subdivision_db = Subdivision(subdivision_name,cypher_name)
            db.session.add(subdivision_db)
            db.session.commit()
            db.session.close()
        conn.close()
        return redirect(url_for('show_Subdivision'))

    return render_template('AddNewSubdivision.html')

@app.route('/editSubdivision/<string:ids>',methods=['GET', 'POST'])
def change_Subdivision(ids):
    conn = db.engine.connect()
    #subdivision_form = db.session.query(Subdivision)
    #result_dep = Department.query.filter(Department.id == ids).first()
    result_subd = db.session.query(Subdivision).filter(Subdivision.id == ids).first()
    form = NewSubdivisionForm(request.form)

    form.subdivision.data = result_subd.name
    form.cypher.data = result_subd.cypher



    if request.method == 'POST' and form.validate():
        subdivision_name = request.form['subdivision_name']
        subdivision_cypher = request.form['subdivision_cypher']

        db.session.query(Subdivision).filter(Subdivision.id == ids).\
            update({'name':subdivision_name,'cypher':subdivision_cypher})

        db.session.commit()
        db.session.close()

        return redirect(url_for('show_Subdivision'))
    conn.close()
    return render_template('ChangeSubdivision.html', form=form)

@app.route('/showSubdivisions',methods=['GET', 'POST'])
def show_Subdivision():
    result_html = db.session.query(Subdivision)

    result_html2 = db.session.query( Subdivision, func.count(Department.id)) \
        .outerjoin(Department, Department.subdivision_id == Subdivision.id) \
        .group_by(Subdivision)

    result_department_html = db.session.query(Department)

#     connection = engine.connect()
#     result = session.execute("""SELECT count(department.id), subdivision.name  FROM subdivision,department, worksheet
# where (subdivision.id = department.subdivision_id) and
# (department.id = worksheet.department_id)
# group by(subdivision.name);""")
#     print(result)

    return render_template('showSubdivision.html',subdivision_html=result_html2,department_html = result_department_html)

@app.route('/delete_subdivision/<string:ids>',methods=['GET', 'POST'])
def delete_subd(ids):
    conn = db.engine.connect()
    db.session.query(Subdivision).filter(Subdivision.id == ids).delete()
    db.session.commit()
    db.session.close()

    conn.close()
    return redirect(url_for('show_Subdivision'))

@app.route('/addDepartment',methods=['GET','POST'])
def add_Department():
    subdivision_form = db.session.query(Subdivision)
    form = NewDepartmentForm(request.form)
    conn = db.engine.connect()
    if request.method == 'POST' and form.validate():
        id_subdivision = request.form['subd']
        department_name = form.department.data

        if db.session.query(Department).filter_by(name = department_name).scalar() == None:
            department_db = Department(department_name,id_subdivision)
            db.session.add(department_db)
            db.session.commit()
            db.session.close()
        conn.close()
        return redirect(url_for('show_Department'))

    return render_template('AddNewDepartment.html',subdivision=subdivision_form)

@app.route('/showDepartments',methods=['GET', 'POST'])
def show_Department():
    # result_html = db.session.query(Department,Subdivision)\
    # .join(Subdivision)\
    # .filter(Department.subdivision_id == Subdivision.id)

    department_count = db.session.query(Department,Subdivision,func.count(Worksheet.id))\
        .outerjoin(Worksheet, Department.id == Worksheet.department_id) \
        .join(Subdivision,Department.subdivision_id == Subdivision.id)\
        .filter(Worksheet.date_of_dismissal == None) \
        .group_by(Department,Subdivision) \
        .order_by(func.count(Worksheet.id).desc())

    worsh_names = db.session.query(Worksheet) \
        .filter(Worksheet.date_of_dismissal == None)



    print(worsh_names)

    return render_template('showDepartment.html',department_html=department_count, work_names = worsh_names)

@app.route('/editDepartments/<string:ids>',methods=['GET', 'POST'])
def change_Department(ids):
    conn = db.engine.connect()
    subdivision_form = db.session.query(Subdivision)
    #result_dep = Department.query.filter(Department.id == ids).first()
    result_dep = db.session.query(Department).filter(Department.id == ids).first()

    result_subd = db.session.query(Subdivision).filter(Subdivision.id == result_dep.subdivision_id).first()
    form = NewDepartmentForm(request.form)

    form.department.data = result_dep.name





    if request.method == 'POST' and form.validate():
        id_subdivision = request.form['subd']
        department_name = request.form['department']

        db.session.query(Department).filter(Department.id == ids).\
            update({'name':department_name,'subdivision_id':id_subdivision})

        db.session.commit()
        db.session.close()

        return redirect(url_for('show_Department'))
    conn.close()
    return render_template('ChangeDepartment.html', subdivision=subdivision_form,form=form,result_subd=result_subd)

@app.route('/delete_depart/<string:ids>',methods=['GET', 'POST'])
def delete_depart(ids):
    print(ids)
    conn = db.engine.connect()
    db.session.query(Department).filter(Department.id == ids).delete()
    db.session.commit()
    db.session.close()

    conn.close()
    return redirect(url_for('show_Department'))


@app.route('/addPosition', methods=['GET', 'POST'])
def add_Position():
    form = NewPositionForm(request.form)
    conn = db.engine.connect()
    if request.method == 'POST' and form.validate():
        position_name = form.name.data
        position_salary = form.salary.data

        if db.session.query(Position).filter_by(name=position_name).scalar() == None:
            position_db = Position(position_name, position_salary)
            db.session.add(position_db)
            db.session.commit()
            db.session.close()
        conn.close()
        return redirect(url_for('show_Position'))

    return render_template('AddNewPosition.html')

@app.route('/editPosition/<string:ids>',methods=['GET', 'POST'])
def change_Position(ids):
    conn = db.engine.connect()

    result_position = db.session.query(Position).filter(Position.id == ids).first()
    form = NewPositionForm(request.form)

    form.name.data = result_position.name
    form.salary.data = result_position.salary

    if request.method == 'POST' and form.validate():
        position_name = request.form['position_name']
        position_salary = request.form['position_salary']

        db.session.query(Position).filter(Position.id == ids).\
            update({'name':position_name,'salary':position_salary})

        db.session.commit()
        db.session.close()

        return redirect(url_for('show_Position'))
    conn.close()
    return render_template('ChangePosition.html',form=form)

@app.route('/delete_position/<string:ids>',methods=['GET', 'POST'])
def delete_position(ids):
    conn = db.engine.connect()
    db.session.query(Position).filter(Position.id == ids).delete()
    db.session.commit()
    db.session.close()

    conn.close()
    return redirect(url_for('show_Position'))

@app.route('/showPosition',methods=['GET', 'POST'])
def show_Position():

    position_count = db.session.query(Position,func.count(Worksheet.id)) \
        .outerjoin(Worksheet,Position.id == Worksheet.position_id) \
        .filter(Worksheet.date_of_dismissal == None)\
        .group_by(Position)\
        .order_by(func.count(Worksheet.id).desc())

    worsh_names = db.session.query(Worksheet) \
        .filter(Worksheet.date_of_dismissal == None)

    return render_template('showPosition.html',position_html=position_count,work_names = worsh_names )



@app.route('/showWorksheets',methods=['GET', 'POST'])
def show_Worksheets():
    result_html = db.session.query(Position)
    return render_template('showPosition.html',position_html=result_html)



@app.route('/addWorksheet', methods=['GET','POST'])
def add_Worksheet():
    form = ReceiptForm(request.form)
    subdivision_form = db.session.query(Subdivision)
    department_form = db.session.query(Department)
    position_form = db.session.query(Position)

    conn = db.engine.connect()
    join_table_subdivision = db.session.query(Subdivision,Department) \
        .join(Department) \
        .filter(Department.subdivision_id == Subdivision.id)

    if request.method == 'POST' and form.validate():
        name_department = request.form['depart']
        department_id = db.session.query(Department).filter(Department.name == name_department).first()
        department_id = department_id.id

        position_id = request.form['position']

        name = form.name.data
        receipt_date = request.form['receipt_date']
        academic_title = request.form['academic_title']
        year_of_birth = request.form['year_of_birth']
        # date_of_dismissal = form.date_of_dismissal.data
        address = request.form['address']
        telephone = request.form['telephone']
        previous_employment = request.form['previous_employment']
        diploma_number = request.form['diploma_number']
        receiptDB = Worksheet(name,department_id,receipt_date,position_id,academic_title,year_of_birth,None,address,telephone,previous_employment,diploma_number)
        db.session.add(receiptDB)
        db.session.commit()
        db.session.close()

        return redirect(url_for('main_page'))
    return render_template('AddNewWorksheet.html',position_html=position_form,subdivision_html=subdivision_form,department_html = department_form,form=form)


@app.route('/editWorksheet/<string:ids>',methods=['GET', 'POST'])
def change_Worksheet(ids):
    conn = db.engine.connect()

    result_worksheet = db.session.query(Worksheet).filter(Worksheet.id == ids).first()
    department_form = db.session.query(Department)
    subdivision_form = db.session.query(Subdivision)
    position_form = db.session.query(Position)

    department_result_form = db.session.query(Department).filter(result_worksheet.department_id == Department.id).first()
    subdivision_result_form = db.session.query(Subdivision).filter(Subdivision.id == Department.subdivision_id).first()
    position_result_form = db.session.query(Position).filter(result_worksheet.position_id == Position.id).first()


    form = ReceiptForm(request.form)

    form.name.data = result_worksheet.name
    form.receipt_date.data = result_worksheet.receipt_date
    form.academic_title.data = result_worksheet.academic_title
    form.year_of_birth.data = result_worksheet.year_of_birth
    form.address.data = result_worksheet.address
    form.telephone.data = result_worksheet.telephone
    form.previous_employment.data = result_worksheet.previous_employment
    form.diploma_number.data = result_worksheet.diploma_number


    if request.method == 'POST' and form.validate():
        subdivision = request.form['sub']
        department = db.session.query(Department).filter(Department.name == request.form['depart']).first()
        department = department.id

        position = request.form['position']
        name = request.form['name']
        receipt_date = request.form['receipt_date']
        academic_title = request.form['academic_title']
        year_of_birth = request.form['year_of_birth']
        address = request.form['address']
        telephone = request.form['telephone']
        previous_employment = request.form['previous_employment']
        diploma_number = request.form['diploma_number']


        db.session.query(Worksheet).filter(Worksheet.id == ids).\
            update({'name':name,'department_id':department,'receipt_date':receipt_date,'position_id':position,
                    'academic_title':academic_title,'year_of_birth':year_of_birth,
                    'address':address,'telephone':telephone,'previous_employment':previous_employment,
                    'diploma_number':diploma_number})

        db.session.commit()
        db.session.close()

        return redirect(url_for('main_page'))
    conn.close()
    return render_template('ChangeWorksheet.html', position_html=position_form,
                           subdivision_html=subdivision_form,department_html = department_form,
                           res_sub=subdivision_result_form, res_dep=department_result_form,
                           res_pos=position_result_form, form=form)

@app.route('/delete_worksheet/<string:ids>',methods=['GET', 'POST'])
def delete_worksheet(ids):
    conn = db.engine.connect()
    dissmisal_date = datetime.now()
    dissmisal_date = dissmisal_date.date()
    db.session.query(Worksheet).filter(Worksheet.id == ids)\
        .update({'date_of_dismissal':dissmisal_date})
    db.session.commit()
    db.session.close()

    conn.close()
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.secret_key = 'secret111'
    app.run(debug=True)

