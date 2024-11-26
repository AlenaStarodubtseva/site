from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель базы данных
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    course_group = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(200), nullable=False)
    period_start = db.Column(db.String(50), nullable=True)
    period_end = db.Column(db.String(50), nullable=True)
    count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Не выполнено")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        course = request.form.get("course")
        group = request.form.get("group")
        course_group = f"{course}{group}"
        destination = request.form.get("destination")
        request_type = request.form.get("request_type")
        count = int(request.form.get("count"))
        period_start = request.form.get("start_date") if request_type == "Справка с отметкой о стипендии" else None
        period_end = request.form.get("end_date") if request_type == "Справка с отметкой о стипендии" else None

        # Проверка правильности данных
        if group in ["МФМО", "МХПО"] and int(course) > 2:
            flash("Группы МФМО и МХПО не могут быть старше 2 курса!")
            return redirect(url_for('index'))
        elif group in ["ИС", "МО", "ЭУ", "СПИ", "СПД"] and int(course) > 4:
            flash("Эта группа не может быть старше 4 курса!")
            return redirect(url_for('index'))

        # Создание новой заявки
        new_request = Request(
            name=name,
            course_group=course_group,
            destination=destination,
            request_type=request_type,
            period_start=period_start,
            period_end=period_end,
            count=count
        )
        db.session.add(new_request)
        db.session.commit()

        flash("Заявка успешно подана!")
        return redirect(url_for('index'))

    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if "complete" in request.form:
            completed_ids = request.form.getlist("completed")
            for request_id in completed_ids:
                req = Request.query.get(request_id)
                req.status = "Выполнено"
                db.session.commit()
        elif "delete" in request.form:
            selected_ids = request.form.getlist("selected")
            for request_id in selected_ids:
                req = Request.query.get(request_id)
                db.session.delete(req)
                db.session.commit()
        elif "archive" in request.form:
            selected_ids = request.form.getlist("selected")
            for request_id in selected_ids:
                req = Request.query.get(request_id)
                db.session.delete(req)
                db.session.commit()
        elif "generate" in request.form:
            selected_ids = request.form.getlist("selected")
            flash(f"Сформирован общий документ для {len(selected_ids)} заявок.")
            return redirect(url_for('admin'))

    requests_without_stipend = Request.query.filter_by(request_type="Справка без отметки о стипендии").all()
    requests_with_stipend = Request.query.filter_by(request_type="Справка с отметкой о стипендии").all()
    return render_template(
        "admin.html",
        requests_without_stipend=requests_without_stipend,
        requests_with_stipend=requests_with_stipend
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

