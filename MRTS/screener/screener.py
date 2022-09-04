import requests, sys, math, copy
from datetime import datetime, date

from ..config.config import SYMBOL_DEFINITIONS, MONTHS, MONTH_CODES

# SETTINGS #############################
MAX_CONTANGO = 15
MIN_BACKWARDATION = 0
########################################


class QuoteQuery():
    def __init__(self, symbol, mintick, tickvalue, hname, margin):
        self.endpoint    = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols='
        self.header      = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        self.mintick     = mintick
        self.tickvalue   = tickvalue
        self.symbol      = symbol
        self.hname       = hname
        self.margin      = margin
        self.result      = {}
        self.execute()

    def execute(self):
        try:
            self.result = requests.get(self.endpoint + self.symbol + '=f', headers=self.header).json()
        except:
            raise RuntimeError("Failed to execute query. Exiting...")
            sys.exit()


class ChartQuery():
    def __init__(self, symbol, definition):
        self.endpoint       = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols='
        self.header         = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        self.symbol         = symbol
        self.root           = definition.root
        self.mintick        = definition.mintick
        self.tickvalue      = definition.tickvalue
        self.hname          = definition.hname
        self.margin         = definition.margin
        self.price          = None
        self.name           = None
        self.expiration     = None
        self.expirationDate = None
        self.iyield          = None

        self.execute()
        self.success        = self.issuccess()


    def execute(self):
        result = requests.get(self.endpoint + self.symbol, headers=self.header)
        if result.status_code == 200:
            r = result.json()
            if r['quoteResponse']['error'] == None and len(r['quoteResponse']['result']) > 0:
                try:
                    self.price = float(r['quoteResponse']['result'][0]['regularMarketPrice'])
                except:
                    pass
                try:
                    self.name = r['quoteResponse']['result'][0]['shortName']
                except:
                    pass
                try:
                    self.expiration = int(r['quoteResponse']['result'][0]['expireDate'])
                except:
                    pass
                try:
                    self.expirationDate = r['quoteResponse']['result'][0]['expireIsoDate']
                except:
                    pass

    def issuccess(self):
        if self.price and self.name and self.expiration and self.expirationDate:
            return True
        return False


class SymbolDefinition():
    def __init__(self, q):
        self.root = q.symbol
        self.mintick = q.mintick
        self.tickvalue = q.tickvalue
        self.hname = q.hname
        self.margin = q.margin
        self.price = self.getprice(q.result)
        self.exchangeCode = self.exchange(q.result)
        self.frontMonth = self.front(q.result)
        self.name = self.contractname(q.result)
        self.frontExpiration = self.expiration(q.result)
        self.year = self.getyear(q.result)

    def exchange(self, q):
        try:
            return q['quoteResponse']['result'][0]['exchange']
        except:
            raise ValueError(q, "\nExchange code missing")

    def getprice(self, q):
        try:
            return float(q['quoteResponse']['result'][0]['regularMarketPrice'])
        except:
            raise ValueError(q, "\nPrice is missing")

    def front(self, q):
        try:
            return q['quoteResponse']['result'][0]['underlyingExchangeSymbol'][3] if self.root in ["NKD", "BTC", "LBS"] else q['quoteResponse']['result'][0]['underlyingExchangeSymbol'][2]
        except:
            raise ValueError(q, "\nSymbol code missing")

    def contractname(self, q):
        try:
            return q['quoteResponse']['result'][0]['shortName']
        except:
            raise ValueError(q, "\nContract name missing")

    def getyear(self, q):
        try:
            return int(q['quoteResponse']['result'][0]['underlyingExchangeSymbol'][4:6]) if self.root in ["NKD", "BTC", "LBS"] else int(q['quoteResponse']['result'][0]['underlyingExchangeSymbol'][3:5])
        except:
            raise ValueError(q, "\nExpiration year is missing")

    def expiration(self, q):
        try:
            return int(q['quoteResponse']['result'][0]['expireDate'])
        except:
            raise ValueError(q, "\nExpiration date missing")


def impliedYield(front, next):
    return 100.0 * math.pow(next.price / front.price, (1.0 / ( (datetime.utcfromtimestamp(next.expiration)-datetime.now()).days / 365.25 ) ) ) - 100.0


