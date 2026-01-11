from flask import Flask, render_template, request
import pickle
import numpy as np

# Load data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommended.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # ✅ Safety check 1: empty input
    if not user_input:
        return render_template('recommended.html', error="Please enter a book name")

    # ✅ Safety check 2: book not in dataset
    if user_input not in pt.index:
        return render_template(
            'recommended.html',
            error="Book not found. Please try another title."
        )

    index = np.where(pt.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

        data.append([
            temp_df.iloc[0]['Book-Title'],
            temp_df.iloc[0]['Book-Author'],
            temp_df.iloc[0]['Image-URL-M']
        ])

    return render_template('recommended.html', data=data)

# ⚠️ Render uses Gunicorn, but keep this for local testing
if __name__ == '__main__':
    app.run()
