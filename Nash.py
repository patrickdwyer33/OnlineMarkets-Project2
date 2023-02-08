import statistics

b_1 = [0,0.25,0.5,0.75,1]
b_2 = {}
for b in b_1:
    if b == 0.5:
        b_2[0.5] = b_1
    if b < 0.5:
        y = 0.5 + b
        m = y / 2
        bids = []
        for i in range(0,5):
            bid = i * (m/2)
            bids.append(bid)
        b_2[b] = bids
    if b > 0.5:
        x = b - 0.5
        m = (1-x) / 2
        bids = []
        for i in range(0,5):
            bid = (i * (m/2)) + x
            bids.append(bid)
        b_2[b] = bids
b_3 = {}
for b in b_2:
    b_2_bids = b_2[b]
    b_2_m = (b_2_bids[4] - b_2_bids[0])/2
    for b_2_bid in b_2_bids:
        if b_2_bid == b_2_m:
            b_3[(b, b_2_bid)] = b_2_bids
        if b_2_bid < b_2_m:
            y = b_2_bid + b_2_m
            x = b_2_bids[0]
            m = (y-x)/2
            bids = []
            for i in range(0, 5):
                bid = (i * (m/2)) + x
                bids.append(bid)
            b_3[(b, b_2_bid)] = bids
        if b_2_bid > b_2_m:
            x = b_2_bid - b_2_m
            y = b_2_bids[4]
            m = (y-x)/2
            bids = []
            for i in range(0, 5):
                bid = (i * (m/2)) + x
                bids.append(bid)
            b_3[(b, b_2_bid)] = bids
actions_meds = {}
medians = []
for key in b_3:
    bid_1 = key[0]
    bid_2 = key[1]
    bid_3_list = b_3[key]
    for bid_3 in bid_3_list:
        bids = [bid_1,bid_2,bid_3]
        med = statistics.median(bids)
        a_1 = bid_1 / 0.25
        bid_2_list = b_2[bid_1]
        m_2 = (bid_2_list[4] - bid_2_list[0])/2
        a_2 = (bid_2 - bid_2_list[0]) / (m_2/2)
        m_3 = (bid_3_list[4] - bid_3_list[0])/2
        a_3 = (bid_3 - bid_3_list[0]) / (m_3/2)
        actions = (a_1, a_2, a_3)
        actions_meds[actions] = med
        medians.append(med)
        print("Bids then Actions then Median")
        print(bids)
        print(actions)
        print(med)
umeds = list(set(medians))
umeds.sort()
for i in range(0, (len(umeds)-1)):
    low = umeds[i]
    high = umeds[i+1]
    mid = (high-low)/2
    umeds.append(mid)
value_list = list(set(umeds))
value_list.sort()
print(value_list)
pure_nashes = {}
for i in range(0,len(value_list)):
    v_1 = value_list[i]
    for j in range(0,len(value_list)):
        v_2 = value_list[j]
        for k in range(0,len(value_list)):
            v_3 = value_list[k]
            for action in actions_meds:
                median = actions_meds[action]
                a_1 = actions[0]
                a_2 = actions[1]
                a_3 = actions[2]
                p_1 = 1 - abs(v_1-median)
                p_2 = 1 - abs(v_2-median)
                p_3 = 1 - abs(v_3-median)
                nash = True
                for i in range(0, 5):
                    a_1_star = (i, a_2, a_3)
                    a_2_star = (a_1, i, a_3)
                    a_3_star = (a_1, a_2, i)
                    med_1 = actions_meds[a_1_star]
                    med_2 = actions_meds[a_2_star]
                    med_3 = actions_meds[a_3_star]
                    p_1_star = 1 - abs(v_1 - med_1)
                    p_2_star = 1 - abs(v_2 - med_2)
                    p_3_star = 1 - abs(v_3 - med_3)
                    if p_1_star > p_1 or p_2_star > p_2 or p_3_star > p_3:
                        nash = False
                bid_1 = a_1 / 4
                if bid_1 < 0.5:
                    y = 0.5 + bid_1
                    if v_2 > y:
                        nash = False
                if bid_1 > 0.5:
                    x = bid_1 - 0.5
                    if v_2 < x:
                        nash = False
                bid_2_list = b_2[bid_1]
                y = bid_2_list[4]
                x = bid_2_list[0]
                m_2 = (y-x)/2
                bid_2 = (a_2 * (m_2/2)) + x
                if bid_2 < m_2:
                    y = m_2 + bid_2
                    if v_3 < x or v_3 > y:
                        nash = False
                if bid_2 > m_2:
                    x = bid_2 - m_2
                    if v_3 < x or v_3 > y:
                        nash = False
                if bid_2 == m_2:
                    if v_3 < x or v_3 > y:
                        nash = False
                values = (v_1, v_2, v_3)
                if nash == True:
                    things = pure_nashes.get(values, [])
                    things.append(action)
                    pure_nashes[values] = things

for key, value in pure_nashes.items():
    print(key, ' : ', value)
