"""Feedback application"""

from flask import Flask, redirect, render_template, session
from models import db, connect_db, User, Feedback
from keys import FLASK_SECRET_KEY
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

#Debug Toolbar still buggy in new version

"""Call connect to database """
connect_db(app)
app.app_context().push()
db.create_all()

"""User routes"""

@app.route("/")
def homepage():
    """Homepage and redirect to register."""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration"""

    form = RegisterForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name) 

        db.session.commit()
        session["username"]= user.username

        return redirect(f"/users/{user.username}")
    
    else:
    
        return render_template("/users/register.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Login an existing user"""

    form = LoginForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password) 
        if user:
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password."]
            return render_template("users/login.html", form=form)

    return render_template("users/login.html", form=form)

@app.route("/logout")
def logout():
    """Logging out a User"""

    session.pop("username")
    return redirect("/")

@app.route("/users/<username>")
def show_user(username):
    """Information Page User"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template("users/show.html", user=user, form=form)


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def adding_feedback(username):
    """Existing user adding a feedback"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
    
        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{username}")
    
    else:
        return render_template("feedbacks/add.html", form=form)
    

@app.route("/users/<username>/delete", methods=["POST"])
def deleting_user(username):
    """Delete user"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def updating_feedback(feedback_id):
    """Update Feedback"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedbacks/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def deleting_feedback(feedback_id):
    """Delete feedback"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm() #taken this approach from the solution as I only made it happen without validation

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
    

