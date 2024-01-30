from glob import glob
from datetime import datetime
import subprocess
import os
import pathlib
from dotenv import load_dotenv

load_dotenv()


def get_latest_save_dir():
    def check_time_format(abs_folder_path: str) -> bool:
        time_str = os.path.basename(os.path.dirname(abs_folder_path))

        try:
            datetime.strptime(time_str, "%Y%m%d-%H%M%S")
            return True
        except Exception as msg:
            pass

        return False

    CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
    all_folders = glob(f"{CURRENT_DIR}/_tmp/*/")
    all_folders = list(
        filter(
            lambda x: check_time_format(x),
            all_folders,
        )
    )
    all_folders = list(sorted(all_folders, reverse=True))

    return all_folders[0]


def check_dependency():
    try:
        # Check ipsec
        subprocess.call(["ipsec", "--version"])

        # Check openssl
        subprocess.call(["openssl", "version"])

    except Exception as msg:
        print(f"Exception: {msg}")
        print(
            """
In MacOS, ipsec can be install via Homebrew.
Openssl should be available in most Linux-based system.
"""
        )
        exit(1)
        pass


def call_gen_script():
    GEN_CERT_PATH = (pathlib.Path(__file__).parent / "gen-cert.sh").resolve()
    assert os.path.exists(
        GEN_CERT_PATH
    ), "Check if the gen-cert.sh helper script is available"

    # NOTE: Username and password. Please note that
    # the password is crucial to generate the client cert.
    USERNAME = os.environ["VPN_CERT_USERNAME"]
    PASSWORD = os.environ["VPN_CERT_PASSWORD"]
    assert isinstance(USERNAME, str), f"Specify your username please"
    assert isinstance(PASSWORD, str), f"Specify your password please"
    # Make unique time string for storage
    TEMP_DIR = datetime.now().strftime("%Y%m%d-%H%M%S")
    TEMP_DIR = f"_tmp/{TEMP_DIR}"
    pathlib.Path(TEMP_DIR).mkdir(exist_ok=True, parents=True)
    print(f"\nThe temp folder used for saving {TEMP_DIR}")

    # TODO: allow default username and password to be change via command prompt
    subprocess.call(
        [
            f"bash",
            GEN_CERT_PATH,
            TEMP_DIR,
            USERNAME,
            PASSWORD,
        ]
    )
    pass


def parse_profile_info():
    # Cert symbol constants
    BEGIN_CERT_SYMBOL = "-----BEGIN CERTIFICATE-----"
    END_CERT_SYMBOL = "-----END CERTIFICATE-----"
    BEGIN_KEY_SYMBOL = "-----BEGIN PRIVATE KEY-----"
    END_KEY_SYMBOL = "-----END PRIVATE KEY-----"
    latest_folder = get_latest_save_dir()
    with open(os.path.join(latest_folder, "profileinfo.txt"), "r") as out:
        text = out.read()
        # First cert is the client cert
        start_idx = text.find(BEGIN_CERT_SYMBOL)
        end_idx = text.find(END_CERT_SYMBOL) + len(END_CERT_SYMBOL)
        client_cert = text[start_idx:end_idx]

        # Only 1 key
        start_idx = text.find(BEGIN_KEY_SYMBOL)
        end_idx = text.find(END_KEY_SYMBOL) + len(END_KEY_SYMBOL)
        client_key = text[start_idx:end_idx]

        pass

    return client_cert, client_key, latest_folder


def parse_config(client_cert, client_key, latest_folder):
    with open("vpnconfig.ovpn") as f:
        text = f.read()

    # NOTE: Delete the `log` command that not working with TunnelBlick
    text = text.replace("log openvpn.log", "")
    text = text.replace("$CLIENTCERTIFICATE", client_cert)
    text = text.replace("$PRIVATEKEY", client_key)

    with open(os.path.join(latest_folder, f"vpnconfig.ovpn"), "w") as f:
        f.write(text)
        pass
    pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(
        dest="subparser_name",
        help="Subcommand options",
    )

    gen_parser = subparser.add_parser(
        "gen",
        help="Generate the CA (self-sign) cert and then client cert. All info will be save into _tmp/{timestamp} folder.",
    )
    parse_parser = subparser.add_parser(
        "parse",
        help="""
Parse the profileinfo.txt (from the latest subfolder _tmp{timestamp}) 
into the OpenVPN profile config""",
    )

    args = parser.parse_args()
    if args.subparser_name == "gen":
        check_dependency()
        call_gen_script()
        exit(0)

    if args.subparser_name == "parse":
        check_dependency()
        client_cert, client_key, latest_folder = parse_profile_info()
        print(f"Found latest_folder: {latest_folder}")
        parse_config(client_cert, client_key, latest_folder)
        exit(0)

    pass
