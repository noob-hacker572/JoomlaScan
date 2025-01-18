#!/usr/bin/python3
import sys
import requests
import argparse
from bs4 import BeautifulSoup
import threading
import time

dbarray = []
useragentdesktop = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
                    "Accept-Language": "it"}
timeoutconnection = 5
swversion = "0.5beta"
pool = None


def hello():
    print("-------------------------------------------")
    print("              Joomla Scan                  ")
    print("   Usage: python joomlascan.py <target>    ")
    print(f"    Version {swversion} - Database Entries {len(dbarray)}")
    print("         created by Andrea Draghetti       ")
    print("-------------------------------------------")


def load_component():
    with open("comptotestdb.txt", "r") as f:
        for line in f:
            dbarray.append(line.strip())


def check_url(url, path="/"):
    fullurl = url + path
    try:
        response = requests.get(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        if response.status_code == 200 and response.text.strip():
            return True
        return False
    except Exception:
        return False


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
    for path in paths:
        if check_url(url, path):
            print(f"\t[+] README file found: {url}{path}")


def check_license(url, component):
    paths = [
        f"/components/{component}/LICENSE.txt",
        f"/components/{component}/license.txt",
        f"/administrator/components/{component}/LICENSE.txt",
        f"/administrator/components/{component}/license.txt",
        f"/components/{component}/{component[4:]}.xml",
        f"/administrator/components/{component}/{component[4:]}.xml",
    ]
    for path in paths:
        if check_url(url, path):
            print(f"\t[+] LICENSE file found: {url}{path}")


def check_changelog(url, component):
    paths = [
        f"/components/{component}/CHANGELOG.txt",
        f"/components/{component}/changelog.txt",
        f"/administrator/components/{component}/CHANGELOG.txt",
        f"/administrator/components/{component}/changelog.txt",
    ]
    for path in paths:
        if check_url(url, path):
            print(f"\t[+] CHANGELOG file found: {url}{path}")


def check_manifest(url, component):
    paths = [
        f"/components/{component}/MANIFEST.xml",
        f"/components/{component}/manifest.xml",
        f"/administrator/components/{component}/MANIFEST.xml",
        f"/administrator/components/{component}/manifest.xml",
    ]
    for path in paths:
        if check_url(url, path):
            print(f"\t[+] MANIFEST file found: {url}{path}")


def scanner(url, component, pool):
    try:
        target_url = f"{url}/index.php?option={component}"
        if check_url(url, f"/index.php?option={component}"):
            print(f"[+] Component found: {component:<25}: {target_url}")
            check_readme(url, component)
            check_license(url, component)
            check_changelog(url, component)
            check_manifest(url, component)

        elif check_url(url, f"/components/{component}/"):
            print(f"[+] Component partially found: {component:<25}: {url}/components/{component}/")
            print("\t[!] This component may not be active.")
            check_readme(url, component)
            check_license(url, component)
            check_changelog(url, component)
            check_manifest(url, component)

        elif check_url(url, f"/administrator/components/{component}/"):
            print(f"[+] Admin Component found: {component:<25}: {url}/administrator/components/{component}/")
            check_readme(url, component)
            check_license(url, component)
            check_changelog(url, component)
            check_manifest(url, component)

    except Exception as e:
        print(f"[!] Error while scanning {component}: {e}")
    finally:
        pool.release()


def main(argv):
    global pool
    load_component()
    hello()

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", action="store", dest="url", help="The Joomla URL/domain to scan.")
    parser.add_argument("-t", "--threads", action="store", dest="threads",
                        help="The number of threads to use when multi-threading requests (default: 10).")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + swversion)

    arguments = parser.parse_args()

    if not arguments.url:
        print("")
        parser.parse_args(["-h"])
        sys.exit(1)

    url = arguments.url
    if not url.startswith(("http://", "https://")):
        print("You must insert http:// or https:// protocol\n")
        sys.exit(1)

    if url.endswith("/"):
        url = url[:-1]

    try:
        numthreads = int(arguments.threads) if arguments.threads else 10
    except ValueError:
        print("You must provide an integer value for the number of threads\n")
        sys.exit(1)

    pool = threading.BoundedSemaphore(value=numthreads)

    print(f"\nTesting Joomla website: {url}\n")

    threads = []
    for component in dbarray:
        pool.acquire()
        t = threading.Thread(target=scanner, args=(url, component, pool))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\nScan finished!\n")


if __name__ == "__main__":
    main(sys.argv)
