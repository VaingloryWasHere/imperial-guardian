import discord
from discord.ext import commands
from tinydb import TinyDB, Query, where
import random
'''
FRUIT COLLECTION CONSISTS OF:
EcoInventory ( Core functionality for viewing inventory and trading)
EcoFruits (Adds functionality for collecting fruits through /grow and /search. Dependent on EcoInventory.)
'''

'''
THIS CLASS ALLOWS THE ALLOWING OPERATIONS:
adding money(negative or positive; low-level function)
depositing
withdrawing
generating balance embed(called 'statement')
getting account
opening account
closing account
refreshing db(background task thru asyncio.tasks)
closing db(for whatever reason)
'''

class BankCore:
    def __init__(self):
        self.bank = TinyDB('data/bank.json')

    def get_account(self, user_id):
        acc = self.bank.get(where('User ID') == int(user_id))
        if acc == None:
            acc = self.open_account(user_id)
            return acc
        return acc

    def open_account(self, user_id, opening_balance = 500, multiplier = 1):
        self.bank.insert({
        'User ID': int(user_id),
        'Wallet': opening_balance,
        'Bank': 0,
        'Fruit Shards':0,
        'Inventory': {},
        'Fruits':{},
        'Daily Streak': 0, #Number of days user has consecutively used ?daily
        'Multiplier': multiplier
        })
        return self.get_account(user_id)

    def generate_statement(self, user_id):
        acc = self.get_account(user_id)
        if acc == None:
            acc = self.open_account(user_id)
            statement = discord.Embed(title="Balance", description='',color=discord.Color.blue())
            statement.add_field(name='',value=f"**Wallet:** ${acc['Wallet']}",inline=False)
            statement.add_field(name='',value=f"**Bank:** ${acc['Bank']}",inline=False)
            statement.add_field(name='',value=f"**Inventory:** {len(acc['Inventory'])} items.",inline=False)
            return statement
        statement = discord.Embed(title="Balance", description='',color=discord.Color.blue())
        statement.add_field(name='',value=f"**Wallet:** ${acc['Wallet']}",inline=False)
        statement.add_field(name='',value=f"**Bank:** ${acc['Bank']}",inline=False)
        statement.add_field(name='',value=f"**Inventory:** {len(acc['Inventory'])} items.",inline=False)
        return statement

    def close_account(self, user_id):
        self.bank.remove(where("User ID")==user_id)

    def add_money(self,user_id,amount,medium='w'): #can do subtraction using negative amount
        '''
    THIS IS A LOW LEVEL FUNCTION. FOR GENERAL USAGE SEE deposit() and withdraw()
        '''
        acc = self.get_account(user_id)
        match medium:
            case 'w':
                acc['Wallet'] += amount
                self.bank.update(acc, where('User ID') == user_id)
            case 'b':
                acc['Bank'] += amount
                self.bank.update(acc, where('User ID') == user_id)
            case 's':
                acc['Fruit Shards'] += amount
                self.bank.update(acc, where('User ID') == user_id)
            case _:
                return ValueError(f"Uknown medium for function add_money(): {medium}")

    def deposit(self, user_id, amount):
        amount = int(amount)
        acc = self.get_account(user_id)
        #subtract from wallet
        self.add_money(user_id, -amount, 'w')
        #add to bank
        self.add_money(user_id, amount, 'b')

    def withdraw(self, user_id, amount):
        acc = self.get_account(user_id)
        #subtract from bank
        self.add_money(user_id, -amount, 'b')
        #add to wallet
        self.add_money(user_id, amount, 'w')

    def close_db(self):
        self.bank.close()

    #Probability function. 50/50 by default. Could be used for jackpot game.
    def toss(self, true_chance = 50):
        toss = random.randint(0,100)
        if toss <= true_chance:
            return True
        elif toss > true_chance:
            return False

    def add_item(self,user_id,item_name,quantity=1):
        user_data = self.get_account(user_id)
        user_data['Inventory'][item_name] = quantity
        self.bank.update(user_data, where('User ID')==user_id)

    def remove_item(self,user_id,item_name,quantity=1):
        user_data = self.get_account(user_id)
        user_data['Inventory'][item_name] = user_data['Inventory'][item_name] - quantity
        if user_data['Inventory'][item_name] <= 0:
            del user_data['Inventory'][item_name]
        self.bank.update(user_data, where('User ID')==user_id)
