import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def create_coinbase_payoffs():
    data = pd.read_csv('coinbase.csv')
    data['change'] = (data['close'] - data['open']) / data['open']
    bitcoin = pd.read_csv('bitcoin.csv')
    data['btc/eth'] = bitcoin['open']/data['open']

    payoffs = {}
    btc_eth_ratios = {}
    data_length = len(data['change'])
    idx_list = []
    for idx, row in data.iterrows():
        info = row['btc/eth']
        delta = row['change']
        invest_payoff = 1 + delta
        short_payoff = 1 - delta
        pidx = data_length - idx - 1
        idx_list.append(idx)
        payoffs[pidx] = [invest_payoff, 1, short_payoff]
        btc_eth_ratios[pidx] = info

    return payoffs, idx_list, btc_eth_ratios

class EW_ALGS:
    instances = []
    payoffs = {}
    action_count = 0
    round = 0
    payoff = 0
    OPT_actions = []
    ALG_actions = []
    info = {}
    info_splits = 0

    def __init__(self, i, k):
        self.birth_round = i
        self.observed_payoffs_dict = {}
        self.observed_info = []
        self.observed_info_dict = {}
        for i in range(0, EW_ALGS.info_splits):
            self.observed_payoffs_dict[i] = []
            self.observed_info_dict[i] = []
        self.splits = []
        self.time_ran = 0
        self.probs = {}

    @classmethod
    def initialize(cls, payoffs, k, info, d):
        cls.action_count = k
        cls.round = 0
        cls.payoff = 0
        cls.payoffs = payoffs
        cls.info = info
        cls.info_splits = d
        cls.instances.clear()
        cls.OPT_actions.clear()
        cls.ALG_actions.clear()

    @classmethod
    def create_ALG(cls):
        ALG = cls(cls.round, cls.action_count)
        ALG.probs = cls.init_probs()
        cls.instances.append(ALG)

    @classmethod
    def place_val(cls, val, splits):
        cur = 0
        next = splits[0]
        split_count = len(splits)
        for i in range(0, split_count):
            if i == (split_count - 1):
                return i
            elif val >= cur and val < next:
                return i
            else:
                cur = splits[i]
                next = splits[(i+1)]
        return -1


    def update_splits(self, num_splits):
        assert(self.observed_info)
        self.splits.clear()
        n = len(self.observed_info)
        if n == 1:
            val = self.observed_info[0]
            for i in range(0, num_splits):
                split = (i+1)*(val/num_splits)
                self.splits.append(split)
        else:
            max_val = max(self.observed_info)
            min_val = min(self.observed_info)
            data_range = max_val - min_val
            for i in range(0, num_splits):
                split = (i+1)*(data_range/num_splits)
                self.splits.append(split)

    @classmethod
    def init_probs(cls):
        initial_prob = 1/cls.action_count
        choice_probs = [initial_prob] * cls.action_count
        return choice_probs

    def choose_action(self, k, cat):
        probs = self.probs[cat]
        x = rand.uniform(0,1)
        cur = 0
        next = probs[0]
        for i in range(0, k):
            if i == (k - 1):
                return i
            elif x >= cur and x <= next:
                return i
            else:
                cur = cur + probs[i]
                next = next + probs[i+1]
        return -1

    @classmethod
    def pick_choice(cls, probs):
        x = rand.uniform(0,1)
        cur = 0
        next = probs[0]
        for i in range(0, k):
            if i == (k - 1):
                return i
            elif x >= cur and x <= next:
                return i
            else:
                cur = cur + probs[i]
                next = next + probs[i+1]
        return -1

    @classmethod
    def run(cls, payoffs, k, info, d):
        cls.initialize(payoffs, k, info, d)
        n = len(cls.payoffs)
        for i in range(0, n):
            cls.run_step()

    @classmethod
    def run_step(cls):
        cls.create_ALG()
        choices = {}
        true_round = cls.round + 1
        max_exp = np.log(true_round)+1
        exp_step = max_exp / true_round
        for alg in cls.instances:
            alg_info = alg.observed_info
            round_info = cls.info[cls.round]
            alg_info.append(round_info)
            alg.update_splits(cls.info_splits)
            cat = cls.place_val(round_info, alg.splits)
            alg.update_alg()
            choice = alg.choose_action(cls.action_count, cat)
            birth = alg.birth_round
            adj_birth = birth + 1
            exp = birth * exp_step
            choices[choice] = choices.get(choice, 0) + (adj_birth**exp)

        vote_sum = 0
        for i in range(0, cls.action_count):
            vote_sum = vote_sum + choices.get(i, 0)
        prob_choices = []
        for i in range(0, cls.action_count):
            prob = choices.get(i, 0) / vote_sum
            prob_choices.append(prob)

        agg_choice = cls.pick_choice(prob_choices)
        round_payoffs = cls.payoffs[cls.round]
        cls.payoff = cls.payoff + round_payoffs[agg_choice]
        cls.round = cls.round + 1
        cls.ALG_actions.append([agg_choice, cls.payoff])
        OPT_idx_payoff = cls.calc_OPT()
        OPT_choice = OPT_idx_payoff[0]
        OPT_payoff = OPT_idx_payoff[1]
        cls.OPT_actions.append([OPT_choice, OPT_payoff])

    def update_alg(self):
        alg_info = self.observed_info
        info_count = len(alg_info)
        observed_info_dict = self.observed_info_dict
        observed_payoffs = self.observed_payoffs_dict
        observed_info.clear()
        observed_payoffs.clear()
        for i in range(0, info_count):
            data = alg_info[i]
            cat = EW_ALGS.place_val(data, self.splits)
            observed_info_dict[cat] = observed_info_dict.get(cat, []).append(data)
            true_idx = self.birth_round + i
            payoffs = EW_ALGS.getPayoffs()
            payoff = payoffs[true_idx]
            for j in range(0, EW_ALGS.action_count):
                observed_payoffs[(j, cat)] = observed_payoffs.get(cat, []).append(payoff)
        probs = self.probs
        time_ran = self.time_ran
        time_ran = time_ran + 1
        e = EW_ALGS.theoretical_e(time_ran)
        for i in range(0, EW_ALGS.info_splits):
            probs[cat] = self.update_probs(e, EW_ALGS.action_count, i)


    @classmethod
    def getPayoffs(cls):
        return cls.payoffs

    @classmethod
    def update_ALGS(cls):
        round_payoffs = cls.payoffs[cls.round]
        for alg in cls.instances:
            observed_payoffs = alg.observed_payoffs
            for i in range(0, cls.action_count):
                observed_payoffs[i] = observed_payoffs.get(i, 0) + round_payoffs[i]
            birth = alg.birth_round
            time_ran = alg.time_ran
            time_ran = time_ran + 1
            #cls.update_e()
            e = cls.theoretical_e(time_ran)
            alg.probs = alg.update_probs(e, cls.action_count)

    @classmethod
    def calc_OPT(cls):
        first_ALG = cls.instances[0]
        observed_payoffs = first_ALG.observed_payoffs
        idx_payoff = []
        for i in range(0, cls.action_count):
            idx_payoff.append([i, observed_payoffs.get(i, 0)])
        return max(idx_payoff,key=lambda x:x[1])

    #@classmethod
    #def update_e(cls):
    #    cls.e = np.sqrt(np.log(cls.action_count)/(cls.round+1))
    @classmethod
    def theoretical_e(cls, time_ran):
        return np.sqrt(np.log(cls.action_count)/time_ran)

    def update_probs(self, e, k, cat):
        probs = []
        for i in range(0, k):
            payoff = self.observed_payoffs_dict.get((i, cat), 0)
            exp = payoff / 2
            top = (1+e)**exp
            probs.append(top)
        total = sum(probs)
        for p in probs:
            p = p / total
        return probs

