from flask import Flask,render_template,url_for,flash,redirect,request
from forms import RegistrationForm,LoginForm,ContactForm,UpdateAccountForm,PostForm
from flask_sqlalchemy import SQLAlchemy ##trying another DS
from datetime import datetime,timedelta
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user   ,current_user ,logout_user ,login_required           
import secrets               
import os   ###
from PIL import Image

from dateutil import parser


app = Flask(__name__)

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="mysql",
  database="project"
)
mycursor = mydb.cursor()


app.config['SECRET_KEY']='b0a26ce6fb663a3d7f006e020de17a9e'  #secret key for protection


login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

@login_manager.user_loader
def load_user(user_id):
   return New3User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)


class New3User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False,nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    phonenumber = db.Column(db.String(60),unique=True, nullable=False)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}','{self.phonenumber}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('new3_user.id'), nullable=False)
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


db.create_all()

Post.query.filter_by(id=12348).delete()
db.session.commit()
posts = [
    {
        'author': 'Group 1',
        'title': 'Social Media Site',
        'content': 'www.facebook.com',
        'date_posted': 'Feb 6, 2021'
    }
]


@app.route('/')
@app.route('/home')
def home():
     posts = Post.query.all()
     return render_template('home.html', posts=posts)


@app.route("/social")
def social():
    return render_template('social.html', posts=posts)

@app.route('/review')
def review():
     posts = Post.query.all()
     return render_template('review.html', posts=posts)


@app.route('/about')
def about():
   return render_template('About.html')

@app.route('/register', methods=['GET','POST'])
def register():


   if current_user.is_authenticated:
      return redirect(url_for('home'))


   form=RegistrationForm()



   if form.validate_on_submit():
          

         
         if request.method =="POST":   #if data is correct go back to home not same page
           user=New3User(username=form.username.data,email=form.email.data,password=form.password.data,phonenumber=form.phonenumber.data)
           db.session.add(user)
           db.session.commit()
           username = request.form["username"]
           email = request.form["email"]
           password = request.form["password"]
           phonenumber=request.form["phonenumber"]
           sql= "SELECT email FROM user WHERE email= %s "
           val=(email,)
           cursor = mydb.cursor(buffered=True)

           mycursor.execute(sql, val)
           myresult=mycursor.fetchone()
           if myresult!=None:
               flash(f'Email is used before') 
               return redirect(url_for('register'))
           else :
               flash(f'Account Created for Mr/Ms {form.username.data}! now you can login','success')
               sql = "INSERT INTO user (username,email,password,phonenumber) VALUES (%s, %s, %s,%s)"
               val = (username,email,password,phonenumber)
               cursor = mydb.cursor(buffered=True)

               mycursor.execute(sql, val)
               mydb.commit()
               print(username,email,password,phonenumber)   
         return redirect(url_for('login'))

         user=New3User(username=form.username.data,email=form.email.data,password=form.password.data,phonenumber=form.phonenumber.data)
         db.session.add(user)
         db.session.commit()
           #if data is correct go back to home not same page
      
     


       
   return render_template('register.html',title='Register',form=form)



@app.route('/login', methods=['GET','POST'] )
def login():
   if current_user.is_authenticated:
      return redirect(url_for('home'))
   form=LoginForm()
   if form.validate_on_submit():
     

         if request.method =="POST":  
           email = request.form["email"]
           password = request.form["password"]
           sql= "SELECT email , password FROM user WHERE email= %s and password = %s "
           val=(email,password)
           mycursor.execute(sql, val)
           myresult=mycursor.fetchone()
           print(myresult)
           
           if myresult==None:
             flash(f'Incorrect email/password!','success') 
             return render_template('login.html',title='login',form=form)  
                        
         user=New3User.query.filter_by(email=form.email.data).first()
         if user is None:
            flash(f'Incorrect email/password!','success')                           ###########################
            return render_template('login.html',title='login',form=form)  

         login_user(user)  

              

         return redirect(url_for('home'))

     
      


         
 
 
 
   return render_template('login.html',title='Register',form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
 
  if request.method == 'POST':
    
    username = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]
    sql = "INSERT INTO contact_us (username,email,subject,message) VALUES (%s, %s, %s,%s)"
    val = (username,email,subject,message)
    mycursor.execute(sql, val)
    mydb.commit()
    print(username,email,subject,message)   
    flash(f'Form posted ! , We are happy to hear from you !')    
    return redirect(url_for('contact'))
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/viewContact')

