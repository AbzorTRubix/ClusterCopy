import os, logging, datetime, argparse
from client import Client
import getpass
import json

GROUP_SIZE = 10

logger = logging.getLogger(__name__)

def fetch_cluster(cluster: str, client: Client) -> dict:
    data = client.api_call('show-simple-cluster',{'name': cluster,
                                                  'show-portals-certificate': True,
                                                  'details-level': 'full',
                                                  'show-advanced-settings': True}).response()['data']
    return data

def fetch_rulebase(client: Client, rulebase: str, size: int,filter = ''):
    result = []
    offset = 0
    num = size
    while(num > 0):
        if num > GROUP_SIZE:
            rules = client.api_call('show-access-rulebase',{'name':rulebase,'show-hits':True,'limit':GROUP_SIZE,'offset':offset,'filter':filter}).response()['data']['rulebase']
        else:
            rules = client.api_call('show-access-rulebase',{'name':rulebase,'show-hits':True,'limit':num,'offset':offset,'filter':filter}).response()['data']['rulebase']
        for rule in rules:
            if 'rulebase' in rule:
                for sect_rule in rule['rulebase']:
                    #TODO - Instead of fetching just name, get name and rule num
                    result.append((sect_rule,rule['name']))
            else:
                result.append((rule,'NO TITLE'))
        num = num - GROUP_SIZE
        offset = offset + GROUP_SIZE
    return result

#NOTE - Similar functionality will be needed for other modules (like NAT)
def fetch_and_add(old_cluster: str, new_cluster: str, client: Client):
    user_input = input('Please provide the package: ').split()
    package = user_input[0] if user_input else None
    results = []
    package_data = client.api_call('show-package',{'name':package}).response()['data']
    acl_packages = [layer['name'] for layer in package_data['access-layers']]
    #TODO - Add new cluster to policy
    for acl in acl_packages:
        rulebase_size = client.api_call('show-access-rulebase',{'name':acl,'limit':1}).response()['data']['total']
        rules = fetch_rulebase(client,acl,rulebase_size,f'installOn:{old_cluster}')
        for rule, _ in rules:
            if 'inner-rules' in rule['filter-match-details'][0]:
                #TODO - Handle Inline Rules
                pass
            #TODO - Add new cluster to unique rules
            pass
    return

def parse() -> argparse.Namespace:
    '''
    Function: parse()
    Description: Parses command line inputs at program start
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('server',type=str,help='SMS Server')
    parser.add_argument('--read',action='store_true',help='enables read only login')
    return parser.parse_args()

def add_cluster(client: Client) -> None:
    #TODO - Add sic-testing code
    user_input = input('Please provide the old cluster object: ').split()
    old_cluster = user_input[0] if user_input else None
    old_config = fetch_cluster(old_cluster,client)
    #TEMP CODE - DELETE LATER
    with open('../../../old_cluster.json',"w") as json_file:
        json.dump(old_config,json_file,indent=4)
    user_input = input('Please provide the new cluster object: ').split()
    new_cluster = user_input[0] if user_input else None
    #TODO - Add other cluster
    #TODO - Add cluster comparison
    fetch_and_add(old_cluster,new_cluster,client)
    return

def main():
    args = parse()
    user_input = input('Please provide your username: ').split()
    username = user_input[0] if user_input else None
    if username:
        os.makedirs('../../../logs', exist_ok=True)
        log_name = f'../../../logs/{username}-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.txt'
        logging.basicConfig(filename=log_name, level=logging.INFO,
                            format="%(levelname)s %(name)s %(threadName)s {0} %(message)s".format(username))
        passwd = getpass.getpass('Enter your password: ')
        client = Client(args.server,username)
        client.login(passwd,False)
        passwd = None
        add_cluster(client)
    client.logout()
    raise SystemExit(0)

if __name__ == '__main__':
    main()
