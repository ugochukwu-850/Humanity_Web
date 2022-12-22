import os, random, sys, time

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required, apology
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime

from modules import filter


#configure application
app = Flask(__name__)

#ensure templates are auto reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#set file path
UPLOAD_FOLDER = "./static/uploads"
app.config['SECRET_KEY'] = "sorry"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///humanity.db")


#defaults requirements or stats
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" 
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    #if it was an uploading post process add the post text and the post path then return the template
    #with the new post
    
    if request.method == "POST":
        
        #get the post text from user if none reload page 
        post_text = request.form.get("Post")
        now = datetime.now()
        time = now.strftime("%m/%d/%Y, %H:%M:%S")
        print(time)
        if not post_text:
            return redirect("/")
         
        #get the file from the users if none save the var and reload the index page
        file = request.files["post_image"]
        
        #if the file is empty or missing 
        if not file or file.filename == '':
            if  session["user_id"]:
                print("yes es")
            #insert the text.time and user_id into the data base and set the path to None 
            db.execute("INSERT INTO posts (user_id, post, image_path,time) VALUES(?,?,?,?)", session["user_id"], post_text, None,time)
            
           #return back to view
            return redirect("/")
        #else if file  is present
        else:
            #start the checks 
            if file and allowed_file(file.filename):
                #get the filename
                filename = file.filename 
                id_name = filename.split('.')[0]
                #set the new name to the id plus the filetype
                new_id = db.execute("SELECT MAX(post_id)AS post_id FROM posts")
                if not new_id[0]["post_id"]:
                    new_id[0]["post_id"] = "1"
                else:
                    new_id[0]["post_id"] = str(new_id[0]["post_id"]) 
                filename = filename.replace(id_name,  new_id[0]["post_id"])
                
                #write a path to the file storage 
                path = f'/static/uploads/{filename}'
                print(session["user_id"])
                #now save the filepath and post text in the db
                db.execute("INSERT INTO posts (user_id, post, image_path,time) VALUES(?,?,?,?)", session["user_id"], post_text, path,time)
                
                #save the file in the right directory
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #redirect to veiw 
                return redirect("/")
            
    #get the files from the db and feed the index page after which you render it 
    data = db.execute("SELECT * FROM posts ORDER BY post_id DESC")
    if not data:
        return render_template("index.html", data=None, dp_path=None, username=None)
    for x in range(len(data)):
        print(data[0]["user_id"])    
    #get the username from users
    user_info = db.execute("SELECT * FROM users JOIN posts ON posts.user_id = users.id ORDER BY posts.post_id DESC")
    print(user_info)
    #since user info and data are both lists of dictionaries I would add the user_info to the the data 
    user_index = 0
    for value in data:
        value["username"] = user_info[user_index]["username"]
        print(value["username"])
        
        value["dp_path"] = user_info[user_index]["dp_path"]
        user_index += 1
    dp_paths = db.execute("SELECT dp_path FROM users WHERE id = ?", session["user_id"])
    dp_path = dp_paths[0]["dp_path"]
    #render the index page with correct vars
    return render_template("index.html", data=data,dp_path=dp_path)

#login A user 
@app.route("/login", methods=["POST", "GET"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
#succesfuk
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
#regsister a user and effectively log them in
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        # display the reistration form
        return render_template("register.html")
    elif request.method == "POST":
        # save variables to hold info for reg.

        username = request.form.get("username")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        nickname = request.form.get("nickname")
        quote = request.form.get("quote")
        email = request.form.get("address")
        check_password = request.form.get("confirm")
        check_username = db.execute(
            "SELECT username FROM users WHERE username = ?", username)

        print("i successfully gor users input")
        # check that the values are correct

        # check the fields are filled
        if len(username) < 1 or len(password) < 1 or len(check_password) < 1:
            print("successful check for pass")
            return apology("Fill all the fields", 400)
            
        # check that the username is not in the database
        elif len(check_username) == 1:
            print("successful check for pass")
            return apology("Your user name seems to have been taking", 400)
        # check the password mathces with the confirmation
        elif password != check_password:
            print("successful check for pass")
            return apology("Password does not match")
        # value check succesful
        print("successful check for pass")
        # save variable for adding into the database

        # create a hash for the  password
        hash_pass = generate_password_hash(password)
        #work the file control
            
        # check if the post request has the file part
        #if 'file' not in request.files:
         #   print("no file part")
          #  flash('No file part')
           # return redirect("/register")
        
        
        file = request.files['profilepic']
        
        if file.filename == '':
            flash('No selected file')
            return redirect("/register")
        if file and allowed_file(file.filename):
            filename = file.filename 
            id_name = filename.split('.')[0]
            picusername = username + "profile"
            
            filename = filename.replace(id_name, picusername)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = f'/static/uploads/{filename}'
            
            
            
        
            file2 = request.files['coverpic']
            
            if file2 and allowed_file(file2.filename):
                filename2 = file2.filename 
                id_name2 = filename2.split('.')[0]
                y = username + "cover"

                filename2 = filename2.replace(id_name2, y)
                path2 = f'/static/uploads/{filename2}'
                

                file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
                
                
        #done
        
        # insert user into the database
        db.execute("INSERT INTO users (username, hash,name, quote,email,coverphoto_path, dp_path) VALUES(?,?,?,?,?,?,?)", username, hash_pass, fullname, quote,email, path2, path)
        # insert user into the database
        user_id = db.execute(
            "SELECT id AS id FROM users WHERE username = ?", username)
        # variable savesuccesful

        # log user in
        session["user_id"] = user_id[0]["id"]
        # done set ting user to session
        return redirect("/")

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/profile")
@login_required
def profile():
    #when called get the neccesary variables from user in session
    dataf = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    
    #assign the, to variabes for easy accesibility
    name = dataf[0]["name"]
    username = dataf[0]["username"]
    email = dataf[0]["email"]
    quote = dataf[0]["quote"]
    dp_path = dataf[0]["dp_path"]
    coverphoto_path = dataf[0]["coverphoto_path"]
    
    #Get post from that user     
    data = db.execute("SELECT * FROM posts WHERE user_id = ?", session["user_id"])
    
    #if there areno posts as such 
    if not data:
        #return the neccesary profile info and in jinja send a message for your all set up
        return render_template("profile.html", name=name,username=username, email=email, quote=quote, dp_path=dp_path, cp_path=coverphoto_path)
    
    #else get users name and dp_path just for redundancy sake
    user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    
    #add it to the data list 
    for value in data:
        value["username"] = user_info[0]["username"]
        value["dp_path"] = user_info[0]["dp_path"]
    #render the template with the data_list
    return render_template("profile.html", data=data,  name=name,username=username, email=email, quote=quote, dp_path=dp_path, cp_path=coverphoto_path)

@app.route("/notifications")
@login_required
def notifications():
    return render_template("notifications.html")


@app.route("/interest")
@login_required
def interest():
    return render_template("interest.html")

@app.route("/notes")
@login_required
def notes():
    return render_template("notes.html")

@app.route("/messages")
@login_required
def messages():
    return render_template("messages.html")



if __name__ == "__main__":
    app.run(debug=True)
