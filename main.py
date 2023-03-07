from flask import Flask, render_template, request , redirect , url_for , flash, session
import mysql.connector
import random
import hashlib

db=mysql.connector.connect(host="localhost", user="root", passwd="your password") ##add your root password

cursor=db.cursor(buffered=True)
flag = 0


# USING DATABASE
cursor.execute("USE dbms_project_pt1 ")

app = Flask(__name__)
app.secret_key= "secret key"


@app.route('/')
def hello_world():
    ####directly open home page if someoone is already logged in
    if ('loggedin' in session) and session['loggedin'] == True:
        msg= session['firstname'] + " already logged in"
        return redirect(url_for('customer_page'))
    else:
    ###or open login page by default
        session['message'] = "Please Log In:"
        return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/err')
def error_page():
    session['message'] = "some error occured please login first"
    return render_template('error.html')
####################################




@app.route('/vendor_charts')
def v_charts_page():
    if not ('loggedin' in session) or session['loggedin']==False:
        return redirect(url_for('error_page'))
    else:
        return render_template('v_charts.html',name = session['firstname'])

@app.route('/vendor_update_stock',methods=["GET","POST"])
def v_update_stock_page():
    if not ('loggedin' in session) or session['loggedin']==False:
        return redirect(url_for('error_page'))
    else:
        # if request.method=='POST':
        #     if request.form['enter_prod_btn']=="val_prod":
        #         pid = request.form['pid_btn']
        #         ptyp = request.form['ptyp_btn']
        #         pname = request.form['pname_btn']
        #         p_cp = request.form['p_cp_btn']
        #         p_sp = request.form['p_sp_btn']
        #         cursor.callproc('add_product',(int(pid),ptyp,pname,float(p_cp),float(p_sp)))
        #         db.commit()
        #         return render_template('v_update_stock.html',name = session['firstname'])
        #     else:
        #         unit = request.form['pid_btn']
        #         pid = request.form['stkquantity_btn']
        #         quantity = request.form['qunit_btn']
        #         vid = str(session['id'])
        #         cursor.callproc('update_stock',(vid,int(pid),int(quantity),unit))
        #         db.commit()
        #         return render_template('v_update_stock.html',name = session['firstname'])
        #



        if request.method=='POST' and request.form['update_stk_btn']=="val_prod":
            pid = request.form['pid_btn']
            ptyp = request.form['ptyp_btn']
            pname = request.form['pname_btn']
            p_cp = request.form['p_cp_btn']
            p_sp = request.form['p_sp_btn']
            cursor.callproc('add_product',(int(pid),ptyp,pname,float(p_cp),float(p_sp)))
            db.commit()
            return render_template('v_update_stock.html',name = session['firstname'])


        if request.method=='POST' and request.form['update_stk_btn']=="val_stk":
                unit = request.form['qunit_btn']
                pid = request.form['p_id_btn']
                pquant = request.form['pquant_btn']
                vid = str(session['id'])
                cursor.callproc('update_stock',(vid,int(pid),int(pquant),unit))
                db.commit()
                return render_template('v_update_stock.html',name = session['firstname'])


        else:
             return render_template('v_update_stock.html',name = session['firstname'])




###############################

@app.route('/acc',methods =["GET","POST"])
def customer_page():

    if session['cv_flag']==0:
        if request.method=='POST' and request.form['update_bud_btn']=="val_bud":
            bud = request.form['new_budget_btn']
            cmd2 = "update customer set budget = " + bud + " where customer_id = " +  str(session['id'])
            cursor.execute(cmd2)
            db.commit()
            return redirect(url_for('customer_page'))
        else:
            print(type(str(session['id'])))
            cmd11 = "select sum(transaction.quantity * product.selling_price) from transaction join product on product.product_id = transaction.product_id where customer_id = " + str(session['id'])
            cursor.execute(cmd11)
            expen= cursor.fetchone()
            cmd1 = "select budget from customer where customer_id = " + str(session['id'])
            cursor.execute(cmd1)
            budget = cursor.fetchone()

            print(budget)
            return render_template('customer.html',name = session['firstname'],budget=budget, expen = expen)



    elif session['cv_flag']==1:

        temp4 = "select sum(product.selling_price - product.cost_price) from transaction join product on product.product_id = transaction.product_id where vendor_id = " + str(session['id'])
        cursor.execute(temp4)
        profit=cursor.fetchone()
        return render_template('vendor.html',name = session['firstname'],profit=profit)
    else:
        return redirect(url_for('error_page'))
    
    
    # ******VENDOR******** INSERTS NEW TRANSACTION
