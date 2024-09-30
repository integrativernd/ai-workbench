echo ${GOOGLE_CREDENTIALS} > /app/credentials.json
base64 -d --input=${TEMPORAL_MTLS_TLS_CERT_VALUE} > /app/certs/ca.pem
base64 -d --input=${TEMPORAL_MTLS_TLS_KEY_VALUE} > /app/certs/ca.key