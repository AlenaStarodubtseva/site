from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO
from docx import Document
import os

# Flask app initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    period = db.Column(db.String(100), nullable=True)  # Добавили новое поле


# Route for the main student form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Получение данных из формы
        name = request.form.get('name')
        course_group = request.form.get('course_group')
        destination = request.form.get('destination')
        request_type = request.form.get('request_type')
        period = request.form.get('period') if request_type == "Справка с отметкой о стипендии" else None

        # Сохранение в базу данных
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

    # Если метод GET, отображаем форму
    return render_template("index.html")


# Admin view for handling requests
@app.route("/admin", methods=["GET"])
def admin():
    requests = Request.query.all()
    return render_template("admin.html", requests=requests)

# Route for generating Word document
@app.route("/generate/<int:request_id>", methods=["GET"])
def generate_doc(request_id):
    req = Request.query.get_or_404(request_id)
    
    # Create Word document
    doc = Document()
    doc.add_heading('Справка об обучении', level=1)
    doc.add_paragraph(f"ФИО: {req.name}")
    doc.add_paragraph(f"Группа: {req.group}")
    doc.add_paragraph(f"Тип справки: {req.request_type}")
    doc.add_paragraph("Подпись: ___________________")
    
    # Save to file-like object
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    # Return as downloadable file
    return send_file(file_stream, as_attachment=True, download_name=f"Справка_{req.name}.docx")

# Generate QR Code for student form
@app.route("/qrcode")
def generate_qr():
    # URL for the student form
    form_url = request.url_root.rstrip('/')  # Base URL (e.g., http://127.0.0.1:5000)
    form_url += "/"  # Ensure trailing slash
    
    # Generate QR Code
    qr = qrcode.make(form_url)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)

    # Return QR code image
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    # Ensure database exists
    if not os.path.exists("requests.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)

@app.route("/admin", methods=["GET"])
def admin():
    # Получаем все запросы из базы данных
    requests = Request.query.all()
    # Показываем страницу с запросами
    return render_template("admin.html", requests=requests)

