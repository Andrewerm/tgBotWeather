
NGROK_DOMAIN_NAME=tortoise-integral-totally.ngrok-free.app
YC=/home/andrewerm/yandex-cloud/bin/yc
API-NAME=test-yc-bot
FUNC_NAME=test-yc-func-bot
FUNC_INIT_NAME=test-yc-func-init
SERVICE_ACC=service-account-for-cf
BOT_TOKEN=6427883624:AAEO5gSpb-C-ms5TkTeGqsO7d14cZm7Yse8
BOT_TOKEN_SECRET=e6qogk0nvce1cfcoopnf
YA_WEATHER_TOKEN_SECRET=e6qdfn9d8n3l5476govp
YA_GEO_TOKEN_SECRET=e6qchj74taa4dnn6oed6
WEBHOOK_URL=https://d5dc9bor4t8rikj6uf5b.apigw.yandexcloud.net
WEBHOOK_PATH=/webhook
BUCKET_NAME=tg-bot-bucket-010101
YA_WEATHER=0d859f58-bafe-4bcd-a29a-1dbd1a510ede
YANDEX_GEO=ae46126c-27e7-419c-a44c-c503864debe8

ngrok-start:
	docker run --net=host -i -t -e NGROK_AUTHTOKEN=2cMyUA1w0SNn10qv18g8nFB6o7D_7zVCeyS9WvGwuq7CSveMQ ngrok/ngrok:latest http --domain=tortoise-integral-totally.ngrok-free.app 8001

make-self-signed-cert:
	openssl req -newkey rsa:2048 -sha256 -nodes -keyout SERVERPRIVATE.key -x509 -days 365 -out SERVERPUBLIC.pem -subj "/C=RU/ST=Moscow/L=Moscow/O=Example Company/CN=testhost"

yc-api-create:
	${YC} serverless api-gateway create ${API-NAME} --spec yc-api-gateway.yaml --description "Для телеграмм бота"

yc-api-info:
	${YC} serverless api-gateway get-spec ${API-NAME}

yc-api-delete:
	${YC} serverless api-gateway delete ${API-NAME}

yc-api-update:
	${MAKE} yc-api-delete
	${MAKE} yc-api-create

yc-func-create:
	${YC} serverless function create --name=${FUNC_NAME} --description "Для тестирования telegram бота"

yc-func-webhook-init-create:
	${YC} serverless function create --name=${FUNC_INIT_NAME} --description "Для инициации webhook telegram бота"

yc-func-delete:
	${YC} serverless function delete --name=${FUNC_NAME}

yc-func-info:
	${YC} serverless function get --name=${FUNC_NAME}

yc-func-init-version-create:
	zip src.zip tg_set_webhook.py requirements.txt && \
    ${YC} serverless function version create \
	--function-name=${FUNC_INIT_NAME} \
    --runtime python312 \
    --entrypoint tg_set_webhook.handler \
    --memory 128m \
    --execution-timeout 3s \
    --environment WEBHOOK_URL=${WEBHOOK_URL} \
    --environment WEBHOOK_PATH=${WEBHOOK_PATH} \
    --source-path ./src.zip \
    --service-account-id ajenrq6dn3cjfqj9e5e7 \
    --secret environment-variable=BOT_TOKEN,id=${BOT_TOKEN_SECRET},key=bot_token

yc-func-version-create:
	zip -FSr tgBotWeather.zip .env .env.yandex requirements.txt bot.py tgbot infrastructure -x "*.pyc" && \
	aws s3 cp tgBotWeather.zip s3://${BUCKET_NAME} && \
	${YC} serverless function version create \
	--function-name=${FUNC_NAME} \
    --runtime python312 \
    --entrypoint bot.ya_handler \
    --memory 128m \
    --execution-timeout 3s \
    --package-bucket-name ${BUCKET_NAME} \
    --package-object-name tgBotWeather.zip \
    --service-account-id ajenrq6dn3cjfqj9e5e7 \
    --environment APP_ENV=yandex \
    --secret environment-variable=BOT_TOKEN,id=${BOT_TOKEN_SECRET},key=bot_token \
    --secret environment-variable=YA_WEATHER,id=${YA_WEATHER_TOKEN_SECRET},key=ya_weather_token \
    --secret environment-variable=YA_GEO,id=${YA_GEO_TOKEN_SECRET},key=ya_geo_token

yc-func-init-exec:
	${YC} serverless function invoke --name ${FUNC_INIT_NAME}

yc-view-roles:
	${YC} serverless function list-access-bindings ${FUNC_NAME}

yc-set-role:
	${YC} serverless function add-access-binding \
  --id d4e6qab2lsdmeqoh7psd \
  --service-account-id ajenrq6dn3cjfqj9e5e7 \
  --role editor

yc-access-key-create:
	${YC} iam access-key create --service-account-name ${SERVICE_ACC}

yc-api-key-create:
	${YC} iam api-key create --service-account-name ${SERVICE_ACC}

# service-account-for-cf
# key_id: YCAJEVk_m3OV9MlxW5tztcmZ3
# secret: YCPY85k-c0uf2n1A_Ad3QUA3dDDrKlrvzaBtODgu
# api-key secret: AQVN16FhQ1k6oYKeDLQrDH0FQDtPqeyR-5sLVIy3

yc-service-account-info:
	${YC} iam service-account get ${SERVICE_ACC} --format json


yc-secret-create-bot-token:
	${YC} lockbox secret create \
	--name bot-token \
	--description "Токен телеграмм бота" \
	--payload "[{ 'key': 'bot_token', 'text_value': ${BOT_TOKEN}}]"


yc-secret-create-ya-weather:
	${YC} lockbox secret create \
	--name ya-weather-token \
	--description "Токен Яндекс погоды" \
	--payload "[{ 'key': 'ya_weather_token', 'text_value': ${YA_WEATHER}}]"

yc-secret-create-ya-geo:
	${YC} lockbox secret create \
	--name ya-geo-token \
	--description "Токен Яндекс Геолокации" \
	--payload "[{ 'key': 'ya_geo_token', 'text_value': ${YANDEX_GEO}}]"

yc-secret-list:
	${YC} lockbox secret list

yc-secret-right-for-secret:
	${YC} lockbox secret add-access-binding \
  --id ${BOT_TOKEN_SECRET} \
  --service-account-id ${SERVICE_ACC} \
  --role lockbox.payloadViewer

yc-secret-weather-right-for-secret:
	${YC} lockbox secret add-access-binding \
		  --id ${YA_WEATHER_TOKEN_SECRET} \
		  --service-account-id ${SERVICE_ACC} \
		  --role lockbox.payloadViewer

yc-secret-geo-right-for-secret:
	${YC} lockbox secret add-access-binding \
		  --id ${YA_GEO_TOKEN_SECRET} \
		  --service-account-id ${SERVICE_ACC} \
		  --role lockbox.payloadViewer

check-tg-info:
	curl --request GET -sL --url 'https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo' | jq '.result'

yc-real-time-log:
	${YC} logging read --follow

yc-create-bucket:
	${YC} storage bucket create \
  --name ${BUCKET_NAME} \
  --default-storage-class standard \
  --max-size 100000000

s3-list-files:
	aws s3 ls s3://${BUCKET_NAME}/

yc-delete-bucket:
	${YC} storage bucket delete --name ${BUCKET_NAME}


yc-database-create:
	yc ydb database create tg-db --serverless --description "БД для телеграмм - бота"