coinbase_payoffs, idx_list, ratios = create_coinbase_payoffs()
data_length = len(idx_list)
k = 3
trials = 100
regrets = {}
payoffs = {}
for i in range(0, trials):
    EW_ALGS.run(coinbase_payoffs, k, ratios, 3)
    for j in range(0, data_length):
        ALG = EW_ALGS.ALG_actions[j]
        ALG_choice = ALG[0]
        ALG_cum = ALG[1]
        OPT = EW_ALGS.OPT_actions[j]
        OPT_choice = OPT[0]
        OPT_cum = OPT[1]

        regret = (OPT_cum-ALG_cum)/(j+1)
        payoff = ALG_cum
        if j > 0:
            prev_ALG = EW_ALGS.ALG_actions[j-1]
            payoff = payoff - prev_ALG[1]

        regrets[j] = regrets.get(j, 0) + regret
        payoffs[j] = payoffs.get(j, 0) + (payoff - 1)

regret_list = []
payoff_list = []

for i in range(0, data_length):
    regret = regrets.get(i, 0) / trials
    payoff = payoffs.get(i, 0) / trials
    print(regret)
    regret_list.append(regret)
    payoff_list.append(payoff)


def EX_Payoff_From(payoffs, i):
    payoff_list = payoffs[i:]
    sum_payoffs = sum(payoff_list)
    n = data_length - i
    return (sum_payoffs / n)

EX_payoff_list = []
for i in range(0, data_length):
    ex = EX_Payoff_From(payoff_list, i)
    EX_payoff_list.append(ex)

figure, axis = plt.subplots(1,3)
axis[0].plot(idx_list, regret_list, '.-')
axis[1].plot(idx_list, payoff_list, '.-')
axis[2].plot(idx_list, EX_payoff_list, '.-')
axis[0].set_title('Avg Regret at Round')
axis[1].set_title('Avg Payoff at Round')
axis[2].set_title('EX Payoff from Round to End')

plt.show()
