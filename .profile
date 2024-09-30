echo ${GOOGLE_CREDENTIALS} > /app/credentials.json

echo ${TEMPORAL_MTLS_TLS_CERT_VALUE} > /app/certs/ca.txt
echo ${TEMPORAL_MTLS_TLS_KEY_VALUE} > /app/certs/ca.key.txt

base64 -d /app/certs/ca.txt > /app/certs/ca.pem
base64 -d /app/certs/ca.key.txt > /app/certs/ca.key