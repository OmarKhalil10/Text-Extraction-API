## To add a new page
* Create the html, css, js in the specified folder using the same folder structure.
* Create a new route in the [app.py](./app.py) file with the name you want using only dashes to seperate words.
```PYTHON
@app.route('NEW-ROUTE')
```
* Define your serving function using a unique name not used before in the whole application.
```PYTHON
def NEW_UNIQUE_NAME():
```
* Return your html file path using render_template.
```PYTHON
return render_template('FILE_PATH.html')
```
* Your newely created route should look like this.
```PYTHON
@app.route('NEW-ROUTE')
def NEW_UNIQUE_NAME():
    return render_template('FILE_PATH.html')
```

## To run the development server
* Open git bash terminal
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --reload
```

## To list all images

```
http://127.0.0.1:5000/list_images
```

## To delete an image
```
curl -X DELETE http://localhost:5000/delete_image?id=<image_id>
```