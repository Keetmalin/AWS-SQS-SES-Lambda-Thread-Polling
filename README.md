# AWS-SQS-SES-Lambda-Thread-Polling

This example illustrates a scenario where an AWS SQS Queue, AWS SES and a Lambda function, work together to deliver messages from SQS to SES. The code given in "sqs-microservice-python3.py" file contains the Lambda code to be run in Python3 environment.

This code is to adhere the Limitations in SES when sending multiple emails at the same time. <a href="https://docs.aws.amazon.com/ses/latest/DeveloperGuide/limits.html">Limitations in AWS SES</a>

<b>Step 1</b>: Add the code to a Lamda function running on Python3

<b>Step 2</b>: In the code, change the respective parameters to support your requirement

<ul>
<li>QUEUE_URL: AWS SQS Queue URL: eg: 'https: //sqs.region.amazonaws.com/endpoint value/queue_name'</li>
<li>LAMBDA_RUN_TIME: Time the Lambda will be runnig before shutting down. (max 5 mins)</li>
<li>THRESHOLD: The time in mili-seconds to keep within a second, to ensure SES limitations are not exceeded.</li>
<li>CHARSET: charset supported in messages</li>
<li>THREAD_COUNT: number of threads to be invoked concurrently (since lambda is running on two cores, 4 thread is ideal)</li>
<li>SES_SEND_RATE: the limitation that SES has, on sending multiple emails at once.</li>
</ul>
  
<b>Step 3</b>: Add CloudWatch rules to invoke the Lambda function every few minutes