class Screener():

    def __init__(self, account):
        self.exposure = []
        self.account = account
        self.run()
        self.portfolio()

    def run(self):
        print('\n')
        for _, v in SYMBOL_DEFINITIONS.items():
            print('{} futures'.format(v['name']))
            s = SymbolDefinition(QuoteQuery(v['root'], v['min_tick'], v['tick_value'], v['name'], v['maintenance_margin']))
            frontix = MONTH_CODES.index(s.frontMonth)
            print('Front month is {} {} @ {}'.format(MONTHS[frontix], str(s.year), s.price))
            maxdiff = .0
            pAddition, bestYield = None, None
            for i in range(12):
                if i == frontix:
                    continue
                cY = s.year
                if i < frontix:
                    cY = s.year + 1
                symbol = s.root + MONTH_CODES[i] + str(cY) + '.' + s.exchangeCode
                q = ChartQuery(symbol, s)
                if q.success:
                    iYield = impliedYield(s, q)
                    state = 'backwardation' if iYield < .0 else 'contango'
                    print('{} @ {} implied yield {:.2f}% {}'.format(q.name, q.price, round(iYield, 2), state))
                    premium = max(iYield - MAX_CONTANGO, MIN_BACKWARDATION - iYield)
                    if premium > maxdiff:
                        pAddition = copy.deepcopy(q)
                        bestYield = iYield
                        maxdiff = premium
            if pAddition != None:
                pAddition.iyield = bestYield
                self.exposure.append(pAddition)
                print('{} expiring {} IY {:.2f}% added to portfolio'.format(pAddition.name, pAddition.expirationDate, bestYield))
            print('\n')

    def portfolio(self):
        if self.exposure == []:
            print('NO CONTRACTS SATISFIED PORTFOLIO INCLUSION CRITERIA\n')
            sys.exit()
        else:
            from prettytable import PrettyTable
            N = len(self.exposure)
            posSizeUSD = self.account * 2.0 / N

            T = PrettyTable()
            T.field_names = ["Name", "Expiration", "Code", "Side", "Contracts", "IY %", "Margin (est.) $"]

            portfolio, contractSizes, warnings = [], [], False
            for candidate in self.exposure:
                contractSize = 1.0 * candidate.price * candidate.tickvalue / candidate.mintick
                if int(posSizeUSD / contractSize) > 0:
                    portfolio.append(candidate)
                    contractSizes.append(contractSize)
                else:
                    print('WARNING: Insuffucient capital. {} excluded from portfolio.'.format(candidate.name))
                    warnings = True

            N = len(portfolio)
            if N == 0:
                print('COULD NOT ADD ANY CONTRACTS TO PORTFOLIO. INSUFFICIENT CAPITAL.\n')
                sys.exit()

            positionSizes, posSizeUSD = [], self.account * 2.0 / N
            for i in range(N):
                positionSizes.append( int( posSizeUSD / contractSizes[i] ) )

            if warnings:
                print('\n')
            longExposure, shortExposure, totalMargin = .0, .0, .0
            for i in range(N):
                P = portfolio[i]
                dt = datetime.utcfromtimestamp(P.expiration)
                if P.iyield < .0:
                    longExposure += positionSizes[i] * contractSizes[i]
                else:
                    shortExposure += positionSizes[i] * contractSizes[i]
                totalMargin += P.margin * positionSizes[i]

                T.add_row([ P.hname, dt.strftime("%b") + ' ' + str(dt.year-2000), P.symbol, 'Long' if P.iyield < .0 else 'Short', positionSizes[i], '{:.2f}'.format(P.iyield), '{}'.format(int(P.margin * positionSizes[i])) ])

            longExposure, shortExposure, totalMargin = int(longExposure), int(shortExposure), int(totalMargin)
            print('LONG EXPOSURE:' + '       ${:,.0f}'.format(longExposure) if longExposure > .0 else '')
            print('SHORT EXPOSURE:' + '      ${:,.0f}'.format(shortExposure) if shortExposure > .0 else '')
            print('ESTIMATED MARGIN:' + '    ${:,.0f}'.format(totalMargin))
            print(T)
            print('\n')
