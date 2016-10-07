#!/bin/bash

if [ $# -lt 1 ]; then
    exit 1
fi

SW_PATH=/home/pi/swfarereducer
KEY_PATH=$SW_PATH/keys
name=""
passphrase=""
private_key=""
public_key=""
dat_file=""
txt_file=""

mkdir -p $KEY_PATH

while getopts ":n:p:" opt;
do
    case $opt in
    n)
		name=$OPTARG
		;;
	p)
		passphrase=$OPTARG
		;;
	\?)
        echo "ERROR: Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "ERROR: Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

private_key=${KEY_PATH}/private_${name}_key.pem
public_key=${KEY_PATH}/public_${name}_key.pem
dat_file=${KEY_PATH}/encrypt_${name}.dat
txt_file=${KEY_PATH}/${name}.txt

# Generate private/public keys for sudo and login commands
openssl genrsa -out $private_key 1024 > /dev/null 2>&1
openssl rsa -in $private_key -out $public_key -outform PEM -pubout > /dev/null 2>&1
echo "$passphrase" > $txt_file
openssl rsautl -encrypt -inkey $public_key -pubin -in $txt_file -out $dat_file > /dev/null 2>&1

rm -f $public_key $txt_file
sync

openssl rsautl -decrypt -inkey $private_key -in $dat_file > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "ERROR: Failed to create keys"
else
	echo "Success!"
fi