@app.route('/enter_transaction',methods=['GET','POST'])
def enter_transaction_func():
    if request.method=='POST' and request.form['enter_trans_btn']=="val_trans":
        cid = request.form['cid_btn']
        pid = request.form['pid_btn']
        # vid = request.form['vid_btn']
        quant = request.form['quant_btn']
        units= request.form['units_btn']
        vid_temp = session['id']
        cursor.execute('call enter_transaction(%s,%s,%s,%s,%s)', (int(cid),int(vid_temp),int(pid),int(quant),units))
        db.commit()
        return redirect(url_for('customer_page'))
    
    

@app.route('/charts')
def charts_page():
    if not ('loggedin' in session) or session['loggedin']==False:
        return redirect(url_for('error_page'))
    else:
        return render_template('charts.html',name = session['firstname'])

@app.route('/stock',methods=['GET','POST'])
def stock_page():
    if not ('loggedin' in session) or session['loggedin']==False:
        return redirect(url_for('error_page'))
    else:
        temp7="select * from product"
        cursor.execute(temp7)
        prod_det = cursor.fetchall()

        temp=''
        cursor.execute( 'select * from vendor')
        data = cursor.fetchall()

        if request.method=='POST':
            temp = request.form['vstock_btn']
            print("temp val is")
            print(temp)
            print(type(temp))
            cmd2 = 'select * from stock where vendor_id = ' + temp
            cursor.execute(cmd2)
            data_table = cursor.fetchall()
            print(data_table)
            print(data_table[0][0])
        # cursor.execute( 'SELECT * from login_credentials')
        # data = cursor.fetchall()
            return render_template('stock.html',name = session['firstname'],data = data,table_data = data_table,p_det=prod_det)
        else:
            return render_template('stock.html',name = session['firstname'],data = data,p_det=prod_det)




@app.route('/transaction_list')
def transaction_list_page():
    if not ('loggedin' in session) or session['loggedin']==False:
        return redirect(url_for('error_page'))
    else:
        cmd6= "select * from transaction where customer_id = " + str(session['id']) + " or vendor_id = " + str(session['id'])
        cursor.execute(cmd6)
        trans = cursor.fetchall()
        if session['cv_flag']==0:
            return render_template('transaction.html',trans = trans,name = session['firstname'])
        elif session['cv_flag']==1:
            return render_template('v_transaction.html',trans = trans,name = session['firstname'])



@app.route('/logout')
def logout_page():
    session.pop('loggedin',None)
    session.pop('username', None)
    session.pop('id', None)
    session.pop('firstname', None)
    session.pop('cv_flag', None)

    # if not('message' in session) or not session['message']:
    session['message']= "Please Log in :)"

    return render_template('login.html')



@app.route('/signin' , methods=['GET', 'POST'])
def login_page():
    if request.method=='POST' and request.form['register_btn']=="val_signup":
        username = request.form['signup_username_btn']
        fname = request.form['signup_fname_btn']
        lname = request.form['signup_lname_btn']
        password = request.form['signup_password_btn']
        cv_flag= request.form['signup_cv_flag_btn']

        h_pass = hashlib.md5(password.encode("utf-8")).hexdigest()
        print(h_pass)

        phonenumber = request.form['signup_phone_btn']
        cursor.execute('call insert_new_user(%s,%s,%s,%s,%s,%s)', (username,h_pass,fname,lname,int(phonenumber),int(cv_flag)))
        db.commit()
        session['message']='account created successfully'
    return render_template('login.html')

@app.route('/home',  methods=['GET', 'POST'])
def home_page():
    msg=''
    if request.method=='POST' and ('loggedin' in session) and session['loggedin'] == True:
        session['message']= session['firstname'] + " was already logged in...now logged out"
        return redirect(url_for('logout_page'))

    elif request.method=='POST' and request.form['login_btn']=="val_login":
        username = request.form['login_username_btn']
        password = request.form['login_password_btn']
        h_pass = hashlib.md5(password.encode("utf-8")).hexdigest()
        cursor.execute( 'SELECT * from login_credentials where username= %s and password=%s ', (username,h_pass) )
        record= cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['id'] = record[0]
            session['firstname'] = (record[3][0]).upper() + record[3][1:]
            print((record[3][0]).upper())
            session['cv_flag']= int(record[6])
            print(session['id'])
            msg="login successful"
            flash(msg)

            return redirect(url_for('customer_page'))
        else:
         session['message'] = " wrong credentials...try again :( "
         return render_template('login.html')
    else:
        return redirect(url_for('error_page'))


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)
