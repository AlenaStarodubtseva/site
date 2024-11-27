from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime  # Для преобразования дат

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
    name = db.Column(db.String(200), nullable=False)
    course_group = db.Column(db.String(10), nullable=False)  # Формат: "1ИС"
    destination = db.Column(db.String(200), nullable=False)  # Куда нужна справка
    request_type = db.Column(db.String(200), nullable=False)  # Тип справки
    period_start = db.Column(db.String(50), nullable=True)  # Начало периода (если есть)
    period_end = db.Column(db.String(50), nullable=True)  # Конец периода (если есть)
    count = db.Column(db.Integer, nullable=False)  # Количество справок

# Главная страница с формой
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        course = request.form.get("course")
        group = request.form.get("group")
        course_group = f"{course}{group}"  # Форматируем как "1ИС"
        destination = request.form.get("destination")
        request_type = request.form.get("request_type")
        period_start = request.form.get("start_date")  # Дата начала периода
        period_end = request.form.get("end_date")  # Дата окончания периода
        count = int(request.form.get("count"))  # Количество справок

        # Проверяем ограничения для курса и группы
        if group in ["ИС", "МО", "ЭУ", "СПИ", "СПД"] and course > 4:
            return "Ошибка: Для выбранной группы курс не может быть больше 4."
        if group in ["МФМО", "МХПО"] and course > 2:
            return "Ошибка: Для выбранной группы курс не может быть больше 2."

        # Обрабатываем период
        if start_date and end_date:
            if start_date > end_date:
                return "Ошибка: Дата начала не может быть позже даты окончания."

            start_date_formatted = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            end_date_formatted = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            period = f"с {start_date_formatted} по {end_date_formatted}"
        else:
            period = None

        # Форматируем курс и группу
        course_group = f"{course}{group}"  # Например, "1ИС"

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
