from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash, abort
import os
from werkzeug.utils import secure_filename
import datetime

# Updated LangChain Imports
from langchain_openai import ChatOpenAI 
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI

from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser


# Flask Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process and rename PDFs
def process_pdf(api_key, model_name, filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Load and split the PDF into pages
    loader = PyPDFLoader(pdf_path)
    documents = loader.load_and_split()
    
    # Concatenate the content of the documents
    context = " ".join([page.page_content for page in documents])
    if len(context) > 128000:
        context = context[:128000]
    
    # Initialize the appropriate LLM
    if 'gpt' in model_name:
        llm = ChatOpenAI(temperature=0, model_name=model_name, openai_api_key=api_key)
    elif 'gpt' in model:
        llm = ChatOpenAI(temperature=0, model_name=model, api_key=api)
    elif 'claude' in model:
        llm = ChatAnthropic(temperature=0, model=model, anthropic_api_key=api)
    elif 'mistral' in model:
        llm = ChatMistralAI(temperature=0, model=model, mistral_api_key=api)
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    
    user_input = '''Based on the file provided, generate a file name in this format: [year published]_[aspect of the technology]_[main topic]_[primary application].pdf. 
    Please do not give any response except for the file name. Do not include symbols like /, \\, ~, !, @, #, or $ in the file name.'''
    

    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", 'You are a helpful assistant. Use the following context when responding:\n\n{context}.'),
        ("human", "{question}")
    ])

    output_parser = StrOutputParser()
    rag_chain = rag_prompt | llm | StrOutputParser()


    response = rag_chain.invoke({
            "question": user_input,
            "context": context
        })
    
    print(response)

    # Extract the filename from the response
    new_filename = response.strip()
    
    # Ensure the filename is secure and ends with .pdf
    new_filename = secure_filename(new_filename)
    if not new_filename.lower().endswith('.pdf'):
        new_filename += '.pdf'
    new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
    
    # Handle duplicate filenames
    if os.path.exists(new_filepath):
        base, ext = os.path.splitext(new_filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{base}_{timestamp}{ext}"
        new_filepath = os.path.join(app.config['PROCESSED_FOLDER'], new_filename)
        print(f"Saving file to: {new_filepath}")
    
    # Move the processed file to the processed folder with the new name
    os.rename(pdf_path, new_filepath)
    return new_filename

# Route for homepage and file upload form
@app.route('/')
def upload_page():
    return render_template('upload_v3.html')

# Route for file upload handling
@app.route('/upload', methods=['GET', 'POST']) # new
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Get API key and model from the form
        api_key = request.form['api_key']
        model_name = request.form['model']
        
        # Process the file
        try:
            new_filename = process_pdf(api_key, model_name, filename)
        except Exception as e:
            flash(f'Error processing file: {e}')
            return redirect(url_for('upload_page'))
        
        # Redirect to download page
        return redirect(url_for('download_page', filename=new_filename))
    else:
        flash('Allowed file types are pdf.')
        return redirect(request.url)



# Route for the download page
@app.route('/download/<filename>')
def download_page(filename):
    return render_template('download.html', filename=filename)

# Route for downloading processed files
@app.route('/processed/<filename>')
def download_file(filename):
    print("Requested filename:", filename)
    directory = app.config['PROCESSED_FOLDER']
    file_path = os.path.join(directory, filename)
    print("Files in processed directory:", os.listdir(directory))
    if os.path.isfile(file_path):
        try:
            return send_from_directory(directory, filename, as_attachment=True)
        except Exception as e:
            print(f"Error sending file: {e}")
            abort(500)
        else:
            print(f"File not found: {file_path}")
            abort(404)

# works on local
# if __name__ == '__main__':
#     # app.run(debug=True)

# For public internet
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get the port from environment or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
