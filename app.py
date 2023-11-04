from flask import Flask, request, render_template, jsonify, flash, redirect, url_for, session, logging, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os

def create_app(test_config=None):
    # Create and configure the app
    template_dir = os.path.abspath('templates')

    # Initialize the app
    app = Flask(__name__, template_folder=template_dir)
    
    # Load default config from settings.py
    app.config.from_pyfile('settings.py')

    # Initialize Plugins
    CORS(app, resources={r"/api/*": {"origins": "*"}})
     
    # Config MySQL
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
    app.config['MYSQL_PORT'] = 3306  # If the port is constant, you don't need to set it from environment variables.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Initialize MySQL
    mysql = MySQL(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    # Define the folder where uploaded images will be saved
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Define allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Function to check if the file extension is allowed
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')
    
    # Define a route for uploading an image and saving it to the server and database
    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        if 'images' not in request.files:
            return jsonify({'status': 'failure', 'message': 'No file part'})

        file = request.files['images']

        if file.filename == '':
            return jsonify({'status': 'failure', 'message': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Insert image and text data into the database
            cursor = mysql.connection.cursor()
            data = {
                'images': filename,
                'texts': request.form.get('texts', '')
            }
            cursor.execute("INSERT INTO users (images, texts) VALUES (%(images)s, %(texts)s)", data)
            mysql.connection.commit()
            cursor.close()

            return jsonify({'status': 'success', 'message': 'Image uploaded and data inserted into the database'})

        return jsonify({'status': 'failure', 'message': 'Invalid file format'})

    # Define a route for deleting an image and its associated data
    @app.route('/delete_image', methods=['POST'])
    def delete_image():
        id = request.form.get('id')  # Get the ID parameter from the POST request

        cursor = mysql.connection.cursor()

        # Check if the image exists
        cursor.execute("SELECT images FROM users WHERE id = %s", (id,))
        result = cursor.fetchone()

        if result:
            image_name = result[0]  # Get the image name from the database
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)  # Create the path to the image

            if os.path.exists(image_path):
                os.remove(image_path)  # Delete the image file

            # Delete the image record from the database
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            mysql.connection.commit()

            cursor.close()

            return jsonify({'status': 'success', 'message': 'Image and associated data deleted successfully'})
        else:
            cursor.close()
            return jsonify({'status': 'failure', 'message': 'Image not found'})
        
    # Define a route to list all images and their details
    @app.route('/list_images', methods=['GET'])
    def list_images():
        cursor = mysql.connection.cursor()

        # Retrieve all data from the database
        cursor.execute("SELECT * FROM users")
        all_data = cursor.fetchall()
        cursor.close()

        return render_template('index.html', all_data=all_data)

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
