#!/usr/bin/python3
import sys
import requests
import argparse
from bs4 import BeautifulSoup
import threading
import time

dbarray = []
url = ""
useragentdesktop = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
                    "Accept-Language": "it"}
timeoutconnection = 5
pool = None
swversion = "0.5beta"


def hello():
    print("-------------------------------------------")
    print("      	     Joomla Scan                  ")
    print("   Usage: python joomlascan.py <target>    ")
    print(f"    Version {swversion} - Database Entries {len(dbarray)}")
    print("         created by Andrea Draghetti       ")
    print("-------------------------------------------")


def load_component():
    with open("comptotestdb.txt", "r") as f:
        for line in f:
            dbarray.append(line.strip())  # Strip trailing newline


def check_url(url, path="/"):
    fullurl = url + path
    try:
        conn = requests.get(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        if conn.headers.get("content-length") != "0":
            return conn.status_code
        else:
            return 404
    except Exception:
        return None


def check_url_head_content_length(url, path="/"):
    fullurl = url + path
    try:
        conn = requests.head(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        return conn.headers.get("content-length")
    except Exception:
        return None


def check_readme(url, component):
    if check_url(url, "/components/" + component + "/README.txt") == 200:
        print(f"\t README file found \t > {url}/components/{component}/README.txt")

    if check_url(url, "/components/" + component + "/readme.txt") == 200:
        print(f"\t README file found \t > {url}/components/{component}/readme.txt")

    if check_url(url, "/components/" + component + "/README.md") == 200:
        print(f"\t README file found \t > {url}/components/{component}/README.md")

    if check_url(url, "/components/" + component + "/readme.md") == 200:
        print(f"\t README file found \t > {url}/components/{component}/readme.md")

    if check_url(url, "/administrator/components/" + component + "/README.txt") == 200:
        print(f"\t README file found \t > {url}/administrator/components/{component}/README.txt")

    if check_url(url, "/administrator/components/" + component + "/readme.txt") == 200:
        print(f"\t README file found \t > {url}/administrator/components/{component}/readme.txt")

    if check_url(url, "/administrator/components/" + component + "/README.md") == 200:
        print(f"\t README file found \t > {url}/administrator/components/{component}/README.md")

    if check_url(url, "/administrator/components/" + component + "/readme.md") == 200:
        print(f"\t README file found \t > {url}/administrator/components/{component}/readme.md")


def check_license(url, component):
    if check_url(url, "/components/" + component + "/LICENSE.txt") == 200:
        print(f"\t LICENSE file found \t > {url}/components/{component}/LICENSE.txt")

    if check_url(url, "/components/" + component + "/license.txt") == 200:
        print(f"\t LICENSE file found \t > {url}/components/{component}/license.txt")

    if check_url(url, "/administrator/components/" + component + "/LICENSE.txt") == 200:
        print(f"\t LICENSE file found \t > {url}/administrator/components/{component}/LICENSE.txt")

    if check_url(url, "/administrator/components/" + component + "/license.txt") == 200:
        print(f"\t LICENSE file found \t > {url}/administrator/components/{component}/license.txt")

    if check_url(url, f"/components/{component}/{component[4:]}.xml") == 200:
        print(f"\t LICENSE file found \t > {url}/components/{component}/{component[4:]}.xml")

    if check_url(url, f"/administrator/components/{component}/{component[4:]}.xml") == 200:
        print(f"\t LICENSE file found \t > {url}/administrator/components/{component}/{component[4:]}.xml")


def check_changelog(url, component):
    if check_url(url, "/components/" + component + "/CHANGELOG.txt") == 200:
        print(f"\t CHANGELOG file found \t > {url}/components/{component}/CHANGELOG.txt")

    if check_url(url, "/components/" + component + "/changelog.txt") == 200:
        print(f"\t CHANGELOG file found \t > {url}/components/{component}/changelog.txt")

    if check_url(url, "/administrator/components/" + component + "/CHANGELOG.txt") == 200:
        print(f"\t CHANGELOG file found \t > {url}/administrator/components/{component}/CHANGELOG.txt")

    if check_url(url, "/administrator/components/" + component + "/changelog.txt") == 200:
        print(f"\t CHANGELOG file found \t > {url}/administrator/components/{component}/changelog.txt")


def check_manifest(url, component):
    if check_url(url, "/components/" + component + "/MANIFEST.xml") == 200:
        print(f"\t MANIFEST file found \t > {url}/components/{component}/MANIFEST.xml")

    if check_url(url, "/components/" + component + "/manifest.xml") == 200:
        print(f"\t MANIFEST file found \t > {url}/components/{component}/manifest.xml")

    if check_url(url, "/administrator/components/" + component + "/MANIFEST.xml") == 200:
        print(f"\t MANIFEST file found \t > {url}/administrator/components/{component}/MANIFEST.xml")

    if check_url(url, "/administrator/components/" + component + "/manifest.xml") == 200:
        print(f"\t MANIFEST file found \t > {url}/administrator/components/{component}/manifest.xml")


def index_of(url, path="/"):
    fullurl = url + path
    try:
        page = requests.get(fullurl, headers=useragentdesktop, timeout=timeoutconnection)
        soup = BeautifulSoup(page.text, "html.parser")
        if soup.title:
            titlepage = soup.title.string
            if "Index of /" in titlepage:
                return True
        return False
    except:
        return False


def scanner(url, component):
    if check_url(url, "/index.php?option=" + component) == 200:
        print(f"Component found: {component}\t > {url}/index.php?option={component}")
        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_manifest(url, component)

    elif check_url(url, "/components/" + component + "/") == 200:
        print(f"Component found: {component}\t > {url}/index.php?option={component}")
        print("\t But possibly it is not active or protected")

        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_manifest(url, component)

    elif check_url(url, "/administrator/components/" + component + "/") == 200:
        print(f"Component found: {component}\t > {url}/index.php?option={component}")
        print("\t On the administrator components")
        check_readme(url, component)
        check_license(url, component)
        check_changelog(url, component)
        check_manifest(url, component)

    pool.release()


def main(argv):
    load_component()
    hello()

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--url", action="store", dest="url", help="The Joomla URL/domain to scan.")
        parser.add_argument("-t", "--threads", action="store", dest="threads",
                            help="The number of threads to use when multi-threading requests (default: 10).")
        parser.add_argument("-v", "--version", action="version", version="%(prog)s " + swversion)

        arguments = parser.parse_args()
    except:
        sys.exit(1)

    if arguments.url:
        url = arguments.url
        if not url.startswith(("http://", "https://")):
            print("You must insert http:// or https:// protocol\n")
            sys.exit(1)

        if url.endswith("/"):
            url = url[:-1]
    else:
        print("")
        parser.parse_args(["-h"])
        sys.exit(1)

    if arguments.threads:
        try:
            numthreads = int(arguments.threads)
        except ValueError:
            print("You must provide an integer value for the number of threads\n")
            sys.exit(1)
    else:
        numthreads = 10

    pool = threading.BoundedSemaphore(value=numthreads)

    print(f"\nTesting Joomla website: {url}\n")

    for component in dbarray:
        pool.acquire()
        t = threading.Thread(target=scanner, args=(url, component))
        t.start()

    time.sleep(1)
    pool.acquire()

    print("\nScan finished!\n")


if __name__ == "__main__":
    main(sys.argv)
