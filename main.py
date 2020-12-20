import pandas as pd
from tqdm import tqdm

def dot_product(selection, weights):
	return sum([a_i * b_i for a_i, b_i in zip(selection, weights)])

def knapsack(cap, n, value, weight, number):
	max_weight = max(weight)
	# remaining_stock is used to remember remaining number of each item for every capacity - max_weight steps into the past (won't access items before that)
	# memory usage without queue: ~2Mio. entries * 10 items per entry * 4B = ~80MB
	# memory usage with queue: max_weight entries * 10 items per entry * 4B = 145KB
	remaining_stock = [list(number) for i in range(max_weight)]
	# max_val contains the dynamic programming results. The size of this data structure could be reduced similarly to remaining_stock, however for the given dataset it is small enough (~2Mio. entries * 4B = ~8MB memory consumption)
	max_val = [0 for i in range(cap + 1)]
	for i in tqdm(range(cap + 1)): # iterate over all capacities until cap
		remaining_stock.append(list(number)) # add a new item to the remaining_stock queue
		best_item_idx = -1
		for j in range(n): # iterate over each item index and remember best item to take in
			if weight[j] <= i and remaining_stock[max_weight-weight[j]][j] > 0:
				if(max_val[i] < max_val[i - weight[j]] + value[j]):
					max_val[i] = max_val[i - weight[j]] + value[j]
					best_item_idx = j
		if best_item_idx > -1: # reduce remaining_stock of the corresponding item
			remaining_stock[-1] = list(remaining_stock[max_weight-weight[best_item_idx]])
			remaining_stock[-1][best_item_idx] -= 1
		del remaining_stock[0]
	selected_items = [a_i - b_i for a_i, b_i in zip(number, remaining_stock[-1])]
	return selected_items, max_val[cap] # return counts of selected items and total value

# read the table from the txt
data = pd.read_csv("bwiTable.txt")

p1_weight = 72400 # weight of frist driver in g
p2_weight = 85700 # weight of second driver in g
cap1 = 1100000 - 72400 # capacity of first transporter
cap2 = 1100000 - 85700 # capacity of second transporter
values = data["Nutzwert"] # list of values of items
weights = data["Gewicht"] # list of weights of items
numbers = data["Einheiten"] # list of maximum number of items needed
n = len(values) # number of different items

# suppose we have one large transporter instead of two small ones, calculate which items could be transported
print("Starting ideal value calculation ...")
total_items, total_value = knapsack(cap1 + cap2, n, values, weights, numbers.tolist())

# now we try to split up the ideal contents of one large transporter among the two small transporters, thus we try to pack up transporter 1 as full as possible (weight-wise)
print("Starting distribution test ...")
transporter1_items, _ = knapsack(cap1, n, weights, weights, total_items)

# calculate value, weight and unused capacity of each transporter, assuming transporter 1 is packed up as full as possible and transporter 2 takes all the remaining items
total_unused_cap = (cap1 + cap2) - dot_product(total_items, weights)
total_weight = dot_product(total_items, weights) + p1_weight + p2_weight
tranporter1_value = dot_product(transporter1_items, values)
transporter1_weight = dot_product(transporter1_items, weights) + p1_weight
transporter1_unused_cap = cap1 + p1_weight - transporter1_weight
transporter2_items = [a_i - b_i for a_i, b_i in zip(total_items, transporter1_items)]
transporter2_weight = dot_product(transporter2_items, weights) + p2_weight
transporter2_unused_cap = cap2 + p2_weight - transporter2_weight

# if the unused capacity of transporter 1 is smaller than the total unused capacity of the imaginary large transporter, then this means transporter 2 can take the remaining items without being overloaded
if total_unused_cap - transporter1_unused_cap > 0:
	print()
	print("The following solution was discovered")
	print("Total items transported: " + str(total_items))
	print("Total value: " + str(total_value))
	print("Total weight: " + str(total_weight) + " of " + str(cap1+cap2+p1_weight+p2_weight) + " grams")
	print()
	print("Items in Transporter 1: " + str(transporter1_items))
	print("Transporter 1 value: " + str(tranporter1_value))
	print("Transporter 1 weight utilization: " + str(transporter1_weight) + " of " + str(cap1 + p1_weight) + " grams, " + str(transporter1_unused_cap) + " unused grams")
	print()
	print("Items in Transporter 2: " + str(transporter2_items))
	print("Transporter 2 value: " + str(total_value - tranporter1_value))
	print("Transporter 2 weight utilization: " + str(transporter2_weight) + " of " + str(cap2 + p2_weight) + " grams, " + str(transporter2_unused_cap) + " unused grams")

# NOTE: If the last if statement is satisfied, this means the algorithm found an optimal solution, which is the case for the given data. However, there are scenarios where this approach doesn't find a solution. Usually, a two dimensional knapsack algorithm would be used to solve this then. However, because the greatest common divisor of all item weights is 1, and the two capacities of the transporters are large (~1Mio.), the runtime of such an algorithm would be infeasible for the current setup.
