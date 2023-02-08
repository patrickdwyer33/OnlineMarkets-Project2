import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

rand.seed()

def Choose_Action(probs):
    x = rand.uniform(0,1)
    cur = 0
    next = probs[0]
    for i in range(0,len(probs)):
        if i == (len(probs) - 1):
            return i
        elif x >= cur and x <= next:
            return i
        else:
            cur = cur + probs[i]
            next = next + probs[i+1]
    return -1

#first click prob is actually last
click_probs = []

class EW:
    def __init__(self, k, n, bidder, value):
        self.k = k
        self.n = n
        self.e = np.sqrt(np.log(k)/n)
        self.payoffs = {}
        self.bidder = bidder
        self.value = value
        self.q = 0
        self.pays = []
        self.regret_val_range = [0,1]
        self.val_range = [0,1]
        self.regret_vals = []
        self.possible_vals = []
        for i in range(0, 100):
            val = i * 0.01
            self.regret_vals.append(val)
            self.possible_vals.append(val)
        self.round = 0
        self.prediction_errors = []
        self.error_sum = 0

    def payoff_cacluator(self, bids, a, reserve):
        other_bids = bids.copy()
        other_bids[self.bidder] = a
        with_player = []
        for i in range(0, len(other_bids)):
            pair = (other_bids[i], i)
            with_player.append(pair)
        with_player.sort()
        for i in range(0, len(with_player)):
            pair = with_player[i]
            bid = pair[0]
            player = pair[1]
            if bid == a and player == self.bidder:
                if i >= reserve:
                    return ((self.value * click_probs[i]) - bid)
            return 0

    def initialize(self, k_min, k_max):
        k_step = (k_max-k_min) / (k-1)
        for i in range(0,k):
            action = k_min + (i*k_step)
            actions.append(action)
        self.actions = actions
        probs = []
        for i in range(0,self.k):
            prob = 1/self.k
            probs.append(prob)
        self.probs = probs
        self.update_quality()

    def run_step(self, bids, action):
        prob_sum = 0
        probs = []
        round_payoffs = []
        actual_payoff = 0
        for i in range(0, self.k):
            a = self.actions[i]
            a_payoff = self.payoff_calculator(bids, a)
            if i == action:
                actual_payoff_bid = (a_payoff, action)
                self.pays.append(action_payoff_bid)
            round_payoffs.append(a_payoff)
            a_totalpayoff = self.payoffs.get(a, 0) + a_payoff
            self.payoffs[a] = a_totalpayoff
            exp = a_totalpayoff / self.h
            prob = (1+self.e)**exp
            probs.append(prob)
            prob_sum = prob + prob_sum
        for i in range(0,self.k):
            p = probs[i]
            prob = p / prob_sum
            probs[i] = prob
        self.probs = probs
        self.round = self.round + 1

        return actual_payoff

    def calculate_rationalizable(self):
        rationalizable_set
        rationalizable_vs = []
        rationalizable_es = []
        rationalizable_lists = []
        for a in self.actions:
            rationalizable = []
            action_pay = self.payoffs[a]
            avg_action_pay = (action_pay) / (self.round+1)
            for v in self.possible_vals:
                for e in self.regret_vals:
                    left = avg_action_pay - e
                    theoretical_sum = 0
                    for pay in self.pays:
                        theoretical_pay = 0
                        if pay > 0:
                            pay_temp = (pay - self.value) * -1
                            theoretical_pay = v - pay_temp
                        theoretical_sum = theoretical_sum + theoretical_pay
                    if theoretical_sum >= left:
                        point = (v,e)
                        rationalizable.append(point)
            rationalizable_lists.append(rationalizable)
        for v in self.possible_vals:
            for e in self.regret_vals:
                point = (v,e)
                in_all = True
                for list in rationalizable_lists:
                    if point not in list:
                        in_all = False
                if in_all:
                    rationalizable_set.append(point)
                    rationalizable_vs.append(v)
                    rationalizable_es.append(e)
        self.rationalizable_set = rationalizable_set
        return rationalizable_vs, rationalizable_es

    def value_prediction(self):
        rats = self.rationalizable_set.copy()
        rats.sort(key = lambda x: x[1])
        prediction_point = rats[0]
        prediction = prediction_point[0]
        return prediction

    def update_error(self):
        v_star = self.value_prediction()
        diff = (v-v_star)**2
        new_error_sum = diff + self.error_sum
        expected = new_error_sum/(self.round+1)
        self.prediction_errors.append(expected)
        self.error_sum = new_error_sum

    def update_quality(self):
        q = rand.uniform(0,1)
        self.q = q


class EW_Auction:
    def __init__(self):
        pass



class trial:
    def __init__(self, m, values):
        self.m = m
        self.values = values
