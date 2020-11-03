import os
import sys
import getopt
import hmac
import hashlib
import urllib.request
import urllib.parse
import json
import getpass
import _thread

class blih:
    def __init__(self, baseurl='https://blih.epitech.eu/', user=None, token=None, verbose=False, user_agent='blih-1.7'):
        self._baseurl = baseurl
        self._user = user
        if token:
            self._token = token
        else:
            self.token_calc()
        if self._user == None:
           self._user = os.environ.get('BLIH_USER', getpass.getuser())
        self._verbose = verbose
        self._useragent = user_agent

    def token_get(self):
        return self._token

    def token_set(self, token):
        self._token = token

    token = property(token_get, token_set)

    def token_calc(self):
        if 'BLIH_TOKEN' in os.environ and self._user == None:
            self._token = bytes(os.getenv('BLIH_TOKEN'), 'utf8')
        else :
            self._token = bytes(hashlib.sha512(bytes(getpass.getpass(), 'utf8')).hexdigest(), 'utf8')

    def sign_data(self, data=None):
        signature = hmac.new(self._token, msg=bytes(self._user, 'utf8'), digestmod=hashlib.sha512)
        if data:
            signature.update(bytes(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), 'utf8'))

        signed_data = {'user' : self._user, 'signature' : signature.hexdigest()}
        if data != None:
            signed_data['data'] = data

        return signed_data

    def request(self, resource, method='GET', content_type='application/json', data=None, url=None):
        signed_data = self.sign_data(data)

        if url:
            req = urllib.request.Request(url=url, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
        else:
            req = urllib.request.Request(url=self._baseurl + resource, method=method, data=bytes(json.dumps(signed_data), 'utf8'))
        req.add_header('Content-Type', content_type)
        req.add_header('User-Agent', self._useragent)

        try:
            f = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print ('HTTP Error ' + str(e.code))
            data = json.loads(e.read().decode('utf8'))
            print ("Error message : '" + data['error'] + "'")
            sys.exit(1)

        if f.status == 200:
            try:
                data = json.loads(f.read().decode('utf8'))
            except:
                print ("Can't decode data, aborting")
                sys.exit(1)
            return (f.status, f.reason, f.info(), data)

        print ('Unknown error')
        sys.exit(1)

    def repo_list(self):
        status, reason, headers, data = self.request('/repositories', method='GET')
        for i in data['repositories']:
            print (i)
        return data['repositories']

def repository(args, baseurl, user, token, verbose, user_agent):
    if len(args) == 0:
        usage_repository()
    if args[0] == 'list':
        if len(args) != 1:
            usage_repository()
        handle = blih(baseurl=baseurl, user=user, token=token, verbose=verbose, user_agent=user_agent)
        return handle.repo_list()

if __name__ == "__main__":
    verbose = False
    user = sys.argv[1]
    baseurl = 'https://blih.epitech.eu/'
    token = None
    user_agent = 'blih-1.7'

    repos = repository(["list"], baseurl, user, token, verbose, user_agent)
    for repo in repos:
        _thread.start_new_thread( os.system, ("git clone git@git.epitech.eu:" + user + "/" + repo, ))
    print("Cloning starting, do not close your terminal!")
