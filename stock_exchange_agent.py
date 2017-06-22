# coding=utf-8
# !/usr/bin/env python
import json
import random
import string
import sys

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate


class StockExchange(Agent):
    class OpenStockExchange(Behaviour):

        ip = None
        msg = None
        brokers = 0

        stocks = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.stocks = self.stock_generate()

        # Sends signal that stock exchange is opened for business
        def open_stock_exchange(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_open',
                 'data': None,
                 'origin': self.ip
                 }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)

        # Sends stock exchange state to brokers
        def send_stock_exchange_report(self, origin_ip):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_report_data',
                 'data': json.dumps(self.stocks),
                 'origin': self.ip
                 }
            )

            self.send_message(msg_sign_in_to_stock_exchange, origin_ip)

        # Informs owner that his stock has changed price
        def inform_owner_change(self, stock, origin_ip):
            msg_owner_share_change = json.dumps(
                {'request_type': 'stock_share_change',
                 'data': json.dumps(stock),
                 'origin': self.ip
                 }
            )

            self.send_message(msg_owner_share_change, origin_ip)

        # Closes stock exchange, we have our winner
        def send_close_stock_exchange(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_close',
                 'data': None,
                 'origin': self.ip
                 }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)
            self.kill()

        def _process(self):
            self.initialize()
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)

                print request
                # Registering brokers to start stock exchange
                if request['request_type'] == 'stock_sign_in':
                    self.brokers += 1

                    # All brokers are registrated
                    if self.brokers == 1:
                        self.open_stock_exchange()

                # Get stock report
                if request['request_type'] == 'stock_report':
                    self.send_stock_exchange_report(request['origin'])

                # Declare winner and close the stock exchange
                if request['request_type'] == 'stock_win':
                    print "Broker %s got rich. Closing stock exchange..." % request['origin']
                    self.send_close_stock_exchange()
                else:
                    pass

        def broadcast_message(self, message):

            brokers = [1]
            for broker in brokers:
                address = "broker%i@127.0.0.1" % broker
                agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("stock")
                self.msg.setLanguage("eng")
                self.msg.addReceiver(agent)
                self.msg.setContent(message)
                self.myAgent.send(self.msg)
                print '\nMessage %s sent to %s' % (message, address)

        def send_message(self, message, address):
            print address

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(message)
            self.myAgent.send(self.msg)
            print '\nMessage %s sent to %s' % (message, address)

        def stock_generate(self):
            result = []
            number_of_stocks = random.randint(3, 5)
            for i in range(0, number_of_stocks):
                price = random.randint(10, 1000)
                result.append(
                    {
                        'id': i + 1,
                        'name': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)),
                        'price': price,
                        'numberOfStocks': 10000,
                        'totalValue': 10000 * price,
                        'tendency': random.choice(
                            [None, 'up', 'down', 'stale', 'up fast', 'up slow', 'down fast', 'down slow']),
                        'owners': []
                    }
                )

            return result

        # Method that allows trading certain amounts of stocks
        def stock_trade(self):
            print "Method that allows trading certain amounts of stocks -> returns amount of money spent or earned"

        # Method that changes prices of generated stocks according with tendency
        def stock_speculate(self):
            for stock in self.stocks:
                if stock['tendency'] == 'up':
                    # % of change
                    change_percentage = random.randint(1, 5) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'down':
                    # % of change
                    change_percentage = random.randint(1, 5) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'stale':
                    # % of change
                    change_percentage = random.randint(0, 1) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'up slow':
                    # % of change
                    change_percentage = random.randint(5, 10) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'up fast':
                    # % of change
                    change_percentage = random.randint(10, 50) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] += delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'down slow':
                    # % of change
                    change_percentage = random.randint(10, 50) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta
                    self.increase_owner_shares(stock, delta)

                if stock['tendency'] == 'down fast':
                    # % of change
                    change_percentage = random.randint(10, 50) / 100
                    delta = stock['price'] * change_percentage
                    stock['price'] -= delta
                    self.increase_owner_shares(stock, delta)

        def increase_owner_shares(self, stock, delta):
            if len(stock > 0):
                for owner in stock['owners']:
                    owner['price'] = owner['price'] + delta
                    owner['totalPrice'] = owner['totalPrice'] * owner['numberOfShares']

                    self.inform_owner_change(stock, owner['ip'])

    def _setup(self):
        print "\nVAS Stock exchange\t%s\tis up" % self.getAID().getAddresses()

        template = ACLTemplate()
        template.setOntology('stock')

        behaviour = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.OpenStockExchange(), behaviour)


if __name__ == "__main__":
    try:
        StockExchange('stock@127.0.0.1', 'stock').start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
