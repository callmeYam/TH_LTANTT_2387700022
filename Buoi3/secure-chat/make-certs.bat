@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

where openssl >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" set "PATH=C:\Program Files\OpenSSL-Win64\bin;%PATH%"
    if exist "C:\Program Files\Git\usr\bin\openssl.exe" set "PATH=C:\Program Files\Git\usr\bin;%PATH%"
)

mkdir certs\ca 2>nul
mkdir certs\server 2>nul
mkdir certs\client 2>nul

openssl genrsa -out certs\ca\ca.key 2048
openssl req -x509 -new -nodes -key certs\ca\ca.key -sha256 -days 3650 -out certs\ca\ca.crt -config openssl.cnf -extensions v3_ca

openssl genrsa -out certs\server\server.key 2048
openssl req -new -key certs\server\server.key -out certs\server\server.csr -subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=localhost"
openssl x509 -req -in certs\server\server.csr -CA certs\ca\ca.crt -CAkey certs\ca\ca.key -CAcreateserial -out certs\server\server.crt -days 365 -sha256

openssl genrsa -out certs\client\client.key 2048
openssl req -new -key certs\client\client.key -out certs\client\client.csr -subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=client"
openssl x509 -req -in certs\client\client.csr -CA certs\ca\ca.crt -CAkey certs\ca\ca.key -CAcreateserial -out certs\client\client.crt -days 365 -sha256

move certs\ca\ca.srl certs\ca\ca.srl.bak >nul 2>&1

echo.
echo ===============================
echo Certificates created successfully!
echo - CA:     certs\ca\
echo - Server: certs\server\
echo - Client: certs\client\
echo ===============================
pause
