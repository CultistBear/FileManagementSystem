from flask import Flask, request, render_template, redirect, url_for, session, send_file
import os
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer
from forms import SignUp, Login, Files, Upload
from flask_wtf.csrf import CSRFProtect
from databaseManagement import DB
import hashlib
from constants import FLASK_SECRET_KEY, PASSWORD_SALT, CURRENT_WORKING_DIRECTORY, FILE_NAME_KEY

################################

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
serializer = URLSafeSerializer(FLASK_SECRET_KEY)
csrf = CSRFProtect(app)

@app.before_request
def make_session_temp():
    if session.get("username", None) == None and request.endpoint not in ["login", "signup", "static", 'logout']:
        return redirect(url_for("login"))
    if session.get("username", None) != None and request.endpoint in ["login", "signup"]:
        return redirect(url_for("home"))
    session.permanent = False

################################

@app.route('/', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    db = DB()
    form = SignUp()
    if form.is_submitted():
        if form.validate():
            name = request.form.get("Name")
            username = request.form.get("Username")
            phone = request.form.get("Phone")
            password = request.form.get("Password")
            email = request.form.get("Email")
            qer = db.query(r"select * from Users where Username = '%s' or Email = '%s'" % (username, email))
            if (len(qer) != 0):
                if (qer[0]["Username"] == username):
                    session["error"] = "Username Already Exists"
                else:
                    session["error"] = "Email Already Exists"
                return redirect(url_for("signup"))
            password += PASSWORD_SALT
            db.query(r"insert into Users(Username, Name, Phone, Email, Password, role) values('%s','%s','%s','%s','%s','user')" % (
                username, name, phone, email, hashlib.md5(password.encode()).hexdigest()))
            session["message"] = "Successfully Signed Up"
            db.close()
            return redirect(url_for("signup"))
        else:
            session["error"] = ". ".join([i[0] for i in form.errors.values()])
            return redirect(url_for("signup"))
        
    error = session.pop("error", None)
    message = session.pop("message", None)
    return render_template('signup.html', form=form, message=message, error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    db = DB()
    if form.validate_on_submit():
        emailorusername = form.UsernameorEmail.data
        password = form.Password.data
        password += PASSWORD_SALT
        password = hashlib.md5(password.encode()).hexdigest()
        if (len(db.query(r"select * from Users where Username = '%s' LIMIT 1" % (emailorusername))) != 0):
            query = db.query(
                r"select * from Users where Username = '%s' LIMIT 1" % (emailorusername))
            if (query[0]['Password'] == password):
                session["username"] = emailorusername
                return redirect(url_for('home'))
            else:
                session["error"] = 'Invalid Password'
                return redirect(url_for("login"))
        session["error"] = 'Invalid Username'
        return redirect(url_for('login'))
    error = session.pop("error", None)
    message = session.pop("message",None)
    return render_template('login.html', form=form, error=error, message=message)


@app.route("/logout")
def logout():
    session.pop("username", None)
    session["message"] = "Successfully Logged Out"
    return redirect(url_for("login"))

################################

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/myfile', methods=['GET', 'POST'])
def myfile():
    userstorage = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'])
    files = None
    form = Files()
    upload_files = Upload()
    if(os.path.exists(userstorage)):
        filesPrivate = os.listdir(os.path.join(userstorage,'private'))
        filesPublic = os.listdir(os.path.join(userstorage,'public'))
    else:
        os.mkdir(userstorage)
        os.mkdir(os.path.join(userstorage, 'public'))
        os.mkdir(os.path.join(userstorage, 'private'))
        files=None
    
    if(not filesPrivate and not filesPublic):
        files = {}
        
    if(filesPrivate):
        files = {i:["Private"] for i in filesPrivate}
    if(filesPublic):
        files.update({i:["Public"] for i in filesPublic})
    
    files = {i:files[i] for i in sorted(files)}
    
    cipher_name = Fernet(FILE_NAME_KEY)
    
    for i in files.keys():
        files[i].append(cipher_name.encrypt(i.encode()).decode())

    if form.validate_on_submit():
        key = cipher_name.decrypt(form.Index.data).decode()
        file_path = os.path.join(userstorage, files[key][0], key)
        action = request.form['button']
        if(action=="Delete"):
            if(os.path.isfile(file_path)):
                os.remove(file_path)
                return redirect(url_for('myfile'))
        elif(action=="Rename"):
            if(os.path.isfile(file_path)):
                os.rename(file_path,os.path.join(userstorage,files[key][0],request.form['Rename_new']))
                return redirect(url_for('myfile'))
        elif(action=="Download"):
            if(os.path.isfile(file_path)):
                return send_file(file_path, as_attachment=True)
        return redirect(url_for('myfile'))
    
    elif upload_files.validate_on_submit():
        file_upload = request.files['File']
        file_type = request.form['File_Type']
        file_upload.save(os.path.join(userstorage, file_type, secure_filename(file_upload.filename)))
        return redirect(url_for('myfile'))
    
    return render_template('myfile.html',files=files,form=form, upload_files=upload_files)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
