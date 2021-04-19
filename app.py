import flask
from flask import jsonify, request
from utils import get_images, get_answer_from_image_and_question, get_questions_from_image
import json
from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

CACHE_FILE = 'cache/cache.json'

url = 'https://firebasestorage.googleapis.com/v0/b/iiqa-dev.appspot.com/o/random%2Fbikes.jpeg'

# cache_file_data = open(CACHE_FILE,'r+')
# cache = json.loads(cache_file_data.read())

def get_data_from_cache(image_url_array, cache):
    try:
        print(cache)
        cached_data = []
        rem_data = []
        for image_url in image_url_array:
            if(cache.get(image_url)):
                cached_data.append(cache.get(image_url))
            else:
                rem_data.append(image_url)
        
        print(cached_data, rem_data)
        return [cached_data, rem_data]
    except Exception as e:
        print(e)
        raise e

def cache_new_data(generated_data, cache, cache_file_data):
    try:
        print('Caching ...')
        for each_data_obj in generated_data:
            cache[each_data_obj['image_path']] = each_data_obj
        cache_file_data.seek(0)
        cache_file_data.write(json.dumps(cache))
        cache_file_data.close()
    except Exception as e:
        print(e)
        raise e

@app.route('/', methods=['POST'])
def home():
    try:

        image_url_array = request.json['image_url_array']
        image_url_array = [each_url[1:-1] for each_url in image_url_array[1:-1].split(', ')]

        cache_file_data = open(CACHE_FILE,'r+')
        cache = json.loads(cache_file_data.read())

        cached_data, rem_image_url_array = get_data_from_cache(image_url_array, cache)

        response_value = []
        if(rem_image_url_array):
            saved_image_path_array = get_images(rem_image_url_array)
            # print(saved_image_path_array)
            # print(str(saved_image_path_array))
            # print(json.dumps(saved_image_path_array))
            # print(json.dumps(str(saved_image_path_array)))
            # return 'ok'
            err, question_array = get_questions_from_image(saved_image_path_array)
            if err:
                return jsonify({'error':err}), 500
            err, generated_answer_array = get_answer_from_image_and_question(saved_image_path_array, question_array)
            if err:
                return jsonify({'error':err}), 500
            
            for question, answer, image_path in zip(question_array, generated_answer_array, rem_image_url_array):
                response_value.append({'question':question, 'answer':answer, 'image_path': image_path})

            cache_new_data(response_value, cache, cache_file_data)

            # cache_file_data.close()
        
        if cached_data: response_value += cached_data
        print(response_value)

        return jsonify({'result':response_value}), 200
    except Exception as e:
        print(e)
        return jsonify({'error':str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=100)
