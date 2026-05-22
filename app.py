import os
import calendar
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Expense, Note, Todo
from datetime import datetime, date
from sqlalchemy import extract
from dotenv import load_dotenv

load_dotenv(override=False)  # real env vars (Railway) always win over .env file

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL')  # None if truly absent
if database_url:
    # Railway (and some older Heroku/Postgres providers) emit postgres:// which
    # SQLAlchemy 1.4+ rejects; replace only the scheme, leave the rest intact.
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
else:
    database_url = 'sqlite:///daily.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/init-db')
def init_db():
    db.create_all()
    return 'Database initialized successfully!'


@app.route('/')
def index():
    tab = request.args.get('tab', 'gastos')
    today = date.today()

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    monthly_expenses = Expense.query.filter(
        extract('month', Expense.date) == today.month,
        extract('year', Expense.date) == today.year
    ).all()
    monthly_total = sum(e.amount for e in monthly_expenses)

    notes = Note.query.order_by(Note.date.desc()).all()
    todos = Todo.query.order_by(Todo.date.desc()).all()

    return render_template('index.html',
                           tab=tab,
                           expenses=expenses,
                           monthly_total=monthly_total,
                           notes=notes,
                           todos=todos,
                           today=today)


# ── Expense routes ─────────────────────────────────────────────────────────────

@app.route('/expenses/add', methods=['POST'])
def add_expense():
    expense = Expense(
        amount=float(request.form['amount']),
        category=request.form['category'],
        description=request.form.get('description', ''),
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    )
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for('index', tab='gastos'))


@app.route('/expenses/<int:id>/edit', methods=['POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    expense.amount = float(request.form['amount'])
    expense.category = request.form['category']
    expense.description = request.form.get('description', '')
    expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    db.session.commit()
    return redirect(url_for('index', tab='gastos'))


@app.route('/expenses/<int:id>/delete', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index', tab='gastos'))


# ── Note routes ────────────────────────────────────────────────────────────────

@app.route('/notes/add', methods=['POST'])
def add_note():
    note = Note(
        title=request.form['title'],
        content=request.form['content'],
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    )
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('index', tab='notas'))


@app.route('/notes/<int:id>/edit', methods=['POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    note.title = request.form['title']
    note.content = request.form['content']
    note.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    db.session.commit()
    return redirect(url_for('index', tab='notas'))


@app.route('/notes/<int:id>/delete', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('index', tab='notas'))


# ── Todo routes ────────────────────────────────────────────────────────────────

@app.route('/todos/add', methods=['POST'])
def add_todo():
    todo = Todo(
        task=request.form['task'],
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
        done=False
    )
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index', tab='todo'))


@app.route('/todos/<int:id>/toggle', methods=['POST'])
def toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for('index', tab='todo'))


@app.route('/todos/<int:id>/edit', methods=['POST'])
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.task = request.form['task']
    todo.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    db.session.commit()
    return redirect(url_for('index', tab='todo'))


@app.route('/todos/<int:id>/delete', methods=['POST'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index', tab='todo'))


# ── Calendar API ───────────────────────────────────────────────────────────────

@app.route('/api/calendar/<int:year>/<int:month>')
def calendar_data(year, month):
    _, days_in_month = calendar.monthrange(year, month)
    start = date(year, month, 1)
    end = date(year, month, days_in_month)

    expenses = Expense.query.filter(Expense.date >= start, Expense.date <= end).all()
    notes = Note.query.filter(Note.date >= start, Note.date <= end).all()
    todos = Todo.query.filter(Todo.date >= start, Todo.date <= end).all()

    data = {}

    for e in expenses:
        key = str(e.date)
        data.setdefault(key, {'expenses': [], 'notes': [], 'todos': []})
        data[key]['expenses'].append({
            'id': e.id, 'amount': e.amount,
            'category': e.category, 'description': e.description
        })

    for n in notes:
        key = str(n.date)
        data.setdefault(key, {'expenses': [], 'notes': [], 'todos': []})
        data[key]['notes'].append({
            'id': n.id, 'title': n.title, 'content': n.content
        })

    for t in todos:
        key = str(t.date)
        data.setdefault(key, {'expenses': [], 'notes': [], 'todos': []})
        data[key]['todos'].append({
            'id': t.id, 'task': t.task, 'done': t.done
        })

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
