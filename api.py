from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

def create_app(test_config=None):
    # Create and configure the app
    template_dir = os.path.abspath('templates')

    # Initialize the app
    app = Flask(__name__, template_folder=template_dir)
    
    # Load default config from settings.py
    app.config.from_pyfile('settings.py')  # Load database environment variables

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

    # Function to insert image and text data into the database
    def insert_data(image_name, texts):
        cursor = mysql.connection.cursor()
        data = {
            'images': image_name,
            'texts': texts
        }
        cursor.execute("INSERT INTO users (images, texts) VALUES (%(images)s, %(texts)s)", data)
        mysql.connection.commit()
        cursor.close()

    # Upload an image, save it to the database, and return the image URL
    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            insert_data(filename, request.form.get('texts', ''))
            return jsonify({'status': 'success', 'message': 'Image uploaded and data inserted into the database', 'image_url': filename})
        else:
            return jsonify({'status': 'failure', 'message': 'No file uploaded'})

    # Delete an image and its associated data
    @app.route('/delete_image', methods=['DELETE'])
    def delete_image():
        image_id = request.args.get('id')
        
        if image_id is None:
            return jsonify({'status': 'failure', 'message': 'Image ID is required'})

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT images FROM users WHERE id = %s", (image_id,))
        result = cursor.fetchone()

        if result:
            image_name = result[0]
            cursor.execute("DELETE FROM users WHERE id = %s", (image_id,))
            mysql.connection.commit()
            return jsonify({'status': 'success', 'message': 'Image and associated data deleted successfully'})
        else:
            mysql.connection.commit()
            return jsonify({'status': 'failure', 'message': 'Image not found'})

    # Define a route to list all images and their details
    @app.route('/list_images', methods=['GET'])
    def list_images():
        cursor = mysql.connection.cursor()

        # Retrieve all data from the database
        cursor.execute("SELECT * FROM users")
        all_data = cursor.fetchall()
        cursor.close()

        return jsonify({'status': 'success', 'data': all_data})

    return app
app = create_app()

if __name__ == '__main__':
    app.run()
