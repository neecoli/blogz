from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'blogz'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

#add a User class   
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'display_mainblog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#LOGIN---------------
@app.route ('/login', methods=['POST', 'GET'])
#User enters a username that is stored in the database with the correct password and is redirected to the /newpost 
#page with their username being stored in a session.
#User enters a username that is stored in the database with an incorrect password and is redirected to the /login 
#page with a message that their password is incorrect.
#User tries to login with a username that is not stored in the database and is redirected to the /login page 
#with a message that this username does not exist.
#User does not have an account and clicks "Create Account" and is directed to the /signup page.

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and user.password != password:
            flash("User password incorrect", "error")
            return redirect('/login')
        elif not user:
            flash('User does not exist', "error")
            return redirect('/login')
        
    return render_template('login.html')
 

#SIGNUP--------------
@app.route ('/signup', methods=['POST', 'GET'])
#User enters new, valid username, a valid password, and verifies password correctly and is redirected to the
#  '/newpost' page with their username being stored in a session.
#User leaves any of the username, password, or verify fields blank and gets an error message that one or more
# fields are invalid.
#User enters a username that already exists and gets an error message that username already exists.
#User enters different strings into the password and verify fields and gets an error message that the 
#passwords do not match.
#User enters a password or username less than 3 characters long and gets either an invalid username or an
#  invalid password message.

def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']

        # TODO - validate user's data

        if (len(username) < 3):
            flash("That's not a valid username", "error")
            return redirect('/signup')
            
        if (len(password) < 3):
            flash("That's not a valid password", "error")
            return redirect('/signup')
    
        if password != verifypassword:
            flash("Passwords don't match", "error")
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - user is duplicate
            return "<h1>Duplicate user</h1>"

   
    return render_template('signup.html')


#HOME----------------------
#The / route displays a Home page list of the usernames for all the authors on the site
#If click on individual user, display blogs for that user
@app.route('/', methods=['POST', 'GET'])
def index():
    
    if 'user' in request.args:
        user = User.query.filter_by(username=session['username']).first()
        #user_id = request.args.get('user')
        #user = User.query.get(user_id)
        userblogs = Blog.query.filter_by(owner=user).all()     
        return render_template('singleUser.html', user=user)

    users = User.query.all()
    return render_template('index.html', users=users)


#ALL POSTS---------------------
#The /blog route displays all the main blog posts.
@app.route('/blog', methods=['POST', 'GET'])
def display_mainblog():
    
    #if user clicks on blog, redirect to individual blog page
    #query db for the blog entry

    """
    try:
        request.args['id']
    except:
        pass
    else:
        blog_id = request.args['id']
        blog = Blog.query.get(blog_id)
        return render_template('individualblog.html', blogname=blog.title, blogentry=blog.body)
    """

    if 'id' in request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
            
        return render_template('individualblog.html', blogname=blog.title, blogentry=blog.body)


      
    if 'user' in request.args:
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        #userblogs = Blog.query.filter_by(owner_id=user_id).all()     
        return render_template('singleUser.html', user=user)
       

    """    
    try:
        request.args['user']
    except:
        pass
    else:
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        #userblogs = Blog.query.filter_by(owner_id=user_id).all()     
        return render_template('singleUser.html', user=user)
    """

    blogs = Blog.query.all()
    return render_template('mainblog.html', blogs=blogs)

    """Todo: generate singleUser.html page using GET request with a user
    query parameter (similar to how we dynamically generated individual blog entry pages)"""


#NEWPOST------------------
#submit a new post at the /newpost route; after submitting new post
#app displays main blog page
#After logging out, unable to access /newpost page (is redirected to /login page instead).
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if 'username' not in session:
        return redirect ('/login')

    if request.method == 'GET':
        return render_template('addblog.html')
    
    blogname = request.form['title']
    blogentry = request.form['body']
    #blogowner = # take username from session here to get ID from db then thats the blogowner ID
    blogowner = User.query.filter_by(username=session['username']).first()
    #blogowner = User.query.filter_by(owner_id=user_id).first()

    new_blog = Blog(blogname, blogentry, blogowner)
    db.session.add(new_blog)
    db.session.commit()
    
    titleerror = ''
    entryerror = ''

    if (not blogname) or (blogname.strip() == ""):
        titleerror = "Enter a Title"
        
    if (not blogentry) or (blogentry.strip() == ""):
        entryerror = "Enter a blog"
    
    if not titleerror and not entryerror:
        #after adding post, go to individual post page
        return render_template('individualblog.html', blogname=blogname, blogentry=blogentry)
        #return render_template('mainblog.html', blogs=blogs)
    else:
        return render_template('addblog.html', titleerror=titleerror, entryerror=entryerror)
        #return redirect("/?error=" + error)


#LOGOUT-------------
#redirects the user to /blog after deleting the username from the session
#After logging out, unable to access /newpost page (is redirected to /login page instead).
@app.route ('/logout',methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()