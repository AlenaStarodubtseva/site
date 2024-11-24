from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Инициализация приложения
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'  # Настройка базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модель базы данных
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    period = db.Column(db.String(100), nullable=True)  # Поле для справок с периодом

# Главная страница с формой
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получаем данные из формы
        name = request.form.get('name')
        course_group = request.form.get('course_group')
        destination = request.form.get('destination')
        request_type = request.form.get('request_type')
        period = request.form.get('period') if request_type == "Справка с отметкой о стипендии" else None

        # Сохраняем данные в базе
        new_request = Request(
            name=name,
            group=course_group,
            request_type=request_type,
            destination=destination,
            period=period
        )
        db.session.add(new_request)
        db.session.commit()
        return "Ваш запрос успешно отправлен!"

    return render_template("index.html")

# Админ-панель для просмотра запросов
@app.route("/admin", methods=["GET"])
def admin():
    requests = Request.query.all()
    return render_template("admin.html", requests=requests)

if __name__ == "__main__":
    app.run(debug=True)
