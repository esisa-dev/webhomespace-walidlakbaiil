import os
from flask import(
    Flask,
    request,
    render_template,
    redirect,
    session,
    url_for,
)
import zipfile
import shutil
from flask import safe_join,abort,send_file
#from werkzeug.security import safe_join
from pathlib import Path
from passlib.hash import sha512_crypt
from datetime import datetime
import hashlib
import datetime as dt
app=Flask(__name__,static_url_path='/static')
userG=""
baseFolder=""
@app.route('/')
def index():
    return render_template('signin.html')




@app.route('/',methods=['POST'])
def login():
    user = request.form['user']
    psswd = request.form['password']
    user1=os.popen(f"sudo cat /etc/shadow | grep {user}").read()
    os.popen(f"cd /home/{user}")
    psswd1=""
    with open('/etc/shadow', 'r') as f:
        for line in f:
            fields = line.split(':')
            if fields[0] == user:
                global userG
                userG=fields[0]
                global baseFolder
                baseFolder=f"/home/{fields[0]}"
                hashed_password = fields[1]
                if sha512_crypt.verify(psswd, hashed_password):
                    psswd1='ok'
                else : 
                     psswd1=""
   
    if(user1 != "" and psswd1=="ok"):
        response=app.make_response(render_template('Home.html'))
        return response
    else :
         return render_template('signin.html',error_auth='login or password incorrect')
    
@app.route('/files',methods=['POST'])
def files():
    
    value=os.popen(f" find /home/{userG} -type f | wc -l").read()
    return render_template('Home.html',value1=value)

@app.route('/dirs',methods=['POST'])
def dirs():
    value=os.popen(f" find /home/{userG} -type d | wc -l").read()
    return render_template('Home.html',value2=value)

@app.route('/space',methods=['POST'])
def space():
    value=os.popen(f"du -sh /home/{userG}").read()
    return render_template('Home.html',value3=value)

def getTimeStamp(tSec:float):
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj,'%Y-%m-%d %H:%M:%S')
    return tStr
def convert_size(size_bytes):
   
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    i = 0
    while size_bytes >= 1024 and i < len(suffixes) - 1:
        size_bytes /= 1024
        i += 1
    
    return f'{size_bytes:.2f} {suffixes[i]}'

@app.route('/index/',defaults={'reqPath':""})
@app.route('/index/<path:reqPath>')
def indesx(reqPath):
    global absPath
    absPath=safe_join(baseFolder,reqPath)
    if not os.path.exists(absPath):
        return abort(404)
    
    if os.path.isfile(absPath):
        return send_file(absPath)
    global objScan
    def objScan(x):
        fIcon = 'bi bi-folder-fill' if os.path.isdir(x.path) else "bi bi-file-earmark"
        filestate=x.stat()
        fBytes = convert_size(filestate.st_size)
        fTime = getTimeStamp(filestate.st_mtime)

        return {'name' : x.name, 'size' : fBytes , 'mTime' : fTime, 'fIcone' : fIcon, 'fLink' : os.path.relpath(x.path,baseFolder).replace("\\","/")}
    
    fNames = [objScan(x) for x in os.scandir(absPath)]
    parentPath = os.path.relpath(Path(absPath).parents[0],baseFolder).replace("\\","/")
    return render_template('Home.html',val=fNames,parentPath=parentPath)
@app.route('/download_home_directory')
def download_home_directory():
    home_directory = baseFolder
    temp_directory = shutil.make_archive('home_directory', 'zip', root_dir=home_directory)
    return send_file(temp_directory, as_attachment=True)
@app.route('/search',methods=['GET','POST'])
def search():
    keyword = request.form['keyword']
    result = ""
    for root, dir, files in os.walk(baseFolder):
      for f in files:
          if keyword.upper() in f.upper():
           result=os.path.join(root, keyword)
   
    parts = result.split("/")

    final = parts[3:-1]


    sin = "/".join(final)
    return redirect(f"/index/{sin}")

if __name__=='__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)