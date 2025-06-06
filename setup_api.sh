#!/bin/bash
set -e

# Variáveis
ENDPOINT_URL="http://localhost:4566"
LAMBDA_NAME="CriarPedido"
API_NAME="RestauranteAPI"
STAGE_NAME="prod"

echo "Criando API REST..."
API_ID=$(aws --endpoint-url=$ENDPOINT_URL apigateway create-rest-api --name $API_NAME --query 'id' --output text)
echo "API criada com ID: $API_ID"

echo "Obtendo recurso raiz '/' da API..."
ROOT_ID=$(aws --endpoint-url=$ENDPOINT_URL apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)
echo "Recurso raiz ID: $ROOT_ID"

echo "Criando recurso /pedidos..."
RESOURCE_ID=$(aws --endpoint-url=$ENDPOINT_URL apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_ID --path-part pedidos --query 'id' --output text)
echo "Recurso /pedidos criado com ID: $RESOURCE_ID"

echo "Criando método POST para /pedidos..."
aws --endpoint-url=$ENDPOINT_URL apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --authorization-type NONE

echo "Integrando método POST com Lambda $LAMBDA_NAME..."
LAMBDA_ARN="arn:aws:lambda:us-east-1:000000000000:function:$LAMBDA_NAME"
aws --endpoint-url=$ENDPOINT_URL apigateway put-integration --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

echo "Adicionando permissão para API Gateway invocar Lambda..."
aws --endpoint-url=$ENDPOINT_URL lambda add-permission --function-name $LAMBDA_NAME --statement-id apigateway-permission --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:000000000000:$API_ID/*/POST/pedidos" || echo "Permissão já existe"

echo "Criando deployment na stage $STAGE_NAME..."
aws --endpoint-url=$ENDPOINT_URL apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE_NAME

echo ""
echo "Setup concluído!"
echo "Endpoint disponível em:"
echo "http://localhost:4566/restapis/$API_ID/$STAGE_NAME/_user_request_/pedidos"
