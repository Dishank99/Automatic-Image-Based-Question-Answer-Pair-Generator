import os
import requests
import json
import joblib
import random

label_encoder_file_name = 'labelencoder/FULL_labelencoder_trainval.pkl'
labelencoder = joblib.load(label_encoder_file_name)

def get_answers_from_labels(label):
    label_name = str(labelencoder.inverse_transform([int(label)]))
    label_name = label_name[2:-2]
    return label_name

def get_images(image_url_array):
    try:
        media_dir = 'media/'
        path_array = []

        for image_url in image_url_array:

            f_name = media_dir + image_url[image_url.rindex('%2F')+3:image_url.rindex('?')]

            #check is file already exists, if it does then dont download 
            if not os.path.exists(f_name):
                print('Downloading Image ...')
                page = requests.get(image_url)
                if page.status_code == 200:
                    with open(f_name, 'wb') as f:
                        for chunk in page:
                            f.write(chunk)

            path = os.path.abspath(f_name)
            path_array.append(path)

        return str(path_array)
    except Exception as e :
        raise e

def get_answer_from_image_and_question(image_path_array, question_array):
    try:
        prediction_result_response = requests.post('http://127.0.0.1:80/',data = json.dumps({'image_path_array':str(image_path_array),'question_array':str(question_array)}), headers={'Content-Type': 'application/json'})        
        if prediction_result_response.status_code != 200:
            return ['Error in answer generation',{}]
        prediction_result = prediction_result_response.json()
        array_of_array_of_labels = prediction_result['result']
        global_response = []
        for array_of_labels in array_of_array_of_labels:
            array_of_answers = [get_answers_from_labels(label) for label in array_of_labels]
            correct_answer = array_of_answers[0]
            options = []
            if correct_answer == 'yes':
                options = [correct_answer, 'no']
            elif correct_answer == 'no':
                options = [correct_answer, 'yes']
            else:
                options = [correct_answer, array_of_answers[3], array_of_answers[4]]
            random.shuffle(options)
            global_response.append({'correct_answer':correct_answer, 'options':options})

        return ['', global_response]
    except Exception as e:
        raise e

def get_questions_from_image(image_path_array):
    try:
        prediction_result_response = requests.post('http://127.0.0.1:90/',data = json.dumps({'image_path_array':str(image_path_array)}), headers={'Content-Type': 'application/json'})        
        if prediction_result_response.status_code != 200:
            return ['Error in question generation',{}]
        prediction_result = prediction_result_response.json()
        array_of_questions = prediction_result['result']
        return ['', array_of_questions]
    except Exception as e:
        raise e