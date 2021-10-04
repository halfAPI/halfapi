http 127.0.0.1:3000/halfapi/whoami Authorization:$(http 127.0.0.1:3000/authentication/check email=malves password=papa|jq -r '.token')
