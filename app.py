from wsgiref import simple_server
from flask import Flask, request, render_template, redirect,send_from_directory
from flask import Response
import os
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import candev
from flask import send_file


os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')


app = Flask(__name__,static_url_path='/static',static_folder='static/')
#dashboard.bind(app)
CORS(app)

app.config["UPLOAD_FOLDER"] = "static/"


@app.route('/')
@cross_origin()
def upload_file():
    return render_template('index.html')

# @app.route('/testing')
# @cross_origin()
# def testing_redirect():
#     print('gaf')
#     return send_from_directory('static/','output_csv/ALDERVILLE_FIRST_NATION_ON_2019-20_page_0.csv')

# @app.route('/display_output')
# @cross_origin()
# def display_output():
#     extracted_files = os.listdir(os.path.join('static','output_csv'))
#     print(extracted_files)
#     # return '<a href="'+dest_path+'">See Files</a>'
#     return render_template('display_result.html',your_list=extracted_files)
    

@app.route('/display', methods = ['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(app.config['UPLOAD_FOLDER'] + filename)
    #     #file = open(app.config['UPLOAD_FOLDER'] + filename,"r")
    #     #content = file.read()

        file_path = app.config['UPLOAD_FOLDER'] + filename
        
        candev.extract_csv(file_path)
        
        extracted_files = os.listdir(os.path.join('static','output_csv'))
        # print(extracted_files)
        # return '<a href="'+dest_path+'">See Files</a>'
        return render_template('display_result.html',your_list=extracted_files)
        # return '<a href="'+dest_path+'" download="'+filename+'">Download</a>'
        # return render_template(dest_path)
    
    return 'an error occured'


# port = int(os.getenv("PORT",5000))
if __name__ == "__main__":
    app.run(debug=True) # me
    # host = '0.0.0.0'
    # #port = 5000
    # httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    # httpd.serve_forever()
