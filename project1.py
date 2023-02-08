import pandas as pd
import matplotlib.pyplot as plt

# Fetch the csv with pandas and remove ourselves
def fetch_csv():
    total_bids = pd.read_csv("/Users/patrickdwyer/Desktop/bid_data.csv")
    mr_pd_netids = ["***8079", "***4122"]

    mr_pd_bids = total_bids[total_bids.ID.isin(mr_pd_netids)].reset_index(drop=True)
    bid_data = total_bids[total_bids.ID.isin(mr_pd_netids) == False].reset_index(drop=True)
    bid_data = bid_data[bid_data['bid in Auction A'] > 0]
    bid_data = bid_data[bid_data[' bid in Auction B'] > 0]
    bid_data = bid_data[bid_data['bid in Auction A'] <= bid_data['v_A']]
    bid_data = bid_data[bid_data[' bid in Auction B'] <= bid_data['v_B']]
    bid_data = bid_data.reset_index(drop=True)
    return mr_pd_bids, bid_data

mr_pd_bids, bid_data = fetch_csv()
print(mr_pd_bids)
print(bid_data)

player_count = 0
# Experimentally, pd was first, but I presume this is because the filter above finds it first
pd_bA = mr_pd_bids.iloc[0].loc['bid in Auction A']
pd_bB = mr_pd_bids.iloc[0].loc[' bid in Auction B']
mr_bA = mr_pd_bids.iloc[1].loc['bid in Auction A']
mr_bB = mr_pd_bids.iloc[1].loc[' bid in Auction B']
print("mr_pd bids:")
print(pd_bA)
print(pd_bB)
print(mr_bA)
print(mr_bB)
pd_vA = 33
pd_vB = 59.3
mr_vA = 43.7
mr_vB = 71.5


pd_A_win_prob = 0
pd_B_win_prob = 0
mr_A_win_prob = 0
mr_B_win_prob = 0

pdU_A = pd_vA - pd_bA
pdU_B = pd_vB - pd_bB
mrU_A = mr_vA - mr_bA
mrU_B = mr_vB - mr_bB

A_bids = []
B_bids = []
Bids_Values = []
for idx, player in bid_data.iterrows():
    player_count = player_count + 1
    playerbid_A = player.loc['bid in Auction A']
    A_bids.append(playerbid_A)
    playerbid_B = player.loc[' bid in Auction B']
    B_bids.append(playerbid_B)
    playervalue_A = player.loc['v_A']
    playervalue_B = player.loc['v_B']
    Bids_Values.append([playervalue_A, playerbid_A])
    Bids_Values.append([playervalue_B, playerbid_B])
    if pd_bA == playerbid_A:
        pd_A_win_prob = pd_A_win_prob + 0.5
    elif pd_bA > playerbid_A:
        pd_A_win_prob = pd_A_win_prob + 1
    if pd_bB == playerbid_B:
        pd_B_win_prob = pd_B_win_prob + 0.5
    elif pd_bB > playerbid_B:
        pd_B_win_prob = pd_B_win_prob + 1

    if mr_bA == playerbid_A:
        mr_A_win_prob = mr_A_win_prob + 0.5
    elif mr_bA > playerbid_A:
        mr_A_win_prob = mr_A_win_prob + 1
    if mr_bB == playerbid_B:
        mr_B_win_prob = mr_B_win_prob + 0.5
    elif mr_bB > playerbid_B:
        mr_B_win_prob = mr_B_win_prob + 1

pd_A_win_prob = pd_A_win_prob / player_count
pd_B_win_prob = pd_B_win_prob / player_count

mr_A_win_prob = mr_A_win_prob / player_count
mr_B_win_prob = mr_B_win_prob / player_count

pdex_A = pdU_A * pd_A_win_prob
pdex_B = pdU_B * pd_B_win_prob

mrex_A = mrU_A * mr_A_win_prob
mrex_B = mrU_B * mr_B_win_prob

print("mr_pd win probs:")
print(pd_A_win_prob)
print(pd_B_win_prob)
print(mr_A_win_prob)
print(mr_B_win_prob)

print("expected utility:")
print(pdex_A)
print(pdex_B)
print(mrex_A)
print(mrex_B)

A_bids.sort()
B_bids.sort()

pd_A_utilities = []
pd_B_utilities = []

mr_A_utilities = []
mr_B_utilities = []

prob_first = 1 / player_count
prev_A_bid = A_bids[0]