'''
The following cog contains the following commands:
?balance(+), ?daily, ?gamble(+), ?deposit(+), ?withdraw(+)
+ means added
'''
class EcoCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bank = BankCore()

    @commands.command(brief='',help='')
    async def balance(self, ctx,member:discord.Member = None):
        if member == None:
            member = ctx.message.author
        statement = self.bank.generate_statement(member.id)
        await ctx.reply(embed=statement)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        daily_streak = self.bank.get_account(ctx.message.author.id)['Daily Streak']
        earnings = 100 + (daily_streak * 10)
        self.bank.add_money(ctx.message.author.id,earnings)
        notice = discord.Embed(title="Daily for {ctx.message.author.name}",description=f"Earnings: ${earnings}\n\nDaily Streak Bonus: ${daily_streak*10}\n\nYour Streak: {daily_streak}",color=discord.Color.blue())
        await ctx.reply(embed=notice)

    @commands.command(brief='',help='')
    async def deposit(self, ctx, amount):
        amount = int(amount)
        acc = self.bank.get_account(ctx.message.author.id)
        wallet_bal = acc['Wallet']
        if acc == None:
            await ctx.send('You do not have an an account yet! Run `?balance` to create one.')
        elif amount <= 0:
            await ctx.reply("Nice try. That amount of money must be equal to your IQ.")
        elif amount > wallet_bal:
            await ctx.reply("You don't have that much money dumbass.")

        else:
            self.bank.deposit(ctx.message.author.id, amount)
            statement=self.bank.generate_statement(ctx.message.author.id)
            statement.set_footer(text=f"**{amount}**",icon_url="https://emoji.discadia.com/emojis/74d36bc8-31d6-4511-bdc0-566b7ae6bb74.PNG")
            await ctx.reply(embed=statement)

        

    @commands.command(brief='',help='')
    async def withdraw(self, ctx,amount):
        amount = int(amount)
        bank_bal = self.bank.get_account(ctx.message.author.id)['Bank']
        if bank_bal == None:
            await ctx.send('You do not have an an account yet! Run `?balance` to create one.')
        elif amount <= 0:
            await ctx.reply("Nice try. That amount of money must be equal to your IQ.")
        elif amount > bank_bal:
            await ctx.reply("You don't have that much money dumbass.")

        else:
            self.bank.withdraw(ctx.message.author.id, amount)
            statement=self.bank.generate_statement(ctx.message.author.id)
            statement.set_footer(text=f"**{amount}**",icon_url="https://emoji.discadia.com/emojis/2a87190b-a9c4-4f6c-89d4-891754d826ce.png")
            await ctx.reply(embed=statement)

    @commands.command(brief='Throw a risky gamble.',help="**Syntax: `?gamble <amount>`\nThere is a 50% chance to lose all the money.\nProfit ranges from 10% to 100% multiplied by your base multiplier.")
    async def gamble(self, ctx, amount):
        amount = int(amount)
        balance = self.bank.get_account(ctx.message.author.id)['Wallet']
        amount = int(amount)
        if amount < 100: 
            await ctx.reply("You must gamble at least $100!")
            return
        if amount > 25000:
            await ctx.reply("You can gamble up to $25,000 at once!")
            return
        if amount > balance:
            await ctx.reply("You don't have that much money idiot.")
            return
        toss = self.bank.toss()
        if toss == False: #money lost lmao. So 50% chance to lose in the first place.
            await ctx.reply(f"Oopse! Your gamble was a lose. **-${amount}**")
            self.bank.add_money(ctx.message.author.id,-amount)
            return

        result_multiplier = random.randint(10,100) / 100
        result_multiplier = result_multiplier * self.bank.get_account(ctx.message.author.id)['Multiplier']
        amount_won = round(amount * result_multiplier, 1) # % of original money won. KEEP in mind that no money deducted from user wallet.
        self.bank.add_money(ctx.message.author.id,amount_won)
        new_balance = self.bank.get_account(ctx.message.author.id)['Wallet']

        result_embed = discord.Embed(title=f"Congo! Profit of ***{int(round(result_multiplier*100,0))}**%", description=f"**Old Balance:** ${balance}\n\n**Amount Won:** ${amount_won}\n\n**New Balance:** ${new_balance}",color=discord.Color.blue())
        result_embed.set_footer(text="*Rounded figure.")
        await ctx.reply(embed=result_embed)
        #TO-DO: add footer saying the probabilioty was rounded.

'''
THIS COG CONTAINS THE FOLLOWING COMMANDS:
?inventory, ?inventory give <quantity> <item name>, 

'''

class EcoInventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bank = BankCore()

    @commands.group(invoke_without_command=True,case_insensitive=True)
    async def inventory(self, ctx,member:discord.Member=None):
        if member == None:
            member = ctx.message.author
        else:
            member = member
        bank_data = self.bank.get_account(member.id)
        inventory_data = bank_data['Inventory'] #dict object.
        em = discord.Embed(title=f"{member.name}'s Inventory.",description=f'Inventory Space: {len(inventory_data)}/25',color=discord.Color.blue())
        if inventory_data == {}:
            em.add_field(name="**None**",value="Emptier than your brain.")
        elif inventory_data != {}:
            for item_key in inventory_data:
                em.add_field(name=f'**{item_key}: {inventory_data[item_key]}**',value='')
        await ctx.reply(embed=em)

    @inventory.command()
    async def give(self,ctx,recipient: discord.Member,amount,*,item_name):
        amount = int(amount)
        user_data = self.bank.get_account(ctx.message.author.id)
        recipient_data = self.bank.get_account(recipient.id)
        print('1')
        if user_data['Inventory'].get(item_name) == None:
            await ctx.reply("You don't have that item!")
            print('2.1')
            return
        if user_data['Inventory'].get(item_name) < amount:
            await ctx.reply("You don't have that many to give!")
            print('2.2')
            return
        try:
            print('2.3')
            self.bank.remove_item(ctx.message.author.id,item_name,amount)
            self.bank.add_item(recipient.id,item_name,amount)
            await ctx.reply(f"Sucess! That item(s) has been given to **{recipient.name}**. You now have **{self.bank.get_account(ctx.message.author.id)['Inventory'].get(item_name)}** of that item left.")
        except Exception as e:
            print(e)
            await ctx.reply(f"An exception occured. Please forward this code to the owner of the bot: ```{e}```")
'''
THIS COG CONTAINS THE FOLLOWING COMMANDS AND DEFINITIONS:
FRUIT SHARDS ARE NOW TREATED AS A CURRENCY IN EcoCore. FRUITS R NOT STORED IN INVENTORY. 
FRUITS CANNOT BE TRADED THROUGH "?inventory give" and require command ?fruit trade <my_fruit> <quantity> <your_fruit> <quantity>

---
Fruits grant multipliers. These stack up to a maxmimum of 200%.
For regulation, a hard maximum inventory space of 25 is imposed.
Common: 1% per fruit 
Uncommon: 3% per fruit. Unlocks ?fruit special
Rare: 8.5% per fruit. Unlocks ?fruit awaken
Epic: 22% per fruit. Unlocks ?fruit daily
Legendary: 49% per fruit. Unlocks ?fruit claim. 100 shards for every legendary. Unlocks ?fruit grow, ?fruit convert
Insane: 90% per fruit. Revamped 300 shards for every Insane. Unlocks ?fruit merge(secret!!!)
---
fruit definition dict (shud probably move to a .yaml tho....)
?fruits(just refers to ?inventory, too lazy will code this properly after all is done)
?fruit search(30% nothing, 20% fruit shards(2-10) then 30% common fruit, 10% uncommon fruit,5% rare fruit,3% epic fruit, 1.5% legendary fruit, 0.5% insane fruit.)
?fruit gacha(20% shards[10-15], 30% common, 25% uncommon,15% rare, 6% epic, 2.8% legendary, 1.2% insane.)
?fruit upgrade(100 shards for 1 level)
?fruit awaken(at level 15, that is 1.5k shards wasted, option to evolve fruit for another 300 shards. Immediately grants the awakened version of the fruit which is guranteed 1 rarity higher, except for insane rarity which has no evolution.)
?fruit daily(free spin daily. 100 shards to 1200 shards)
?fruit special(daily special fruit discount, can be none, in fruit definition dict.)
?fruit multiplier(shows total multiplier)
?fruit claim (see above)
?fruit grow(uses fertiliser and sacrifices certain fruits for seeds to get a chance to obtain double or even triple of that fruit, provided inventory space is available. Requires 2 hours time and minimum $600 dollar investment.)
?fruit convert(conversion rate of 100:1 for money to shards i.e 100 coins for a shard.)
?fruit merge(Uses 1 Insane Fruit, 2 Legendary Fruits OR 5 Epic Fruits OR 18 Rare Fruits to obtain the secret grade - Domain Fruits.)
 --- Domain Fruits grant bonus 100% multiplier ALWAYS on top of other fruit multiplier. and only one can be owned by each player. Unlocks ?fruit domain, ?fruit erase
?fruit domain(used every day, for 1 hour increases bonus multiplier to 800%)
?fruit erase(wipes out you, or another player's inventory, at the cost of either 10k shards OR destroying the Domain Fruit.)
'''
class EcoFruitsCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bank = BankCore()

    @commands.command()
    async def fruits(self,ctx):
        em = discord.Embed(title="Your Fruits",description='')
        fruit_inventory = self.bank.get_account(ctx.message.author.id)['Fruits']
        if len(fruit_inventory) == 0:
            await ctx.reply("HOMIE YOU GOT NO FRUITS BRUH.")
            return
        for item_key in fruit_inventory.keys():
            item_quantity = fruit_inventory[item_name]
            em.add_field(name=item_key,value=item_quantity)
        await ctx.reply(embed=em)

    @commands.group(invoke_without_command=True,case_insensitive=True)
    async def fruit(self,ctx):
        #displays fruit commands list.
        await ctx.reply("Accepted subcommands: **?fruit search**")

    @fruit.command()
    async def search(self,ctx):
        pass