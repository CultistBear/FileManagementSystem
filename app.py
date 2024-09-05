from flask import Flask, request, render_template, redirect, url_for, session, send_file
import os
import time
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer
from forms import SignUp, Login, Files, Upload, DownloadPublic, FileLogs
from flask_wtf.csrf import CSRFProtect
from databaseManagement import DB
import hashlib
import datetime
from constants import FLASK_SECRET_KEY, PASSWORD_SALT, CURRENT_WORKING_DIRECTORY, FILE_NAME_KEY, FILE_SHARE_KEY,TIME_OF_DAY

################################

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
serializer = URLSafeSerializer(FLASK_SECRET_KEY)
csrf = CSRFProtect(app)

@app.before_request
def make_session_temp():
    session.permanent = False
    #if not request.is_secure:
    #    return redirect(request.url.replace('http://', 'https://', 1), code = 301)
    if session.get("username", None) == None and request.endpoint not in ["login", "signup", "static", 'logout']:
        return redirect(url_for("login"))
    if session.get("username", None) != None and request.endpoint in ["login", "signup"]:
        return redirect(url_for("home"))

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
        if (len(db.query(r"select * from Users where (Username = '%s' or email = '%s') LIMIT 1" % (emailorusername, emailorusername))) != 0):
            query = db.query(
                r"select * from Users where (Username = '%s' or email = '%s')LIMIT 1" % (emailorusername, emailorusername))
            if (query[0]['Password'] == password):
                session["username"] = query[0]['Username']
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
    db = DB()
    form = Files()
    upload_files = Upload()
    userstorage = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'])
    files = []
    if(os.path.exists(userstorage)):
        files = db.query(r"select FileName, FileType, LastEditedUser, LastEditedTime from Files where FileOwner = '%s'" % (session['username']))
    else:
        os.mkdir(userstorage)
    
    cipher_name = Fernet(FILE_NAME_KEY)
    
    files = sorted(files, key=lambda x: x['FileName'])
    for file in files:
        file['Index'] = cipher_name.encrypt((file['FileName']+"!!!!!"+file['FileType']).encode()).decode()
    
    if form.validate_on_submit():
        FileName, FileType = cipher_name.decrypt(form.Index.data).decode().split("!!!!!")
        file_path = os.path.join(userstorage, FileName)
        action = request.form['button']
        if(action=="Delete"):
            if(os.path.isfile(file_path)):
                with open(os.path.join(userstorage, FileName+"_log.txt"), "a", encoding="utf-8") as i:
                    i.write("File %s Deleted by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                    i.close()
                if(os.path.exists(os.path.join(userstorage, "deleted-logs"))):
                    pass
                else:
                    os.mkdir(os.path.join(userstorage, "deleted-logs"))
                os.replace(os.path.join(userstorage, FileName+"_log.txt"), os.path.join(userstorage,"deleted-logs",FileName+"_log.txt"))
                os.remove(file_path)
                db.query(r"delete from Files where FileName = '%s' and FileOwner = '%s'" % (FileName, session['username']))
                return redirect(url_for('myfile'))
        elif(action=="Rename"):
            if(os.path.isfile(file_path)):
                with open(os.path.join(userstorage, FileName+"_log.txt"), "a", encoding="utf-8") as i:
                    i.write("File %s renamed as %s by %s at %s.\n"%(FileName, request.form['Rename_new'], session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                    i.close()
                os.rename(file_path,os.path.join(userstorage,request.form['Rename_new']))
                os.rename(os.path.join(userstorage, FileName+"_log.txt"), os.path.join(userstorage, request.form['Rename_new']+"_log.txt"))
                db.query(r"update Files set FileName = '%s', LastEditedUser = '%s', LastEditedTime = '%s' where FileName = '%s' and FileOwner = '%s'" % (request.form['Rename_new'], session['username'], db.query("select now()")[0]['now()'], FileName, session['username']))
                return redirect(url_for('myfile'))
        elif(action=="Download"):
            if(os.path.isfile(file_path)):
                with open(os.path.join(userstorage, FileName+"_log.txt"), "a", encoding="utf-8") as i:
                    i.write("File %s downloaded by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                    i.close()
                return send_file(file_path, as_attachment=True)
        elif(action =="Share"):
            cipher_share = Fernet(FILE_SHARE_KEY)
            share_link_viewer = cipher_share.encrypt((FileName+"!!!!!"+session['username']+"!!!!!"+"Viewer").encode()).decode()
            share_link_editor = cipher_share.encrypt((FileName+"!!!!!"+session['username']+"!!!!!"+"Editor").encode()).decode()
            with open(os.path.join(userstorage, FileName+"_log.txt"), "a", encoding="utf-8") as i:
                i.write("File %s shared by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                i.close()
            session['flag'] = 1
            session['share_links'] = [request.scheme + '://' + request.host + url_for("download_file", encfilestr=share_link_viewer), request.scheme + '://' + request.host + url_for("download_file", encfilestr=share_link_editor)]
            return redirect(url_for('myfile'))
        return redirect(url_for('myfile'))
    
    elif upload_files.validate_on_submit():
        file_upload = request.files['File']
        file_type = request.form['File_Type']
        file_upload.save(os.path.join(userstorage, secure_filename(file_upload.filename)))
        db.query(r"insert into Files(FileName, FileOwner, FileType, LastEditedUser, LastEditedTime) values('%s','%s','%s','%s','%s')" % (secure_filename(file_upload.filename), session['username'], file_type, session['username'], db.query("select now()")[0]['now()']))
        with open(os.path.join(userstorage, secure_filename(file_upload.filename)+"_log.txt"), "a", encoding="utf-8") as i:
            i.write("File %s Uploaded by %s at %s.\n"%(secure_filename(file_upload.filename), session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
            i.close()
        #if(os.path.exists(os.path.join(userstorage, secure_filename(file_upload.filename))) == False)
        return redirect(url_for('myfile'))
    flag = session.pop('flag', 0)
    share_links = session.pop('share_links', None)
    return render_template('myfile.html',files=files,form=form, upload_files=upload_files, flag = flag, share_links = share_links)

@app.route("/public", methods=['GET', 'POST'])
def publicfiles():
    db = DB()
    form =  DownloadPublic()
    cipher_name = Fernet(FILE_NAME_KEY)
    index = []
    publicFileList = db.query(r"select FileName, FileOwner, LastEditedUser, LastEditedTime from Files where FileType='public'")
    if(publicFileList):
        publicFileList = sorted(publicFileList, key=lambda x: x['FileName'])
        for row in publicFileList:
            index.append(cipher_name.encrypt((row["FileName"]+"!!!!!"+row["FileOwner"]).encode()).decode())
            row.update({"FileName":row['FileName']})
            row.update({"FileOwner":hashlib.shake_256(row['FileOwner'].encode("utf-8")).hexdigest(length=8)})
            row.update({"LastEditedUser":hashlib.shake_256(row['LastEditedUser'].encode("utf-8")).hexdigest(length=8)})
            timestr=row['LastEditedTime'].ctime().split()
            timeofday=TIME_OF_DAY[int(int(timestr[3][:2])/6)]
            week=str(int(int(timestr[2])/7)+1)
            row.update({"LastEditedTime":timeofday+", Week "+week+" of "+timestr[1]+", "+timestr[4]})
    else:
        publicFileList = []
    
    if form.validate_on_submit():
        FileName,FileOwner=cipher_name.decrypt(form.Index.data).decode().split("!!!!!")
        userstorage = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', FileOwner)
        if(os.path.isfile(os.path.join(userstorage, FileName))):
            with open(os.path.join(userstorage, secure_filename(FileName)+"_log.txt"), "a", encoding="utf-8") as i:
                i.write("File %s Downloaded by %s at %s.\n"%(secure_filename(FileName), session['username'], time.asctime()))
                i.close()
            return send_file(os.path.join(userstorage, FileName), as_attachment=True)
        
    return render_template("publicfiles.html", publicFileList=publicFileList, form=form, index=index)

@app.route('/edit/<string:encfilestr>', methods=['GET', 'POST'])
def download_file(encfilestr):
    
    cipher_share = Fernet(FILE_SHARE_KEY)
    filename, fileowner, authority = cipher_share.decrypt(encfilestr.encode()).decode().split("!!!!!")
    if(os.path.exists(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner, filename))):
        if(authority == "Viewer"):
            with open(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner, filename)+"_log.txt", "a", encoding="utf-8") as i:
                i.write("File %s Accessed with Viewer Access by %s at %s.\n"%(filename, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                i.close()
            return render_template("editspace.html", authority=authority, encfilestr = encfilestr)
        elif(authority == "Editor"):
            db = DB()
            form = Files()
            upload_files = Upload()
            filepath = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner)
            filestorage = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner, filename)
            files = db.query(r"select FileName, FileType, LastEditedUser, LastEditedTime from Files where FileOwner = '%s' and FileName = '%s'" % (fileowner, filename))
            with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                i.write("File %s Accessed with Editor Access by %s at %s.\n"%(files[0]['FileName'], session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                i.close()
            cipher_name = Fernet(FILE_NAME_KEY)
            
            for file in files:
                file['Index'] = cipher_name.encrypt((file['FileName']+"!!!!!"+file['FileType']).encode()).decode()

            if form.validate_on_submit():
                FileName, FileType = cipher_name.decrypt(form.Index.data).decode().split("!!!!!")
                action = request.form['button']
                if(action=="Delete"):
                    if(os.path.isfile(filestorage)):
                        os.remove(filestorage)
                        db.query(r"delete from Files where FileName = '%s' and FileOwner = '%s'" % (FileName, fileowner))
                        with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                            i.write("File %s Deleted by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                            i.close()
                        if(os.path.exists(os.path.join(filepath, "deleted-logs"))):
                            pass
                        else:
                            os.mkdir(os.path.join(filepath, "deleted-logs"))
                        os.replace(os.path.join(filestorage+"_log.txt"), os.path.join(filepath,"deleted-logs",FileName+"_log.txt"))
                        return redirect(url_for("download_file", encfilestr=encfilestr))
                elif(action=="Rename"):
                    cipher_share = Fernet(FILE_SHARE_KEY)
                    share_link_editor = cipher_share.encrypt((request.form['Rename_new']+"!!!!!"+fileowner+"!!!!!"+"Editor").encode()).decode()
                    if(os.path.isfile(filestorage)):
                        os.rename(filestorage,os.path.join(filepath,request.form['Rename_new']))
                        db.query(r"update Files set FileName = '%s', LastEditedTime = '%s', LastEditedUser = '%s' where FileName = '%s' and FileOwner = '%s'" % (request.form['Rename_new'], db.query("select now()")[0]['now()'], session['username'], FileName, fileowner))
                        with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                            i.write("File %s Renamed to %s by %s at %s.\n"%(FileName, request.form['Rename_new'], session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                            i.close()
                        os.rename(filestorage+"_log.txt", os.path.join(filepath,request.form['Rename_new'])+"_log.txt")
                        return redirect(url_for("download_file", encfilestr=share_link_editor))
                elif(action=="Download"):
                    if(os.path.isfile(filestorage)):
                        with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                            i.write("File %s Downloaded by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                            i.close()
                        return send_file(filestorage, as_attachment=True)
                elif(action =="Share"):
                    cipher_share = Fernet(FILE_SHARE_KEY)
                    share_link_viewer = cipher_share.encrypt((FileName+"!!!!!"+fileowner+"!!!!!"+"Viewer").encode()).decode()
                    share_link_editor = cipher_share.encrypt((FileName+"!!!!!"+fileowner+"!!!!!"+"Editor").encode()).decode()
                    with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                            i.write("File %s Shared by %s at %s.\n"%(FileName, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                            i.close()
                    session['flag'] = 1
                    session['share_links'] = [request.scheme + '://' + request.host + url_for("download_file", encfilestr=share_link_viewer), request.scheme + '://' + request.host + url_for("download_file", encfilestr=share_link_editor)]
            elif upload_files.validate_on_submit():
                file_upload = request.files['File']
                os.remove(filestorage)
                db.query(r"delete from Files where FileName = '%s' and FileOwner = '%s'" % (filename, fileowner))
                file_upload.save(os.path.join(filepath, secure_filename(file_upload.filename)))
                db.query(r"insert into Files(FileName, FileOwner, FileType, LastEditedUser, LastEditedTime) values('%s','%s','%s','%s','%s')" % (secure_filename(file_upload.filename), fileowner, files[0]['FileType'], session['username'], db.query("select now()")[0]['now()']))
                cipher_share = Fernet(FILE_SHARE_KEY)
                share_link_editor = cipher_share.encrypt((secure_filename(file_upload.filename)+"!!!!!"+fileowner+"!!!!!"+"Editor").encode()).decode()
                with open(filestorage+"_log.txt", "a", encoding="utf-8") as i:
                    i.write("File Reuploaded as %s by %s at %s.\n"%(secure_filename(file_upload.filename),session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
                    i.close()
                os.replace(os.path.join(filestorage+"_log.txt"), os.path.join(filepath, (secure_filename(file_upload.filename)+"_log.txt")))
                return redirect(url_for("download_file", encfilestr=share_link_editor))
            return render_template("editspace.html", filename=filename, fileowner=fileowner, authority=authority, form = form, upload_files = upload_files, file = files[0], encfilestr = encfilestr, flag=session.pop('flag', 0), share_links=session.pop('share_links', None))
        
    else:
        return render_template("404.html")
    

@app.route('/download/<string:encfilestr>')
def download(encfilestr):
    cipher_share = Fernet(FILE_SHARE_KEY)
    filename, fileowner, _ = cipher_share.decrypt(encfilestr.encode()).decode().split("!!!!!")
    filepath = os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner, filename)
    with open(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', fileowner, filename)+"_log.txt", "a", encoding="utf-8") as i:
        i.write("File %s Downloaded by %s at %s.\n"%(filename, session['username'][:3]+"*"*(len(session['username'])-3), time.asctime()))
        i.close()
    return send_file(filepath, as_attachment=True)

@app.route('/filelogs', methods=['GET', 'POST'])
def filelogs():
    form = FileLogs()
    logs = None
    deletedlogs = None
    cipher_name = Fernet(FILE_NAME_KEY)
    if(os.path.exists(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username']))):
        logs = {}
        for i in os.listdir(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'])):
            if len(i)>8 and i[-8:]=='_log.txt':
                logs[i] = [cipher_name.encrypt((i+"!!!!!"+"Exists").encode()).decode(), "\n".join(open(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'], i)).readlines()[::-1])]
    if(os.path.exists(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'],'deleted-logs'))):
        deletedlogs = {}
        for i in os.listdir(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'],'deleted-logs')):
            if len(i)>8 and i[-8:]=='_log.txt':
                deletedlogs[i] = [cipher_name.encrypt((i+"!!!!!"+"Deleted").encode()).decode(), "\n".join(open(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'],'deleted-logs', i)).readlines()[::-1])]
    if form.validate_on_submit():
        FileName, Location = cipher_name.decrypt(form.Index.data).decode().split("!!!!!")
        if(Location == "Exists" and os.path.exists(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'], FileName))):
            return send_file(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'], FileName), as_attachment=True)
        elif(Location == "Deleted" and os.path.exists(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'],'deleted-logs', FileName))):
            return send_file(os.path.join(CURRENT_WORKING_DIRECTORY, 'files', session['username'],'deleted-logs', FileName), as_attachment=True)
    return render_template("accessfilelogs.html",form=form, logs=logs, deletedlogs=deletedlogs)
    
############################
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    ssl_context = (str(CURRENT_WORKING_DIRECTORY)+r'\Certificates\server.crt', str(CURRENT_WORKING_DIRECTORY)+r'\Certificates\server.key')
    app.run(debug=True, ssl_context=ssl_context, host="0.0.0.0")
