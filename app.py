from flask import Flask, render_template, request, redirect, url_for, session, flash 
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import sqlite3, os
import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'sendmenote'

#===================FUNCTIONS===================
#EMAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fatimahnajihah05@gmail.com'
app.config['MAIL_PASSWORD'] = 'kdtg gpki efah gyal'  # NOT gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

#TOKEN ----------
serializer = URLSafeTimedSerializer(app.secret_key)

#use this when want to test result on terminal
def checking(output):
    print("-> " + output)

#DATABASE
def get_db():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# home
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('index.html') #initialise the screen

# successful note
@app.route('/notesent', methods=['GET'])
def notesent():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, notes FROM NoteDatabase ORDER BY noteID DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        username = row['username'] if row['username'] else 'anon'
        note_text = row['notes'] if row['notes'] else ''
    else:
        username = 'anon'
        note_text = 'No notes yet.'

    return render_template('notesent.html', username=username, note=note_text)

@app.route('/shownoteonlytims', methods=['GET'])
def shownote():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, notes, date FROM NoteDatabase ORDER BY noteID DESC")
    rows = c.fetchall()
    conn.close()

    return render_template('shownote.html', notes=rows)

@app.route('/readnoteonlytims', methods=['GET'])
def readnote():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT noteID, username, notes, date FROM NoteDatabase ORDER BY noteID DESC")
    rows = c.fetchall()

    selected_id = request.args.get('noteID', type=int)
    selected_note = None

    if selected_id is not None:
        selected_note = next((r for r in rows if r['noteID'] == selected_id), None)

    if not selected_note and rows:
        selected_note = rows[0]

    if selected_note is not None:
        session['selected_noteID'] = selected_note['noteID']

    conn.close()
    return render_template('readnote.html', notes=rows, selected_note=selected_note)


# new note entry
@app.route('/new-note', methods=['GET','POST'])
def newnote():
    if request.method == 'POST':
        note = request.form['note']
        username = request.form['username']

        #make sure all details are entered
        if not note:
            flash("Geng, kau submit kosong buat ape. be fr.", "error")
            return redirect(url_for('newnote'))
        if not username:
            flash("Ooo ingat nonchalant la submit unknown centu?", "error")
            return redirect(url_for('newnote'))
        
        checking(f"Username : {username}")
        checking(f"Note : {note}")

        conn = get_db()
        c = conn.cursor()

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            c.execute("INSERT INTO NoteDatabase (username, notes, date) VALUES (?,?,?)",
                      (username, note, date))
            conn.commit()

            note_id = c.lastrowid
            checking(f"noteID: {note_id}")

            # flash(f"Note sent! Tenkiu do nanti aq baca :P", "success")
            return redirect(url_for('notesent'))
        except Exception as e:
            conn.rollback()
            checking(f"Error: {e}")

            flash("Not triggered","error")
            return redirect(url_for('newnote'))
        finally:
            conn.close()
    return render_template('newnote.html') #initialise the screen

# read notes
@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        password = request.form['password']

        #make sure all details are entered
        if password == "Kokomi5!":
            return redirect(url_for('readnote'))
    return render_template('verify.html') #initialise the screen

#INIT 
if __name__ == '__main__':
    app.run(debug=True)