def viewC():
   if current_user.is_authenticated:

      mycursor.execute("SELECT * FROM contact_us")
      row_headers=[x[0] for x in mycursor.description] 
      myresult = mycursor.fetchall()
      for x in myresult:
         print(x)
      return render_template('viewContact.html',viewC=myresult)    
   else :
      form=LoginForm()
      return render_template('login.html',title='login',form=form)     




@app.route('/avilablegroups')
def avilablegroups():
      mycursor.execute("SELECT * FROM fundgroup")
      row_headers=[x[0] for x in mycursor.description] 
      myresult = mycursor.fetchall()
      for x in myresult:
         print(x)
      return render_template('avilablegroups.html',avilablegroups=myresult)



@app.route('/avilablegroups2')
def avilablegroups2():
      mycursor.execute("SELECT * FROM fundinggroup20$")
      row_headers=[x[0] for x in mycursor.description] 
      myresult = mycursor.fetchall()
      for x in myresult:
         print(x)
      return render_template('avilablegroups2.html',avilablegroups2=myresult)


@app.route('/addGroup', methods=['GET', 'POST'])
def add():
      
      if request.method=="POST":
         name = request.form["Name"]
         phone = request.form["phone"]
         turn= request.form["turn"]
         monthly=request.form["monthlypay"]
         id=request.form["ID"]
         City=request.form["City"]
     #    user=User(username=username,phone=phone,turn=turn,monthlypay=monthlypay)

      #   db.session.add(user)
   #      db.session.commit()
         turn = request.form["turn"]
         sql = "INSERT INTO fundGroup (name,phone,turn,monthly,id,City) VALUES (%s, %s,%s, %s,%s,%s)"
         val = (name,phone,turn,monthly,id,City)
         cursor = mydb.cursor(buffered=True)

         mycursor.execute(sql, val)
         mydb.commit()
         flash(f'Group is succesfully added !')    
         return redirect(url_for('home')) 
      else:
         return render_template('addGroup.html') 



@app.route('/addd', methods=['GET', 'POST'])
def addd():
      
   
      if request.method=="POST":
         name = request.form["Name"]
         phone = request.form["phone"]
         turn= request.form["turn"]
         monthly=request.form["monthlypay"]
         
         turn = request.form["turn"]
         City=request.form["City"]
         sql = "INSERT INTO fundGroup (name,phone,turn,monthly,City) VALUES (%s, %s,%s, %s,%s)"
         val = (name,phone,turn,monthly,City)
         mycursor.execute(sql, val)
         mydb.commit()
         flash(f'User is succesfully added !')    
         return redirect(url_for('avilablegroups2'))
    
      else:
         return render_template('addMember.html') 
  
@app.route('/avilable',methods=['GET','POST'])
def avilable():
   return render_template('available.html')


@app.route('/addMember', methods=['GET', 'POST'])
def addP():
   

      if request.method=="POST":
         name = request.form["Name"]
         phone = request.form["phone"]
         turn= request.form["turn"]
         monthly=request.form["monthlypay"]
         id=request.form["ID"]
         City=request.form["City"]

         turn = request.form["turn"]
         sql = "INSERT INTO fundGroup (name,phone,turn,monthly,id,City) VALUES (%s, %s,%s, %s,%s,%s)"
         val = (name,phone,turn,monthly,id,City)
         mycursor.execute(sql, val)
         mydb.commit()
         flash(f'User is succesfully added !')    
         return redirect(url_for('avilablegroups'))
    
      else:
         return render_template('addMember.html') 
               

@app.route('/addMember2', methods=['GET', 'POST'])
def addP2():
   

      if request.method=="POST":
         name = request.form["Name"]
         phone = request.form["phone"]
         turn= request.form["turn"]
         monthly=request.form["monthlypay"]
         id=request.form["ID"]
         City=request.form["City"]
         turn = request.form["turn"]
         sql = "INSERT INTO fundinggroup20$ (name,phone,turn,payment,id,City) VALUES (%s, %s,%s, %s,%s,%s)"
         val = (name,phone,turn,monthly,id,City)
         mycursor.execute(sql, val)
         mydb.commit()
         flash(f'User is succesfully added !')    
         return redirect(url_for('avilablegroups2'))
    
      else:
         return render_template('addGroup.html') 
               


 
@app.route('/admin')
def admin():
    if current_user.is_authenticated:  
       return render_template('admin.html')
    else:
       form=LoginForm()
       return render_template('login.html',title='login',form=form)  



@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for('home'))



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path) 

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)







@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))



if __name__ == '__main__':
   app.run(debug=True)


 