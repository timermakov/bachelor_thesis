#!/bin/bash

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

domains=(timhq.ru www.timhq.ru)
primary_domain=${domains[0]} # Use the first domain for path creation
rsa_key_size=4096
data_path="./data/certbot"
email="ts.ermakov@yandex.ru" 
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

if [ -d "$data_path" ]; then
  read -p "Existing data found for $primary_domain. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi


if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

echo "### Creating dummy certificate for $primary_domain ..."

cert_path="/etc/letsencrypt/live/$primary_domain"

host_cert_path_dir="$data_path/conf/live/$primary_domain"

mkdir -p "$host_cert_path_dir"
docker-compose -f docker-compose-prod.yml "$@" run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$cert_path/privkey.pem' \
    -out '$cert_path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo


echo "### Starting nginx ..."
docker-compose -f docker-compose-prod.yml "$@" up --force-recreate -d nginx
echo

echo "### Deleting dummy certificate for $primary_domain ..."
docker-compose -f docker-compose-prod.yml "$@" run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$primary_domain && \
  rm -Rf /etc/letsencrypt/archive/$primary_domain && \
  rm -Rf /etc/letsencrypt/renewal/$primary_domain.conf" certbot
echo


echo "### Requesting Let's Encrypt certificate for $domains ..."
#Join $domains to -d args
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose -f docker-compose-prod.yml "$@" run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot # Consider removing --force-renewal for normal runs after first success
echo

echo "### Reloading nginx ..."
docker-compose -f docker-compose-prod.yml "$@" exec nginx nginx -s reload
