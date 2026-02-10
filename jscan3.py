#!/usr/bin/python3
import sys
import requests
import argparse
from bs4 import BeautifulSoup
import threading
import time

dbarray = []
url = ""
useragentdesktop = {
    "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Accept-Language": "it"
}
timeoutconnection = 5
pool = None
swversion = "0.5beta"


def hello():
    print("-------------------------------------------")
    print("             Joomla Scan                  ")
    print("   Usage: python joomlascan.py <target>    ")
    print(f"    Version {swversion} - Database Entries {len(dbarray)}")
    print("         created by Andrea Draghetti       ")
    print("-------------------------------------------")


def load_component():
    with open("comptotestdb.txt", "r") as f:
        for line in f:
            dbarray.append(line.strip())


def check_url(url, path="/"):
    try:
        r = requests.get(url + path, headers=useragentdesktop, timeout=timeoutconnection)
        return r.status_code if r.headers.get("content-length") != "0" else 404
    except:
        return None


def check_readme(url, component):
    paths = [
        f"/components/{component}/README.txt",
        f"/components/{component}/readme.txt",
        f"/components/{component}/README.md",
        f"/components/{component}/readme.md",
        f"/administrator/components/{component}/README.txt",
        f"/administrator/components/{component}/readme.txt",
        f"/administrator/components/{component}/README.md",
        f"/administrator/components/{component}/readme.md",
    ]
    for p in paths:
        if check_url(url, p) == 200:
            print(f"\t README file found \t > {url}{p}")


def check_license(url, component):
    paths = [
        f"/components/{component}/LICENSE.txt",
        f"/components/{component}/license.txt",
        f"/administrator/components/{component}/LICENSE.txt",
        f"/administrator/components/{component}/license.txt",
        f"/components/{component}/{component[4:]}.xml",
        f"/administrator/components/{component}/{component[4:]}.xml",
    ]
    for p in paths:
        if check_url(url, p) == 200:
            print(f"\t LICENSE file found \t > {url}{p}")


def check_changelog(url, component):
    paths = [
        f"/components/{component}/CHANGELOG.txt",
        f"/components/{component}/changelog.txt",
        f"/administrator/components/{component}/CHANGELOG.txt",
        f"/administrator/components/{component}/changelog.txt",
    ]
    for p in paths:
        if check_url(url, p) == 200:
            print(f"\t CHANGELOG file found \t > {url}{p}")


def check_manifest(url, component):
    paths = [
        f"/components/{component}/MANIFEST.xml",
        f"/components/{component}/manifest.xml",
        f"/administrator/components/{component}/MANIFEST.xml",
        f"/administrator/components/{component}/manifest.xml",
    ]
    for p in paths:
        if check_url(url, p) == 200:
            print(f"\t MANIFEST file found \t > {url}{p}")


def scanner(url, component):
    global pool
    try:
        if check_url(url, f"/index.php?option={component}") == 200:
            print(f"Component found: {component}\t > {url}/index.php?option={component}")

        elif check_url(url, f"/components/{component}/") == 200:
            print(f"Component found: {component}\t > {url}/index.php?option={component}")
            print("\t But possibly it is not active or protected")

        elif check_url(url, f"/administrator/components/{component}/") == 200:
            print(f"Component found: {component}\t > {url}/index.php?option={component}")
            print("\t On the administrator components")

        else:
            return

        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_manifest(url, component)

    finally:
        pool.release()


def main(argv):
    global pool

    load_component()
    hello()

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("-t", "--threads", default=10, type=int)
    parser.add_argument("-v", "--version", action="version", version=swversion)
    args = parser.parse_args()

    url = args.url.rstrip("/")
    if not url.startswith(("http://", "https://")):
        print("You must insert http:// or https://")
        sys.exit(1)

    pool = threading.BoundedSemaphore(args.threads)

    print(f"\nTesting Joomla website: {url}\n")

    for component in dbarray:
        pool.acquire()
        threading.Thread(target=scanner, args=(url, component), daemon=True).start()

    while threading.active_count() > 1:
        time.sleep(0.2)

    print("\nScan finished!\n")


if __name__ == "__main__":
    main(sys.argv)
