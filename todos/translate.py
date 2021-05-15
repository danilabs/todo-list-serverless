import os
import json
import logging

from todos import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')
translateaws = boto3.client('translate')
comprehend = boto3.client('comprehend')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# method comprehendText
def comprehendText(data):
    try:
        response = comprehend.detect_dominant_language(Text=data)
        return response['Languages'][0]['LanguageCode']
    except Exception as e:
        logger.error(e)
        raise Exception("[ErrorMessageComprehend]: " + str(e))

# method translateText
def translateText(data, source, target):
    try:
        response = translateaws.translate_text(
            Text=data,
            SourceLanguageCode='auto',
            TargetLanguageCode=target
            )
        return response['TranslatedText']
    except Exception as e:
        logger.error(e)
        raise Exception("[ErrorMessageTranslate]: " + str(e))


# method translate
def translate(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    lang = event['pathParameters']['lang']

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    # sourceLang = comprehendText(result['Item']['text'])
    # None sourceLang, uses auto
    text = translateText(result['Item']['text'], None, lang)
    r = result['Item']

    r.update({'lang': lang, 'detectedLang': 'auto', 'text': text)
    response = {
        "statusCode": 200,
        "body": json.dumps(r, cls=decimalencoder.DecimalEncoder)
    }

    return response
