import os, logging, datetime, argparse

logger = logging.getLogger(__name__)

def parse() -> argparse.Namespace:
    '''
    Function: parse()
    Description: Parses command line inputs at program start
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('server',type=str,help='SMS Server')
    return parser.parse_args()

def main():
    args = parse()
    user_input = input('Please provide your username: ').split()
    username = user_input[0] if user_input else None
    if username:
        os.makedirs('../../../logs', exist_ok=True)
        log_name = f'../../../logs/{username}-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.txt'
        logging.basicConfig(filename=log_name, level=logging.INFO,
                            format="%(levelname)s %(name)s %(threadName)s {0} %(message)s".format(username))

if __name__ == '__main__':
    main()
