import random

xtra = 1.23
amount = 1000

result_multiplier = random.randint(0,100) / 100
print(result_multiplier)
print(amount*result_multiplier)
result_multiplier = result_multiplier * xtra
amount_won = round(amount * result_multiplier, 1) # % of original money won. KEEP in mind that no money deducted from user wallet.


print(result_multiplier)
print(amount*result_multiplier)
print(amount_won)