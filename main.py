from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(60))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    bloggers = User.query.all()
    return render_template('index.html', bloggers=bloggers)

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        correct_password = User.query.filter_by(password=password).first()

        if existing_user and not correct_password:
            flash(username + ", input password is incorrect")
            return redirect('/login')
    
        if not existing_user:
            flash("selected username doesn't exist")
            return redirect('/login')
        
        elif existing_user and existing_user.password == password:
            session['username'] = username
            return redirect('/newpost')

    else:
        return render_template('/login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username=="" or password=="" or verify=="":
            flash("uncompleted input")
            return redirect('/signup')
            
        if existing_user:
            flash("username already exist")
            return redirect('/signup')

        if password != verify:
            flash("passwords do not match")
            return redirect('/signup')

        if len(username)<3 or len(password)<3:
            flash("inputs must be longer the two characters")
            return redirect('/signup') 

        elif not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    else:
        return render_template('signup.html')

@app.route('/newpost')
def new_post():
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def validation():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']

        title_error = "Please fill in the title"
        body_error = "Please fill in the body"
        if not blog_title and not blog_body:
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        if not blog_title and blog_body:
            return render_template('newpost.html', title_error=title_error)
        if blog_title and not blog_body:
            return render_template('newpost.html', body_error=body_error)
        else:
            new_entry = Blog(blog_title, blog_body, owner)
            db.session.add(new_entry)
            db.session.commit()
            id_query = Blog.query.all()
            for i in id_query:
                last_id = i.id
            blog_id = last_id
            return redirect('/blog?id={0}'.format(blog_id))

@app.route('/blog', methods=['POST', 'GET'])
def list_blog():

    if request.method == 'GET':
        id = request.args.get('id')
        username = request.args.get('user')
        

        if id:
            #id = int(id)
            contents = Blog.query.filter_by(id=id).all()
            bloggers = User.query.all()
            return render_template('template.html', contents=contents, bloggers=bloggers)

        if username:
            users = User.query.filter_by(username=username).first()
            entry_list = Blog.query.filter_by(owner_id=users.id).all()
            bloggers = User.query.all()
            return render_template('blog.html', entry_list=entry_list, bloggers=bloggers)

        else:
            entry_list = Blog.query.all()
            bloggers = User.query.all()
            return render_template('blog.html', entry_list=entry_list, bloggers=bloggers)

app.secret_key = "blablablablaaa"
if __name__ == '__main__':
    app.run()