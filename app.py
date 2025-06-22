from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os, json

app = Flask(__name__)
app.secret_key = 'your-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "hcen123":
            user = User("admin")
            login_user(user)
            return redirect(url_for("admin"))
        return "Invalid login"
    return '''
        <form method="post">
            <input name="username" placeholder="Username">
            <input name="password" placeholder="Password" type="password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
def index():
    approved = json.load(open("data.json", "r")) if os.path.exists("data.json") else []
    return render_template("index.html", entries=[e for e in approved if e.get("approved")])

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        entry = dict(request.form)
        entry["approved"] = False
        data = json.load(open("data.json", "r")) if os.path.exists("data.json") else []
        data.append(entry)
        json.dump(data, open("data.json", "w"), indent=2)
        return redirect("/")
    return render_template("submit.html")

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    data = json.load(open("data.json", "r")) if os.path.exists("data.json") else []
    if request.method == "POST":
        for i, d in enumerate(data):
            if str(i) in request.form:
                d["approved"] = True
        json.dump(data, open("data.json", "w"), indent=2)
        return redirect("/admin")
    return render_template("admin.html", entries=data)

@app.route("/export")
@login_required
def export():
    import csv
    from io import StringIO
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["name", "phone", "car_color", "car_type", "model", "appearance", "report", "approved"])
    writer.writeheader()
    for entry in json.load(open("data.json")):
        writer.writerow(entry)
    return output.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment;filename=reports.csv'}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
