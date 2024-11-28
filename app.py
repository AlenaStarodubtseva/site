from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from docx import Document
import pytz
import datetime
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.shared import RGBColor


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///requests.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
timezone = pytz.timezone("Asia/Tokyo")
current_time = datetime.datetime.now(timezone).strftime('%d.%m.%Y')
# Модель данных
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_group = db.Column(db.String(20), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Главная страница (заявка)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        course = int(request.form["course"])
        group = request.form.get("group")
        destination = request.form.get("destination")
        request_type = request.form.get("request_type")
        quantity = int(request.form["quantity"])
        period_start = request.form.get("period_start")
        period_end = request.form.get("period_end")

            
        # Проверка на тип справки
        if request_type == "Справка с отметкой о стипендии" and (not period_start or not period_end):
            flash("Пожалуйста, укажите период для справки с отметкой о стипендии.")
            return redirect("/")

        # Проверка курсов для групп
        if group in ["МФМО", "МХПО"] and course > 2:
            flash("Группы МФМО и МХПО не могут быть на курсе больше 2.", "error")
            return redirect(url_for("index"))

        if group in ["МО", "ИС", "ЭУ", "СПД", "СПИ"] and course > 4:
            flash("Группы МО, ИС, ЭУ, СПД, СПИ не могут быть на курсе больше 4.", "error")
            return redirect(url_for("index"))

        # Проверка периода
        if period_start and period_end and period_start > period_end:
            flash("Начальная дата не может быть позже конечной.", "error")
            return redirect(url_for("index"))

        # Проверка количества справок
        if quantity < 1:
            flash("Количество справок должно быть не меньше 1.", "error")
            return redirect(url_for("index"))
        
        # Создание новой заявки
        new_request = Request(
            name=name,
            course_group=f"{course}{group}",
            destination=destination,
            request_type=request_type,
            quantity=quantity,
            period_start=datetime.datetime.strptime(period_start, "%Y-%m-%d") if period_start else None,
            period_end=datetime.datetime.strptime(period_end, "%Y-%m-%d") if period_end else None,
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Заявка успешно отправлена!")
        return redirect("/")
    return render_template("index.html")


# Админ-панель
@app.route("/admin")
def admin():
    requests_with_stipend = Request.query.filter_by(request_type="Справка с отметкой о стипендии").all()
    requests_without_stipend = Request.query.filter_by(request_type="Справка без отметки о стипендии").all()
    return render_template("admin.html", requests_with_stipend=requests_with_stipend, requests_without_stipend=requests_without_stipend)

# Удаление заявок
@app.route("/delete", methods=["POST"])
def delete():
    ids_to_delete = request.form.getlist("delete_ids")
    for request_id in ids_to_delete:
        request_to_delete = Request.query.get(request_id)
        db.session.delete(request_to_delete)
    db.session.commit()
    flash("Выбранные заявки удалены.")
    return redirect("/admin")

@app.route('/handle-requests', methods=['POST'])
def handle_requests():
    selected_ids = request.form.getlist('request_ids')  # Получаем выбранные ID заявок
    action = request.form.get('action')  # Получаем значение action

    if action == "delete":
        # Удаление заявок из базы данных
        for request_id in selected_ids:
            request_to_delete = Request.query.get(request_id)
            if request_to_delete:
                db.session.delete(request_to_delete)
        db.session.commit()
        flash("Выбранные заявки успешно удалены", "success")
        return redirect(url_for('admin'))

    elif action == "generate":
        # Генерация общего документа
        selected_requests = Request.query.filter(Request.id.in_(selected_ids)).all()
        doc = Document()
        
        # Установка шрифта для всего документа
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(11)
        
        # Заголовок документа
        title = doc.add_heading(level=1)
        run = title.add_run(f"Заявка на справки {datetime.datetime.now().strftime('%d.%m.%Y')} факультета физико-математического образования и технологии")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0, 0, 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Создание таблицы
        table = doc.add_table(rows=1, cols=5)  # Заголовки таблицы
        table.style = 'Table Grid'
        
        # Добавление заголовков
        hdr_cells = table.rows[0].cells
        hdr_titles = ["Ф.И.О.", "Курс, группа", "Куда", "Сколько", "Примечание"]
        for idx, cell in enumerate(hdr_cells):
            cell.text = hdr_titles[idx]
            cell.paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            cell.paragraphs[0].runs[0].font.size = Pt(11)
            cell.paragraphs[0].runs[0].font.name = 'Times New Roman'

        # Установка стиля заголовков таблицы
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                run = paragraph.runs[0]
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            
        # Заполнение таблицы данными
        for req in selected_requests:
            row_cells = table.add_row().cells
            row_cells[0].text = req.name
            row_cells[1].text = req.course_group
            row_cells[2].text = req.destination
            row_cells[3].text = str(req.quantity)

        # Добавление примечания для справки с отметкой о стипендии
            if req.request_type == "Справка с отметкой о стипендии":
                row_cells[4].text = f"{req.period_start.strftime('%d.%m.%Y')} – {req.period_end.strftime('%d.%m.%Y')}"
            else:
                row_cells[4].text = "-"

        # Форматирование текста в каждой ячейке строки
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    
        # Сохранение документа во временный файл
        temp_file = BytesIO()
        doc.save(temp_file)
        temp_file.seek(0)

        return send_file(
            temp_file,
            as_attachment=True,
            download_name="Общий_документ.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    else:
        flash("Неизвестное действие", "error")
        return redirect(url_for('admin'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
