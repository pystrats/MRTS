import sys
from ..screener import screener


def main(args):
    
    n_args = len(args) - 1
    incorrect_call = False
    if n_args != 1:
        incorrect_call = True
    if n_args == 1:
        try:
            account = float(args[1])
        except:
            incorrect_call = True
    if incorrect_call:
        print('\nValid calls:\n\nmrts [ACCOUNT_VALUE_IN_USD]\n')
        sys.exit()

    exit_code = screener.Screener(account)
