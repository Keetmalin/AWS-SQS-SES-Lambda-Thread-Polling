
# coding=utf-8
import boto3
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

message_queue = boto3.client('sqs')
amazon_ses = boto3.client('ses')
stop_process = False

# set these at environment variables
QUEUE_URL = '<queue email>'
LAMBDA_RUN_TIME = 250000
THRESHOLD = 100
CHARSET = 'UTF-8'
THREAD_COUNT = 4
SES_SEND_RATE = 14
###


def get_time_millis():
    """
    This function returns the current time in milliseconds
    :return current_time : the current time in milliseconds
    """
    current_time = int(round(time.time() * 1000))
    return current_time


def receive_messages():
    """
    This function retrieves messages from SQS
    :return response: dictionary of messages received from SQS
    """
    response = message_queue.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=1,
        WaitTimeSeconds=0
    )

    return response


def send_email(text):
    """
    This function will send an email through AWS SWS
    :param text: the message to be sent through SES
    :return response: the response received from SES
    """
    response = amazon_ses.send_email(
        Source='<email address>',
        Destination={
            'ToAddresses': [
                '<email address>',
            ]
        },
        Message={
            'Subject': {
                'Data': 'this is a test email',
                'Charset': CHARSET
            },
            'Body': {
                'Text': {
                    'Data': 'just a test' + text,
                    'Charset': CHARSET
                }
            }
        }
    )

    return response


def delete_message(receipt_handle):
    """
    This function will delete the specified message from SQS
    :param receipt_handle: this is the handle of the message to be deleted
    """
    message_queue.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )
    print("Message deleted")


def process_message(message):
    """
    This function will process each message using a separate thread
    :param message: the message object that needs to be processed
    """

    try:
        sendEmail(message['Body'])
        delete_message(message['ReceiptHandle'])
    except Exception:
        print("Exception caught")


def handle_sqs_messages(pool):
    """
    This function controls the maximum send rate per second
    :param pool: the thread pool
    """
    start_time = get_time_millis()
    counter = 0

    while counter < SES_SEND_RATE and get_time_millis() - start_time + THRESHOLD < 1000:

        response = receive_messages()
        global stop_process

        if response.get('Messages') is None:
            stop_process = True
            break

        messages = response['Messages']

        if SES_SEND_RATE - counter - len(messages) < 0:
            pool.map(process_message, messages[:(SES_SEND_RATE - counter)])
            counter += len(messages)
        else:
            pool.map(process_message, messages)
            counter += len(messages)

        if len(messages) < 10:
            stop_process = True
            break

    pool.close()
    pool.join()


    if get_time_millis() - start_time - 1000 + 50 < 0:
        time.sleep(get_time_millis() - start_time - 1000 + 50)


def handle_lambda_process():
    """
    This function handles the process of Lambda and stops it when needed
    """
    overall_start = get_time_millis()

    while not stop_process and get_time_millis() - overall_start < LAMBDA_RUN_TIME:
        handle_sqs_messages(ThreadPool(THREAD_COUNT))


def lambda_handler(event, context):
    """
    This is the handler of the lambda function

    :param event: event that triggers the lambda function
    :param context: the context in which the lambda is being run
    :return: the final status of the process
    """
    handle_lambda_process()

    return 'Lambda Process Completed'


lambda_handler("", "")
