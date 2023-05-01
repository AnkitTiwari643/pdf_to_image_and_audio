import time
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import io
import os
import PyPDF2
from pdf_audio_api import settings
from gtts import gTTS
import tempfile
from pdf2image import convert_from_bytes


@csrf_exempt
def generate_audio(request):
    # get the text from the request
    pdf_file = request.FILES.get("pdf_file")

    # Extract the text from the PDF file
    text = extract_text(pdf_file)

    # generate the speech and save it to a file
    audio = gTTS(text=text, lang='hi', tld='co.in')
    unique_id = uuid.uuid4().hex
    file_name = f"output_{unique_id}.mp3"
    audio.save(file_name)
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)

    # save the output file to the media folder
    file_path = fs.save(file_name, open(file_name, 'rb'))

    # generate the URL of the output file
    file_url = fs.url(file_path)

    # create a JSON response object containing the URL
    response_data = {'file_url': file_url}
    print(response_data)
    return JsonResponse(response_data)

def extract_text(pdf_file):
    with io.BytesIO() as text_buffer:
        text_buffer.write(pdf_file.read())
        text_buffer.seek(0)
        pdf_reader = PyPDF2.PdfReader(text_buffer)
        text = ""
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
        return text



@csrf_exempt
def pdf_to_images(request):
    if request.method == 'POST':
        # Get the uploaded PDF file from the request
        pdf_file = request.FILES['pdf_file']

        # Create a temporary file to save the PDF data
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_file.read())

        fs = media_path = os.path.join(settings.MEDIA_ROOT)
        fs = fs[:len(fs)-1]
        print("fs", fs)
        # Convert the PDF to a list of images using pdf2image
        images = convert_from_bytes(open(tmp_file.name, 'rb').read(), poppler_path=r'C:\Users\91930\PycharmProjects\pythonProject\poppler-23.01.0\Library\bin', output_folder=fs, fmt='jpg')
        print(images)
        now = time.time()
        cutoff = now - 5  # 5 seconds ago
        image_urls = []
        for f in os.listdir(fs):
            if f.endswith('.jpg') and os.path.getctime(os.path.join(fs, f)) > cutoff:
                url = default_storage.url(f)
                image_urls.append(url)
        print(image_urls)
        print(len(image_urls))

        response_data = {'file_url': image_urls}
        return JsonResponse(response_data)


@csrf_exempt
def save_pdf_server(request):
    pdf_file = request.FILES.get('pdf_file')
    unique_id = uuid.uuid4().hex
    file_name = f"output_{unique_id}.pdf"
    path = default_storage.save('pdfs/' + pdf_file.name, ContentFile(pdf_file.read()))
    return JsonResponse({'file_url': path})
