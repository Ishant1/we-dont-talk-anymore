from google.cloud import documentai_v1 as documentai
from google.cloud import storage
import os

# TODO(developer): Uncomment these variables before running the sample.
# project_id= 'YOUR_PROJECT_ID'
# location = 'YOUR_PROJECT_LOCATION' # Format is 'us' or 'eu'
# processor_id = 'YOUR_PROCESSOR_ID' # Create processor in Cloud Console
# gcs_input_uri = "YOUR_INPUT_URI"
# gcs_output_uri = "YOUR_OUTPUT_BUCKET_URI"
# gcs_output_uri_prefix = "YOUR_OUTPUT_URI_PREFIX"
project_id = "hackathon-team-07"
processor_id = "ff2b8b191f175e01"


def process_document_sample(blob_content):
    from google.cloud import documentai_v1 as documentai

    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{project_id}/locations/eu/processors/{processor_id}"


    # Read the file into memory
    document = {"content": blob_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)

    document = result.document

    print("Document processing complete.")

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    document_pages = document.pages

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    for page in document_pages:
        paragraphs = page.paragraphs
        for paragraph in paragraphs:
            paragraph_text = get_text(paragraph.layout, document)
            print(f"Paragraph text: {paragraph_text}")



def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response

file_path = "doc_ai_input.pdf"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\wafi-\Downloads\hackathon-team-07-170cf73a6fea.json"
process_document_sample(file_path=file_path)