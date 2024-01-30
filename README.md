Azure VPN Certificate Helper
---

# Overview
This repo contains script to help generate SELF-SIGNED VPN certificate on MacOS. Help a lot when setup a VPN in Azure VNet Gateway.

If you found this repo help, consider give it a star 🌟💫⭐ It will chear me up!

# Requirements 
Dependencies are:
- ipsec (available via homebrew -> https://formulae.brew.sh/formula/strongswan)
- openssl 
- Python >=3.8
- pbcopy (for paste the certificate in clipboard, can turn this off in the bash script if you don't have it)

## python requirements

```
pip install python-dotenv
```

# Usages

```
$ python main.py --help
usage: main.py [-h] {gen,parse} ...

positional arguments:
  {gen,parse}  Subcommand options
    gen        Generate the CA (self-sign) cert and then client cert. All info will be save into _tmp/{timestamp} folder.
    parse      Parse the profileinfo.txt (from the latest subfolder _tmp{timestamp}) into the OpenVPN profile config

optional arguments:
  -h, --help   show this help message and exit

```
## Generate the certs
First, to generate the CA (self-signed) cert, and use that cert to sign another client cert, run

```
$ python main.py gen
```

Result of the above command:    
```
Darwin strongSwan U5.9.11/K22.6.0
University of Applied Sciences Rapperswil, Switzerland
OpenSSL 3.1.2 1 Aug 2023 (Library: OpenSSL 3.1.2 1 Aug 2023)

The temp folder used for saving _tmp/20240130-224143
Root CA certification: 
<MIIC5...so-long-cert-in-base64-here>

Copied to clipboard -> paste this into the Gateway Point2site configuration.
Proceed to make the client certificate
Enter Import Password: 
```

Add the end of the result, you have to manually enter the password. Check the main.py begining section of the script for this variable.

## Parse the client cert into OpenVPN profile

After you paste the CA cert (as base64) into Azure Virtual Network Gatewate (to setup the point-to-site VPN), you will be able to download the VPN profiles. Make sure you have OpenVPN options.

Copied the profile (`vpnprofile.ovpn`) to this directory. Then run:

```
$ python main.py parse
```

Then check the latest folder (in `_tmp/{timestamp}`) for a new parsed and useable `vpnprofile.ovpn.`

# Todos

- Add the option to choose the cert folder to load from.
- Add the option to specify the path to the VPN profile file.

