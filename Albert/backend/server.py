#setup flask
from flask import Flask, render_template, request, redirect, url_for, jsonify
import datetime
import requests
#whats the pip install for postgres
import psycopg2
import requests
from keybert import KeyBERT
import nltk
from nltk.data import find
import openai
import json
from openai import OpenAI
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from flatten_json import flatten
import ast


app = Flask(__name__)

@app.route('/questions', methods=['GET'])
def questions():
    #connect to postgres
    conn = psycopg2.connect(
        host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
        user="postgres",
        password="why",
        port="5432"
    )
    #cursor for postgres
    cur = conn.cursor()
    #select all questions entries
    cur.execute("SELECT * FROM questions;")
    #fetch all journal entries
    rows = cur.fetchall()
    #return the journal entries
    return jsonify({"results": rows})

#function to insert a new journal entry
@app.route('/insert', methods=['POST'])
def insert():
  #connection code for postgres
  #write me code to pull linktoimage,entrytext, lastwrite from request

  linktoimage = request.form['linktoimage']
  entrytext = request.form['entrytext']
  lastwrite = request.form['lastwrite']


  


  #connect to postgres
  conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
  )
  #cursor for postgres
  cur = conn.cursor()
  #insert a new journal entry
  entrydate = datetime.datetime.now().strftime("%Y-%m-%d")

  #write an insert query that uses the variables linktoimage,entrytext, lastwrite, entrydate
  cur.execute("INSERT INTO journal (entrydate, linktoimage, entrytext, lastwrite) VALUES (%s, %s, %s, %s)", (entrydate, linktoimage, entrytext, lastwrite))

  #commit the transaction
  conn.commit()



  return None

#select all journal entries for the cards
@app.route('/get', methods=['GET'])
def get():
  #connect to postgres
  conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
  )
  #cursor for postgres
  cur = conn.cursor()
  #select all journal entries

  cur.execute("SELECT * FROM journal")
  #fetch all journal entries
  rows = cur.fetchall()
  #return the journal entries
  return jsonify({"results": rows})

@app.route('/get_column', methods=['get'])
def get_column():
  #write me code to pull the column name from the request
  column = request.args.get('column')

  #connect to postgres
  conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
  )

  query = "SELECT " + column + " FROM journal;"
  #cursor for postgres

  cur = conn.cursor()
  #select all journal entries
  cur.execute(query)
  #fetch all journal entries
  rows = cur.fetchall()
  #return the journal entries
  return jsonify({"results": rows})

def extract_and_expand_concepts(doc):
  #write me code to pull the entrytext from the request
  
# Function to check and download necessary NLTK packages
  def download_nltk_data_if_needed(packages=['wordnet', 'averaged_perceptron_tagger']):
      for package in packages:
            try:
                # Check if the package is already downloaded
                find(f"corpora/{package}.zip")
            except LookupError:
                # If not found, download it
                nltk.download(package, quiet=True)

    # Example usage
  download_nltk_data_if_needed()
  lemmatizer = WordNetLemmatizer()
  def query_conceptnet_specific(word, relationships=['/r/RelatedTo', '/r/IsA', '/r/PartOf', '/r/UsedFor', "/r/AtLocation"], limit_per_relation=4):
        related_concepts = {}
        base_url = 'http://api.conceptnet.io/query'
        
        for relationship in relationships:
            related_concepts[relationship] = []
            url = f'{base_url}?node=/c/en/{word}&rel={relationship}&limit={limit_per_relation}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for edge in data.get('edges', []):
                    related_node = edge['end']['label'] if edge['start']['label'].lower() == word.lower() else edge['start']['label']
                    weight = edge.get('weight', 0)
                    if related_node.lower() != word.lower():  # Filter out self references
                        related_concepts[relationship].append((related_node, weight))
            else:
                print(f"Failed to fetch data for relationship {relationship}. Status code: {response.status_code}")
        return related_concepts

  def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)


  def lemmatize_keywords(keywords):
        return [lemmatizer.lemmatize(keyword, get_wordnet_pos(keyword)) for keyword in keywords]

  def get_keywords(doc, threshold=0.5):
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 1), stop_words=None)
        filtered_keywords = [keyword[0] for keyword in keywords if keyword[1] >= threshold]

        if filtered_keywords:
            return lemmatize_keywords(filtered_keywords)
        else:  
            # Find the keyword with the highest score, regardless of threshold
            highest_scoring_keyword = max(keywords, key=lambda x: x[1]) 
            return lemmatize_keywords([highest_scoring_keyword[0]]) 

  def get_and_process_wikipedia_summary(keywords):
        summaries_keywords = []
        for keyword in keywords:
            url = 'https://en.wikipedia.org/w/api.php'
            params = {'action': 'query', 'format': 'json', 'titles': keyword, 'prop': 'extracts', 'exintro': True, 'explaintext': True}
            response = requests.get(url, params=params)
            data = response.json()
            page = next(iter(data['query']['pages'].values()), {})
            summary = page.get('extract')
            if summary:
                summary_keywords = get_keywords(summary, 0.5)  

                # Keep only top 3 by score
                top_summary_keywords = sorted(summary_keywords, key=lambda x: x[1], reverse=True)[:3]
                summaries_keywords.extend(top_summary_keywords)

        return list(set(summaries_keywords))  # Remove duplicates, considering both keyword and score

    # Start of the main logic
  initial_keywords = get_keywords(doc)
  all_keywords = get_and_process_wikipedia_summary(initial_keywords)
  all_concepts = []

    # Query ConceptNet for each keyword and accumulate concepts
  for keyword in all_keywords:
        related_concepts_by_relationship = query_conceptnet_specific(keyword)
        for relationship, concepts in related_concepts_by_relationship.items():
            all_concepts.extend([concept for concept, weight in concepts])

  return list(set(all_concepts))  # Return a unique list of all related concepts

