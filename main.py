from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String)
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost')
def new_post():
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def validation():
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
            new_entry = Blog(blog_title, blog_body)
            db.session.add(new_entry)
            db.session.commit()
            id_query = Blog.query.all()
            for i in id_query:
                last_id = i.id
            blog_id = last_id
            return redirect('/blog?id={0}'.format(blog_id))

@app.route('/blog', methods=['POST', 'GET'])
def template():
    if request.method == 'GET':
        id = request.args.get('id')
        if id:
            #id = int(id)
            contents = Blog.query.filter_by(id=id).all()
            return render_template('template.html', contents = contents)
        else:
            entry_list = Blog.query.all()
            return render_template('blog.html', entry_list=entry_list)


if __name__ == '__main__':
    app.run()