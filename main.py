from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'DB NAME GOES HERE'
app.config['MONGO_URI'] = 'DB URI GOES HERE'

mongo = PyMongo(app)

#main page to redirect
@app.route('/')
def index():
    if 'username' in session:
        return redirect('/home')
    else:
        return render_template('login.html')

# page to login
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

# page for registering 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')

@app.route('/home')
def home():
    user = session['username']
    return render_template('home.html', user=user)
    
@app.route('/about')
def about():
    user = session['username']
    return render_template('about.html', user=user)

# page for handling scheduling    
@app.route('/schedule', methods=['POST', 'GET'])
def schedule():
    user = session['username']
    users = mongo.db.users
    login_user = users.find_one({'name' : user})
    lens = 0
    for a in login_user:
        lens +=1
    print(lens)
    
    if request.method == 'POST':
        users.update({"name" : session['username']}, {"$set": {'full_name' : request.form['fname'], 'phone' : request.form['phone'], 'date' : request.form['dates'], 'time' : request.form['times'], 'employee' : request.form['emps']}})
        #if len(session) >= 6:
            
        session['full_name'] = request.form['fname']
        session['phone'] = request.form['phone']
        session['date'] = request.form['dates']
        session['time'] = request.form['times']
        session['employee'] = request.form['emps']

        return render_template('scheduled.html', user=user, name=session['full_name'], phone=session['phone'], date=session['date'], time=session['time'], emps=session['employee'])
        
    
    elif len(session) >= 7 or lens >= 8:
        
        session['full_name'] = login_user['full_name']
        session['phone'] = login_user['phone']
        session['date'] = login_user['date']
        session['time'] = login_user['time']
        session['employee'] = login_user['employee']
       
        return render_template('scheduled.html', user=user, name=session['full_name'], phone=session['phone'], date=session['date'], time=session['time'], emp=session['employee'])
    
    else:
        return render_template('schedule.html', user=user)

# page for logging out    
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)