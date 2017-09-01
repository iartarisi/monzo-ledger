# encoding: -utf8-

# Copyright 2017 Ionuț Arțăriși

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime

import babel.numbers
from dateutil.relativedelta import relativedelta
import dateutil.parser
from monzo.monzo import Monzo

# Get this from https://developers.monzo.com/api/playground
ACCESS_TOKEN = ''

MONZO_ACCOUNT = 'Assets:Monzo'
TOPUP_ACCOUNT = 'Assets:Coop'

CATEGORY_MAP = {
    'cash': 'Expenses:Cash',
    'eating_out': 'Expenses:Social:Going Out',
    'shopping': 'Expenses:Shopping',
    'bills': 'Expenses:Bills',
    'general': 'Expenses',
    'groceries': 'Expenses:Everyday:Groceries',
    'holidays': 'Expenses:Vacation',
    'entertainment': 'Expenses:Entertainment',
    'transport': 'Expenses:Everyday:Transportation'
}


if __name__ == '__main__':
    client = Monzo(ACCESS_TOKEN)
    print('Finding your Monzo account...')
    account = client.get_first_account()
    print('Fetching transactions...')
    transactions = client.get_transactions(account['id'])['transactions']

    print('Crunching...')
    today = datetime.date.today()
    this_month = today.replace(day=1)
    next_month = today + relativedelta(months=1)
    for trx in transactions:
        if not trx['settled']:
            # print("Ignoring {} at {}".format(trx['description'], trx['created']))
            continue

        try:
            settled = dateutil.parser.parse(trx['settled'])
        except ValueError as e:
            import pdb; pdb.set_trace()
        if this_month < settled.date() < next_month:
            # TODO replace currency ISO with symbol
            currency = babel.numbers.get_currency_symbol(trx['currency'])
            # amount in ledger format
            amount = '{} {}'.format(currency, trx['amount']/100)
            if trx['is_load']:
                print("""
{date} * {description}
    {topup_account}
    {monzo}  {amount}""".format(
        date=settled.date(),
        description=trx['description'],
        topup_account=TOPUP_ACCOUNT,
        monzo=MONZO_ACCOUNT,
        amount=amount,
    ))
            else:
                print("""
{date} * {description}
    {expenses_account}
    {monzo}  {amount}""".format(
        date=settled.date(),
        description=trx['description'],
        expenses_account=CATEGORY_MAP[trx['category']],
        monzo=MONZO_ACCOUNT,
        amount=amount,
    ))