def vectorize_search(related_words):
    #write me code to pull the query from the request
    
    #write me code to connect to postgres
    conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
    )
    #write me code to create a cursor for postgres
    cur = conn.cursor()
    #write me code to execute the search query
    

    #write me  code that should go through an array called related_words and execute a search for each word
    results = []
    print(related_words)
    for word in related_words:
        cleaned_word = ''.join(letter for letter in word if letter.isalnum())

        query = """SELECT * FROM vectorize.search(
    job_name => 'find_content',
    query => '""" + cleaned_word + """',
    return_columns => ARRAY['entrydate', 'entrytext'],
    num_results => 3
);"""
        cur.execute(query)
        rows = cur.fetchall()
        #append each of the rows within the results to a list
        
        for row in rows:
            results.append(row)
        
    conn.close()
    return results


    #write me code to fetch the results
    

    #write me code to fetch the results
    rows = cur.fetchall()
    #return the results
    return jsonify({"results": rows})


@app.route('/answer_question', methods=['GET'])
def answer_question():
    '''
    return [
    '2021-10-05',
    "Dave is more than a son; he's your bridge to the past and your guide in the present. He encourages you to remember things that once brought joy, like making burritos, and he patiently helps you through moments of confusion. Dave's visits, notes, and gestures of love anchor you to the world and to who you are."
]

'''
    #write me code to pull the question from the request
    question = request.args.get('question')
    
    #write me postgress connection code to insert the question into the database
    conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
    )
    #write me code to create a cursor for postgres
    cur = conn.cursor()
    #write me code to execute the search query
    
# Use a parameterized query for security and to avoid SQL injection
    query = "INSERT INTO questions (question) VALUES (%s);"
    cur.execute(query, (question,))

    # Commit the transaction to make sure the data is saved
    conn.commit()
    print("inserted")


    
    #write me code to call the function generate_summary_and_extract_list
    related_words = extract_and_expand_concepts(question)
    tembostuff = vectorize_search(related_words)


    
    results = generate_summary_and_extract_list(str(question), str(tembostuff))
    return jsonify({"results": results})
    




    #return the result

# Example usage


def generate_summary_and_extract_list(user_message, data_dump):
    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key="why")

    message = f"You are an assistant who summarizes in 2nd person the diary entries for an Alzheimer's patient to refresh their memory based on 'entrytext:' and return also the most relevant date in [summary, date] format, feel free to correct the user if the prompt is obviously contradicting data. The data is below and has ('entrydate', 'entrytext', and 'similarity_score'). Similarity_score is equivalent to the importance of the sentence. {data_dump} THE RETURN MUST BE A LIST IN [DATE, summary] the summary is a general answer to the users question while inferring from their past memories. The list should have only 1 SINGULAR element."
    # Make the API call
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
        {"role": "system", "content": message},
        {"role": "user", "content": user_message},
      ]
    )
    # Assuming the response structure is similar to what you've shared
    # Extract the stringified list from the response
    stringified_list = response.choices[0].message.content

    # Convert the stringified list back into a Python list
    extracted_list = ast.literal_eval(stringified_list)
    return extracted_list




if __name__ == '__main__':
  app.run(host="0.0.0.0",port=6000, debug=True)

