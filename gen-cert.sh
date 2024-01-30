#!/bin/bash

TEMP_DIR=$1
USERNAME=$2
PASSWORD=$3

CA_KEY_PATH="$TEMP_DIR/caKey.pem"
CA_CERT_PATH="$TEMP_DIR/caCert.pem"



CLIENT_CERT_PATH="$TEMP_DIR/${USERNAME}_cert.pem"
CLIENT_KEY_PATH="$TEMP_DIR/${USERNAME}_key.pem"
P12_FILE_PATH="$TEMP_DIR/${USERNAME}.p12"

# Make the CA certificate (known as root or self-signed)
ipsec pki --gen --outform pem > $CA_KEY_PATH
ipsec pki --self \
    --in $CA_KEY_PATH \
    --dn "CN=VPN CA" \
    --ca --outform pem > $CA_CERT_PATH

echo "Root CA certification: "
CA_CERT_BASE64=$(openssl x509 -in $CA_CERT_PATH -outform der | base64)
echo $CA_CERT_BASE64
echo "Copied to clipboard -> paste this into the Gateway Point2site configuration."
echo $CA_CERT_BASE64 | pbcopy


echo "Proceed to make the client certificate"
# Make the signed client certificate

ipsec pki --gen --outform pem > $CLIENT_KEY_PATH
ipsec pki --pub --in $CLIENT_KEY_PATH | ipsec pki --issue --cacert $CA_CERT_PATH \
    --cakey $CA_KEY_PATH \
    --dn "CN=${USERNAME}" \
    --san "${USERNAME}" \
    --flag clientAuth \
    --outform pem > $CLIENT_CERT_PATH

openssl pkcs12 -in $CLIENT_CERT_PATH \
    -inkey $CLIENT_KEY_PATH \
    -certfile $CA_CERT_PATH \
    -export -out $P12_FILE_PATH \
    -password "pass:${PASSWORD}"

openssl pkcs12 -in $P12_FILE_PATH -nodes -out "$TEMP_DIR/profileinfo.txt"
