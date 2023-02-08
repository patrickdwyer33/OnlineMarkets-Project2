import random as rand
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

rand.seed()

def Generate_Adv_Payoff(payoffs, k):
    payoff = rand.uniform(0,1)
    V_list = []
    for i in range(0, k):
        action_payoffs = payoffs.get(i, [0])
        action_payoff = sum(action_payoffs)
        V_list.append([action_payoff, i])
    V_list.sort()
    j_star = V_list[0][1]
    cur = 0
    next = 1
    while (next < len(V_list) and V_list[cur][0] == V_list[next][0]):
        j_star = V_list[cur][1]
        cur = cur + 1
        next = next + 1
    new_payoffs = {}
    for i in range(0, k):
        action_payoffs = payoffs.get(i,[])
        if i == j_star:
            action_payoffs.append(payoff)
        else:
            action_payoffs.append(0)
        new_payoffs[i] = action_payoffs

    return new_payoffs

def Generate_Bern_Payoff(payoffs, probs, k):
    new_payoffs = {}
    for i in range(0, k):
        action_payoffs = payoffs.get(i, [])
        prob = probs[i]
        x = rand.uniform(0,1)
        if x <= prob:
            action_payoffs.append(1)
        else:
            action_payoffs.append(0)
        new_payoffs[i] = action_payoffs
    return new_payoffs

def Generate_D_Payoff(payoffs, round, k):
    new_payoffs = {}
    x = rand.uniform(0, round)
    idx = round % k
    for i in range(0, k):
        action_payoffs = payoffs.get(i, [0])
        last_payoff = action_payoffs[-1]
        new = last_payoff + round
        if i == idx:
            action_payoffs.append(new)
        else:
            action_payoffs.append(last_payoff)
        new_payoffs[i] = action_payoffs
    return new_payoffs

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

def Convert_Date_To_FileDate(date):
    filedate = date.replace(':', '/')
    return filedate

def Update_Choice_Probs(payoffs, probs, round, e, k, h):
    prob_sum = 0
    for i in range(0, k):
        action_payoffs = payoffs[i]
        sum = 0
        for j in range(0,round):
            sum = sum + action_payoffs[j]
        exp = sum / h
        prob = ((1+e)**exp)
        probs[i] = prob
        prob_sum = prob_sum + prob
    for i in range(0, k):
        probs[i] = probs[i] / prob_sum
    return probs

class Exponential_Weights:
    def __init__(self, k, n, h):
        self.k = k
        self.n = n
        self.h = h
        e_list = []
        e = np.sqrt(np.log(k)/n)
        self.theoretical_e = e
        e_max = 2*e
        e_step = e_max / 20
        for i in range(0,20):
            if i != 10:
                e_i = i*e_step
                e_list.append(e_i)
            else:
                e_list.append(e)
        ftl_e = e*3
        e_list.append(e_max)
        e_list.append(ftl_e)
        self.learning_rates = e_list


    def Create_Adv_Payoffs(self):
        payoffs = {}
        for i in range(0,self.n):
            payoffs = Generate_Adv_Payoff(payoffs, self.k)
        return payoffs

    def Create_Bern_Payoffs(self):
        probs = {}
        for i in range(0, self.k):
            probs[i] = rand.uniform(0, 0.5)
        payoffs = {}
        for i in range(0, self.n):
            payoffs = Generate_Bern_Payoff(payoffs, probs, self.k)
        return payoffs

    def Create_D_Payoffs(self):
        payoffs = {}
        for i in range(0,self.n):
            payoffs = Generate_D_Payoff(payoffs, i, self.k)
        return payoffs


    def Run(self, payoffs, e):
        ftl_e = self.learning_rates[-1]
        if e == ftl_e:
            payoff = self.FTL(payoffs)
        else:
            payoff = 0
            initial_prob = 1/self.k
            choice_probs = [initial_prob] * self.k
            k = self.k
            h = self.h
            for i in range(0, self.n):
                choice = Choose_Action(choice_probs)
                assert(choice != -1)
                payoff_list = payoffs.get(choice, [0])
                payoff = payoff + payoff_list[i]
                round = i + 1
                choice_probs = Update_Choice_Probs(payoffs, choice_probs, round, e, k, h)
        return payoff
    @classmethod
    def Calc_OPT(cls, payoffs):
        total_payoffs = []
        for action in payoffs:
            action_payoffs = payoffs[action]
            total = sum(action_payoffs)
            total_payoffs.append(total)
        total_payoffs.sort(reverse=True)
        OPT = total_payoffs[0]
        return OPT
    @classmethod
    def Cur_Winner(cls, payoffs, round):
        total_payoffs = []
        for action in payoffs:
            action_payoffs = payoffs[action]
            sum = 0
            for i in range(0, round):
                sum = action_payoffs[i] + sum
            total_payoffs.append([sum, action])
        total_payoffs.sort(reverse=True)
        cur = total_payoffs[0]
        cur_idx = cur[1]
        return cur_idx

    def FTL(self, payoffs):
        payoff_list = []
        initial_prob = 1/self.k
        choice_probs = [initial_prob] * self.k
        first_choice = Choose_Action(choice_probs)
        choice_payoffs = payoffs.get(first_choice, [0])
        payoff = choice_payoffs[0]
        payoff_list.append(payoff)
        for i in range(1, self.n):
            cur = self.Cur_Winner(payoffs, i)
            choice_payoffs = payoffs.get(cur, [0])
            payoff = choice_payoffs[i]
            payoff_list.append(payoff)
        payoff = sum(payoff_list)
        return payoff




figure, axis = plt.subplots(1,3)
# model == 0 --> adv, model == 1 --> bern, model == 2 --> D
def Monte_Carlo(_EW, trials, model):
    inputs = []
    for i in range(0,trials):
        if model == 0:
            input = _EW.Create_Adv_Payoffs()
        elif model == 1:
            input = _EW.Create_Bern_Payoffs()
        elif model == 2:
            input = _EW.Create_D_Payoffs()
        inputs.append(input)
    e_list = _EW.learning_rates
    avg_regret_list = []
    for i in range(0, len(e_list)):
        e = e_list[i]
        regrets = []
        for j in range(0, trials):
            payoffs = inputs[j]
            ALG = _EW.Run(payoffs, e)
            OPT = Exponential_Weights.Calc_OPT(payoffs)
            regret = OPT - ALG
            regret = regret / EW.n
            regrets.append(regret)
        avg = sum(regrets)
        avg = avg / len(regrets)
        avg_regret_list.append(avg)
    axis[model].plot(e_list, avg_regret_list, '.-')
    if model == 0:
        axis[model].set_title("Adv_Model")
    if model == 1:
        axis[model].set_title("Bern_Model")
    if model == 2:
        axis[model].set_title("Model_D")


EW = Exponential_Weights(10, 100, 1)
EW_D = Exponential_Weights(10, 100, 100)

Monte_Carlo(EW, 100, 0)
Monte_Carlo(EW, 100, 1)
Monte_Carlo(EW_D, 100, 2)

plt.show()
