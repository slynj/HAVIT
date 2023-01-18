from flask import Flask, request
from flask_cors import CORS, cross_origin

import config, os

from video import export_video

app = Flask(__name__, static_folder='../web/build', static_url_path='/')

CORS(app, resources={r'/api/*': {'origins': '*'}})

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# For Flask to React Routing...
@app.errorhandler(404)
def not_found(e):   
    '''
    This function is used to redirect the user to the React Router page
    Parameters
    ----------
    e: Exception
        The exception that was raised
    Returns
    -------
    DOM File
        Returns a HTML script that contains the visual elements of the website
    '''
    return app.send_static_file('index.html')

@app.route('/') 
def serve():
    '''
    This function is executed in root directory,
    redirecting to the static HTML file generated by React front-end framework
    
    Parameters
    ----------
    None
    Returns
    -------
    DOM File
        Returns a HTML script that contains the visual elements of the website
    '''
    return app.send_static_file('index.html')

@app.route('/api/firebase-auth', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def firebase_auth():
    # Get the Firebase credentials from the request
    firebase_token = request.form['firebase_token']

    # Verify the Firebase token using the Firebase Admin SDK
    try:
        decoded_token = config.auth.verify_id_token(firebase_token)
        print("Successfully verified Firebase token: ", decoded_token);

        config.initialize_app()

        return {'status': 'success', 'user_id': decoded_token['uid']}, 200

    except config.auth.AuthError as e:
        return {'status': 'error', 'message': str(e)}, 400

@app.route('/api/export-video', methods=['POST'])
@cross_origin
def get_video():
    timeline_name = request.form['timeline_name']
    template_name = request.form['template_name']

    user = config.auth.get_user(user_id)
    email = user.email

    try:
        export_video(email, timeline_name, template_name)

        return {'status': 'success'}, 200
    
    except:
        return {'status': 'error'}, 400

if __name__ == '__main__':
    # python api.py (Windows) OR python3 api.py (macOS/Linux)
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host='0.0.0.0', port=port)