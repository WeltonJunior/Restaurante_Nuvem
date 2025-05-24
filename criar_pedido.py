import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb', endpoint_url='http://10.255.255.254:4566')
table = dynamodb.Table('Pedidos')

sqs = boto3.client('sqs', endpoint_url='http://10.255.255.254:4566')
queue_url = sqs.get_queue_url(QueueName='FilaPedidos')['QueueUrl']

def lambda_handler(event, context):
    # Recebe o pedido (no evento HTTP direto na Lambda)
    pedido = json.loads(event['body'])

    # Gera ID único para o pedido
    pedido_id = str(uuid.uuid4())

    # Insere pedido no DynamoDB
    item = {
        'id': pedido_id,
        'cliente': pedido['cliente'],
        'itens': pedido['itens'],
        'mesa': pedido['mesa'],
        'status': 'recebido'
    }
    table.put_item(Item=item)

    # Envia o id do pedido para a fila SQS
    sqs.send_message(QueueUrl=queue_url, MessageBody=pedido_id)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Pedido criado', 'id': pedido_id})
    }