'''
linktoimage = "c"
# Create a list to store the journal entri, keeping content intact
journal_entries = [
    """This morning, I found a note next to my bed labeled "Call Dave about the doctor's appointment." I spent a good minute wondering who Dave could be. I saw his contact image and he looks a lot like me. It's unsettling not to remember who some people are. Later, a man called Dave came by. He said he's my son. We talked about my health and upcoming doctor's visit. He brought Chipotle and it was really good. He told me that I could make something like this if I went to Kroger to buy the ingredients: rice, beans, and tortillas. He told me to send him a picture of the finished burrito. He seemed nice.""",
    """I found myself standing in the middle of Kroger, holding a shopping list I don't remember writing. The list had simple items: rice, beans, and tortillas. But, why am I here? The last thing I recall was wanting to make burritos. Did Dave suggest coming here? It's all a bit fuzzy. Anyway, after I bought the ingredients, I made two burritos and they were pretty good. But they were not as good as Chipotle. I feel like I'm forgetting to do something.""",
    """This morning started with a sense of accomplishment; I remembered the burritos from yesterday, albeit not as tasty as Chipotle's. As I cleaned up, I found a note on the fridge written in my handwriting, "Send Dave a picture of the burrito." That's what I forgot! I quickly took a photo of the remaining burrito and sent it to Dave. His reply was instant, filled with laughing emojis and a "Looks delicious! Proud of you, Dad." Dad. That word echoed in my mind. Dave is not just someone who looks a lot like me; he is my son, a part of me. It's a strange feeling, knowing so much yet so little about someone so important.""",
    """Dave came over today. Seeing him in person, there's no denying the resemblance; it's like looking into a mirror from the past. He brought a photo album, flipping through pages of memories, some familiar, others like stories from another's life. "This is us camping," he pointed to a picture, "You loved making campfire burritos." Suddenly, the trip to Kroger, the attempt at making burritos—it all made sense. It wasn't just about recreating a meal; it was about reconnecting with a past that keeps slipping away from me. Dave hugged me before he left, a simple gesture that filled the room with warmth and love.""",
    """I woke up today feeling more connected to my surroundings. The notes, the photos, Dave's visits—they're all breadcrumbs leading me back home, to myself. I decided to make burritos again, this time adding my own twist, something from the faded edges of my memory. As I cooked, I realized why Dave had encouraged me to make them. It's not the burritos that matter; it's the act of remembering, of doing something that once brought joy. I sent Dave a picture, not expecting praise, but as a thank you for guiding me through the fog.""",
    """Dave surprised me with a visit today. "Let's go for a drive," he said. We ended up at Kroger, but this time, it wasn't about buying ingredients. We walked through each aisle slowly, Dave pointing out different foods, sharing stories about our family's cooking adventures. Apparently, I was the chilli cookoff champion and I used a lot of spices. That explains why I like chilli. Each story was a piece of me, returned through his words. Back home, as we cooked together, I realized these moments are my lifeline, anchoring me to the world, to Dave, to who I am.""",
    """Today was a good day. I sat by the window, reflecting on the past week. The journey from confusion to clarity isn't linear; it's filled with moments of both loss and discovery. Dave is more than a son; he's my bridge to the past and my guide in the present. And the tortillas? They're more than just an ingredient; they're a symbol of connection—to my culture, to my family, and to the memories that shape us. I may not always remember the specifics, but the feelings they evoke, the sense of belonging and love, are unforgettable. As I close today's entry, I'm filled with gratitude for Dave, for the reminders"""]

entrydate = ["2021-10-01", "2021-10-02", "2021-10-03", "2021-10-04", "2021-10-05", "2021-10-06", "2021-10-07"]



SELECT * FROM vectorize.search(
    job_name => 'find_content',
    query => 'dave',
    return_columns => ARRAY['entrydate', 'entrytext'],
    num_results => 3
);

  #connect to postgres
conn = psycopg2.connect(
    host="org-buycott-inst-alzvectorbackend.data-1.use1.tembo.io",
    user="postgres",
    password="why",
    port="5432"
  )
  #cursor for postgres
cur = conn.cursor()
  #insert a new journal entry

for i in range(len(journal_entries)):
  #write an insert query that uses the variables linktoimage,entrytext, lastwrite, entrydate
  entrytext = journal_entries[i]
  date = entrydate[i]
  cur.execute("INSERT INTO journal (entrydate, linktoimage, entrytext) VALUES (%s, %s, %s)", (date, linktoimage, entrytext))

  #commit the transaction
conn.commit()

'''
