import os
import pandas as pd
import requests
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

GOOGLE_BOOKS_API_KEY = "AIzaSyCwFQNwNZvqZEeXtT8i1WcIAQA8OPkx494"

def fetch_from_google_books(title, author=None):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    query = f"intitle:{title}"
    if author:
        query += f"+inauthor:{author}"
    params = {'q': query, 'key': GOOGLE_BOOKS_API_KEY, 'maxResults': 5}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    return []

def fetch_from_open_library(title, author=None):
    base_url = "https://openlibrary.org/search.json"
    params = {'title': title}
    if author:
        params['author'] = author
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('docs', [])
    return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Read and process the CSV file
            goodreads_df = pd.read_csv(filepath)
            results = []

            # Iterate over the rows in the DataFrame
            for index, row in goodreads_df.iterrows():
                title = row.get('Title', '')
                author = row.get('Author', '')

                google_books_results = fetch_from_google_books(title, author)
                open_library_results = fetch_from_open_library(title, author)

                # Combine results
                for book in google_books_results:
                    volume_info = book['volumeInfo']
                    results.append({
                        'source': 'Google Books',
                        'title': volume_info.get('title', 'Unknown'),
                        'author': ', '.join(volume_info.get('authors', ['Unknown'])),
                        'isbn': ', '.join([identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', [])]),
                        'published_date': volume_info.get('publishedDate', 'Unknown')
                    })

                for book in open_library_results:
                    results.append({
                        'source': 'Open Library',
                        'title': book.get('title', 'Unknown'),
                        'author': ', '.join(book.get('author_name', ['Unknown'])),
                        'isbn': ', '.join(book.get('isbn', [])),
                        'published_date': book.get('first_publish_year', 'Unknown')
                    })

            return render_template('index.html', results=results)

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=13989, debug=True)
