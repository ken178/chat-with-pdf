import streamlit as st
import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from spacy import displacy
import pdfplumber
import pymongo

# Install required libraries
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Define a function to extract text from a PDF
def extract_text_from_pdf(file_path):
    try:
        pdf_file_obj = open(file_path, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
        num_pages = pdf_reader.numPages
        text = ''
        for page in range(num_pages):
            page_obj = pdf_reader.getPage(page)
            text += page_obj.extractText()
        pdf_file_obj.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# Define a function to preprocess the text
def preprocess_text(text):
    try:
        # Remove punctuation and stop words
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.isalpha()]
        tokens = [word for word in tokens if word.lower() not in set(stopwords.words('english'))]

        # Lemmatize tokens
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

        return tokens
    except Exception as e:
        print(f"Error preprocessing text: {e}")
        return []

# Define a function to store extracted text in a database
def store_text_in_database(text, database_name):
    try:
        client = pymongo.MongoClient()
        db = client[database_name]
        collection = db['pdf_content']
        collection.insert_one({'text': text})
        client.close()
    except Exception as e:
        print(f"Error storing text in database: {e}")

# Define a function to search the database
def search_database(query, database_name):
    try:
        client = pymongo.MongoClient()
        db = client[database_name]
        collection = db['pdf_content']
        results = collection.find({'$text': {'$search': query}})
        client.close()
        return results
    except Exception as e:
        print(f"Error searching database: {e}")
        return []

# Define the main function
def main():
    # Create a Streamlit app instance
    st.title("PDF Text Extraction and Search")

    # Define a sidebar layout for the input file and search query
    with st.sidebar:
        st.write("Upload a PDF file:")
        uploaded_file = st.file_uploader("Choose a file", type="pdf")

        st.write("Enter a search query:")
        search_query = st.text_input("Search query:")

    # Define a layout for displaying search results
    if uploaded_file is not None:
        # Extract text from the uploaded PDF
        text = extract_text_from_pdf(uploaded_file.name)

        # Preprocess the text (but don't store preprocessed text)
        preprocessed_text = preprocess_text(text)

        # Store the original text in a database
        if text:
            store_text_in_database(text, 'your_database_name')

            # Search the database for relevant answers
            search_results = search_database(search_query, 'your_database_name')

            # Display the search results
            st.write("Search results:")
            if search_results:
                for result in search_results:
                    st.write(result['text'])
            else:
                st.write("No search results found.")

if __name__ == "__main__":
    main()

#This code will now store the original text in the database instead of the preprocessed text. When a search query 
# is entered and submitted, the search results will be displayed on the Streamlit app.

