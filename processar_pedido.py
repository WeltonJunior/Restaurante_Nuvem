import boto3
import json
import traceback
import time

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://10.255.255.254:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)
table = dynamodb.Table('Pedidos')

s3 = boto3.client(
    's3',
    endpoint_url='http://10.255.255.254:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)
bucket_name = 'bucketcomprovantes'
sns = boto3.client(
    'sns',
    endpoint_url='http://10.255.255.254:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

def lambda_handler(event, context):
    print("Evento recebido:", json.dumps(event, indent=2))
    try:
        for record in event.get('Records', []):
            pedido_id = record['body']
            print(f"Processando pedido ID: {pedido_id}")

            # Buscar pedido no DynamoDB
            res = table.get_item(Key={'id': pedido_id})
            pedido = res.get('Item')

            if not pedido:
                print(f"Pedido {pedido_id} não encontrado no DynamoDB.")
                continue

            # Simula geração do PDF
            pdf_content = (
                f"Comprovante do Pedido {pedido_id}\n"
                f"Cliente: {pedido['cliente']}\n"
                f"Itens: {pedido['itens']}\n"
                f"Mesa: {pedido['mesa']}\n"
                f"Status: {pedido['status']}\n"
            )
            print("Gerando PDF simulado para o pedido...")

            # Salvar no S3
            s3.put_object(
                Bucket=bucket_name,
                Key=f"{pedido_id}.pdf",
                Body=pdf_content.encode('utf-8')
            )
            print(f"PDF do pedido {pedido_id} salvo no bucket {bucket_name}.")

            # Atualizar status no DynamoDB
            table.update_item(
                Key={'id': pedido_id},
                UpdateExpression="set #s = :v",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={':v': 'processado'}
            )
            print(f"Status do pedido {pedido_id} atualizado para 'processado'.")

            sns.publish(
                TopicArn='arn:aws:sns:us-east-1:000000000000:PedidosConcluidos',
                Subject='Pedido Pronto!',
                Message=f'Novo pedido concluído: {pedido_id}'
            )
            print(f"Notificação SNS enviada para o pedido {pedido_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processamento concluído'})
        }

    except Exception as e:
        print("Erro durante o processamento:")
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
