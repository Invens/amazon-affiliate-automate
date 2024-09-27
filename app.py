from flask import Flask, render_template, request, redirect, url_for
import pymysql
import schedule
import time
from campaign_scheduler import run_campaign  # Campaign Scheduler logic

app = Flask(__name__)

# MySQL database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",  # Your MySQL host
        user="root",       # MySQL username
        password="",  # MySQL password
        db="campaign_db",  # Database name
        cursorclass=pymysql.cursors.DictCursor
    )

# Homepage: Create & List Campaigns
@app.route('/')
def index():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM campaigns")
        campaigns = cursor.fetchall()
    conn.close()
    return render_template('index.html', campaigns=campaigns)

# Create new campaign
@app.route('/create', methods=['GET', 'POST'])
def create_campaign():
    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        keywords = request.form['keywords']
        category = request.form['category']
        tag = request.form['tag']
        interval = request.form['intervals']
        max_posts = request.form['max_posts']
        total_posts = request.form['total_posts']

        # Insert campaign into MySQL
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO campaigns (campaign_name, keywords, category, tag, intervals, max_posts, total_posts)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (campaign_name, keywords, category, tag, interval, max_posts, total_posts))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('create_campaign.html')

# Edit Campaign
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_campaign(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM campaigns WHERE id = %s", (id,))
        campaign = cursor.fetchone()

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        keywords = request.form['keywords']
        category = request.form['category']
        tag = request.form['tag']
        interval = request.form['intervals']
        max_posts = request.form['max_posts']
        total_posts = request.form['total_posts']

        # Update campaign in MySQL
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE campaigns SET campaign_name = %s, keywords = %s, category = %s, tag = %s, intervals = %s, max_posts = %s, total_posts = %s 
                WHERE id = %s
            ''', (campaign_name, keywords, category, tag, interval, max_posts, total_posts, id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_campaign.html', campaign=campaign)

# Delete Campaign
@app.route('/delete/<int:id>')
def delete_campaign(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM campaigns WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090, debug=True)