pd_first_A = (pd_vA-(prev_A_bid+0.0001))*prob_first
pd_A_utilities.append([prev_A_bid, pd_first_A])

mr_first_A = (mr_vA-(prev_A_bid+0.0001))*prob_first
mr_A_utilities.append([prev_A_bid, mr_first_A])

A_equal_count = 0
for i in range(1,len(A_bids)):
    bid = A_bids[i] + 0.0001
    prob = (i+1)/player_count
    pd_utility = (pd_vA-bid)*prob
    mr_utility = (mr_vA-bid)*prob
    if A_bids[i] == prev_A_bid:
        A_equal_count = A_equal_count + 1
        last_idx = i - A_equal_count
        pd_A_utilities[last_idx] = [bid, pd_utility]
        mr_A_utilities[last_idx] = [bid, mr_utility]
    else:
        pd_A_utilities.append([bid, pd_utility])
        mr_A_utilities.append([bid, mr_utility])
    prev_A_bid = A_bids[i]

prev_B_bid = B_bids[0]

pd_first_B = (pd_vB-(prev_B_bid+0.0001))*prob_first
pd_B_utilities.append([prev_B_bid, pd_first_B])

mr_first_B = (mr_vB-(prev_B_bid+0.0001))*prob_first
mr_B_utilities.append([prev_B_bid, mr_first_B])

B_equal_count = 0
for i in range(1,len(B_bids)):
    bid = B_bids[i] + 0.0001
    prob = (i+1)/player_count
    pd_utility = (pd_vB-bid)*prob
    mr_utility = (mr_vB-bid)*prob
    if B_bids[i] == prev_B_bid:
        B_equal_count = B_equal_count + 1
        last_idx = i - B_equal_count
        pd_B_utilities[last_idx] = [bid, pd_utility]
        mr_B_utilities[last_idx] = [bid, mr_utility]
    else:
        pd_B_utilities.append([bid, pd_utility])
        mr_B_utilities.append([bid, mr_utility])
    prev_B_bid = B_bids[i]


pd_A_utilities.sort(key = lambda x: x[1])
pd_B_utilities.sort(key = lambda x: x[1])

mr_A_utilities.sort(key = lambda x: x[1])
mr_B_utilities.sort(key = lambda x: x[1])

pd_A_U_optidx = len(pd_A_utilities) - 1
pd_B_U_optidx = len(pd_B_utilities) - 1

mr_A_U_optidx = len(mr_A_utilities) - 1
mr_B_U_optidx = len(mr_B_utilities) - 1

pd_opt_A = pd_A_utilities[pd_A_U_optidx]
pd_opt_B = pd_B_utilities[pd_B_U_optidx]

pd_optbid_A = pd_opt_A[0]
pd_optutility_A = pd_opt_A[1]
pd_optbid_B = pd_opt_B[0]
pd_optutility_B = pd_opt_B[1]

mr_opt_A = mr_A_utilities[mr_A_U_optidx]
mr_opt_B = mr_B_utilities[mr_B_U_optidx]

mr_optbid_A = mr_opt_A[0]
mr_optutility_A = mr_opt_A[1]
mr_optbid_B = mr_opt_B[0]
mr_optutility_B = mr_opt_B[1]

print("pd bid, utility")
print(pd_optbid_A)
print(pd_optutility_A)
print(pd_optbid_B)
print(pd_optutility_B)
print("mr bid, utility")
print(mr_optbid_A)
print(mr_optutility_A)
print(mr_optbid_B)
print(mr_optutility_B)

diff_from_mean = 0
data_included = 0
ratio_list = []
ratio_count = {}
for i in range(0,len(Bids_Values)):
    bid_val = Bids_Values[i]
    val = bid_val[0]
    bid = bid_val[1]

    ratio = bid / val
    ratio_count[ratio] = ratio_count.get(ratio, 0) + 1
    diff_from_mean = diff_from_mean + ratio
    if ratio >= 0.5:
        data_included = data_included + 1
average_diff = diff_from_mean / (player_count * 2)
data_included = data_included + 1
ratio_count_list = []
for ratio in ratio_count:
    count = ratio_count[ratio]
    ratio_list.append(ratio)
    ratio_count_list.append(count)
print(average_diff)
print(data_included)
s = pd.Series(ratio_list, ratio_count_list)
data = {'ratio': ratio_list,
        'count': ratio_count_list}
df = pd.DataFrame(data,columns=['ratio','count'])
df.plot(x ='ratio', y='count', kind = 'scatter')
plt.show()
