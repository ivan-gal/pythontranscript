import moviepy.editor as mp
import os
import speech_recognition as sr
from google.cloud import language_v1
import sys


clip = mp.VideoFileClip(sys.argv[1])
clip = clip.subclip(sys.argv[2], sys.argv[3])
os.remove("file.wav")
clip.audio.write_audiofile("file.wav")

with open("./key.json") as f:  # your google API key here
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
r = sr.Recognizer()
file = 'file.wav'

with sr.AudioFile(file) as source:
    audio = r.record(source)
    # Transcribe audio file
text = r.recognize_google_cloud(
    audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, show_all=True)

nextText = ''.join([i['alternatives'][0]['transcript']
                   for i in text['results']])

with open('file.txt', 'w') as f:
    f.write(nextText)

textFile = open("./file.txt", "r")


def classify(text, verbose=True):
    """Classify the input text into categories. """

    language_client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=text.encode("utf-8"), type_=language_v1.Document.Type.PLAIN_TEXT
    )
    response = language_client.classify_text(request={'document': document})
    categories = response.categories

    result = {}

    for category in categories:
        # Turn the categories into a dictionary of the form:
        # {category.name: category.confidence}, so that they can
        # be treated as a sparse vector.
        result[category.name] = category.confidence

    if verbose:
        for category in categories:
            print(u"=" * 20)
            print(u"{:<16}: {}".format("Categoria", category.name))
            print(u"{:<16}: {}".format("Confianza", category.confidence))

    return result


def sample_analyze_sentiment(text_content):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    client = language_v1.LanguageServiceClient()

    # text_content = 'I am so happy and joyful.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={'document': document, 'encoding_type': encoding_type})
    # Get overall sentiment of the input document
    print(u"Sentimiento total del documento: {}".format(
        response.document_sentiment.score))
    # print(
    #     u"Magnitud del sentimiento del documento: {}".format(
    #         response.document_sentiment.magnitude
    #     )
    # )
    # Get sentiment for all sentences in the document
    for sentence in response.sentences:
        print(u"Texto: {}".format(sentence.text.content))
        print(u"Puntuación del sentimiento de la frase: {}".format(
            sentence.sentiment.score))
        # print(u"Magnitud del sentimiento de la frase: {}".format(
        #     sentence.sentiment.magnitude))

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Idioma del texto: {}".format(response.language))


classify(nextText)
sample_analyze_sentiment(nextText)
