from flask import *
from flask_mysqldb import MySQL
from pdfminer.high_level import extract_text
import nltk
import string
import random
import pandas as pd

# downloading word dictionaries, will be useful when word2vec is implemented


app = Flask(__name__)

# Configuration
app.config['MYSQL_HOST'] = 'msimserver.database.windows.net'
app.config['MYSQL_USER'] = 'msimadmin@msimserver'
app.config['MYSQL_PASSWORD'] = 'Talentsharks$'
app.config['MYSQL_DB'] = 'msimdb'

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    return "Welcome to recommendation api"

@app.route('/skills', methods=['GET'])
def skills():
    candidate_id = request.args.get('candidate_id')
    candidate_resume_path = request.args.get('resume_path') # path for resume
    resume_text = extract_text(candidate_resume_path)

    # tokenizing the text
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(resume_text)

    # removing the stop words
    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    # remove punctuations (Need to check this one)
    # filtered_tokens = [w for w in word_tokens if w.isalpha()]
    filtered_tokens = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
    

    # Generating bigrams (Machine Learning --> MachineLearning)
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

    store_skills = set() #Returning a set, can be converted into list/JSON/P-Queue/other
    TECH_SKILLS_DB = [
    'java',
    'c',
    'javascript',
    'machinelearning',
    'linux',
    'mongodb',
    'python',
    'oops',
    'unix',
    'net'
    ]
    for token in filtered_tokens:
        if token.lower() in TECH_SKILLS_DB:
            store_skills.add(token.lower())
    
    for ngram in bigrams_trigrams:
        if ngram.lower() in TECH_SKILLS_DB:
            store_skills.add(token.lower())
        

    skill_list = tuple(store_skills)
    delim = ","
    skill_string = delim.join(skill_list)

    curr = mysql.connection.cursor()
    curr.execute("UPDATE CANDIDATE_BANK SET SKILL=%s where IM_CAN_ID=%s",(skill_string,candidate_id))
    mysql.connection.commit()
    curr.close()

    return jsonify(skill_list)



if __name__ == '__main__':
    app.run(debug=True)


