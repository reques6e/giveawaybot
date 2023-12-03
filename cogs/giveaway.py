import nextcord
import datetime
import sqlite3
import asyncio
import random
from config import staff_role
from nextcord.ext import commands
from nextcord.ui import Button, View

connection = sqlite3.connect('db/giveaway.db')
cursor = connection.cursor()


class GCModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Создание розыгрыша")
        self.oneGC = nextcord.ui.TextInput(
            label="Приз", placeholder="Роль, 100 монет")
        self.add_item(self.oneGC)
        self.twoGC = nextcord.ui.TextInput(
            label="Описание", placeholder="...", style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.twoGC)
        self.threeGC = nextcord.ui.TextInput(
            label="Время (в минутах)", placeholder="5")
        self.add_item(self.threeGC)
        self.fourGC = nextcord.ui.TextInput(
            label="Максимальное количество победителей", placeholder="10")
        self.add_item(self.fourGC)
        self.fiveGC = nextcord.ui.TextInput(
            label="ID канала", placeholder="1077992294424252516", default_value=str(channel_id))
        self.add_item(self.fiveGC)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        time = int(self.threeGC.value)
        author = interaction.user
        join = Button(style=nextcord.ButtonStyle.grey,
                      label='Участвовать')
        
        async def join_callback(interaction: nextcord.Interaction):
            cursor.execute("SELECT userid FROM giveusers WHERE userid = {}".format(interaction.user.id))
            check_usr = cursor.fetchone()
            if check_usr is None:
                check_usr = [0]
            if interaction.user.id != check_usr[0] and interaction.user.id != author.id:
                cursor.execute("INSERT INTO giveusers(userid) VALUES ({})".format(interaction.user.id))
                connection.commit()
                await interaction.send("Вы успешно приняли участие в розыгрыше на {}".format(self.oneGC.value), ephemeral=True)
            else:
                cursor.execute("SELECT userid FROM giveusers")
                all_users = cursor.fetchall()
                text = ''
                for i in all_users:
                    memb = interaction.guild.get_member(i[0])
                    text += '{} '.format(memb.mention)
                if text == '':
                    text='Пока никого...'
                embmemb = nextcord.Embed(description=text,
                                         color=nextcord.Colour.from_rgb(47, 49, 54))
                embmemb.timestamp = datetime.datetime.now()
                await interaction.send(embed=embmemb, ephemeral=True)

        join.callback = join_callback
        view = View()
        view.add_item(join)

        emb = nextcord.Embed(title='Розыгрыш: {}'.format(self.oneGC.value),
                             description=self.twoGC.value,
                             color=nextcord.Colour.from_rgb(47, 49, 54))
        emb.add_field(name='> Макс. победителей', value='```{}```'.format(self.fourGC.value))
        emb.add_field(name='> Время', value='```{} ч. {} мин.```'.format(time//60, time%60))
        emb.set_footer(text=interaction.user, icon_url=interaction.user.avatar)
        emb.timestamp = datetime.datetime.now()
        msg = await interaction.guild.get_channel(int(self.fiveGC.value)).send(embed=emb, view=view)
        await interaction.response.send_message('Успех!', ephemeral=True)
        while time != 0:
            await asyncio.sleep(60)
            time -= 1
            cursor.execute("SELECT userid FROM giveusers")
            all_users = cursor.fetchall()
            count_users = []
            for i in all_users:
                count_users.append(i[0])
            join = Button(style=nextcord.ButtonStyle.grey,
                          label='Участвовать [{}]'.format(len(count_users)))
            join.callback = join_callback
            view2 = View(timeout=None)
            view2.add_item(join)
            emb = nextcord.Embed(title='Розыгрыш: {}'.format(self.oneGC.value),
                             description=self.twoGC.value,
                             color=nextcord.Colour.from_rgb(47, 49, 54))
            emb.add_field(name='> Макс. победителей', value='```{}```'.format(self.fourGC.value))
            emb.add_field(name='> Время', value='```{} ч. {} мин.```'.format(time//60, time%60))
            emb.set_footer(text=interaction.user, icon_url=interaction.user.avatar)
            emb.timestamp = datetime.datetime.now()
            await msg.edit(embed=emb, view=view2)
        if time == 0:
            cursor.execute("SELECT userid FROM giveusers")
            all_users = cursor.fetchall()
            for_wins = []
            for i in all_users:
                for_wins.append(i[0])
            winner = random.choices(for_wins, k=int(self.fourGC.value))
            emb = nextcord.Embed(title='Розыгрыш: {}'.format(self.oneGC.value),
                             description=self.twoGC.value,
                             color=nextcord.Colour.from_rgb(47, 49, 54))
            emb.add_field(name='> Макс. победителей', value='```{}```'.format(self.fourGC.value))
            emb.add_field(name='> Время', value='```0 ч. 0 мин.```')
            emb.set_footer(text=interaction.user, icon_url=interaction.user.avatar)
            emb.timestamp = datetime.datetime.now()
            if int(self.fourGC.value) <= 1:
                await msg.edit("**Победитель: {} | {}**".format(interaction.guild.get_member(winner[0]).mention, self.oneGC.value), embed=emb, view=None)
            else:
                text2 = ''
                for i2 in winner:
                    text2 += '{} '.format(interaction.guild.get_member(i2).mention)
                await msg.edit("**Победитель: {}| {}**".format(text2, self.oneGC.value), embed=emb, view=None)
            cursor.execute("DELETE FROM giveusers")
            connection.commit()



class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("GiveAway - work")
        cursor.execute("""CREATE TABLE IF NOT EXISTS giveusers(
            userid BIGINT);
        """)
        connection.commit()

    @nextcord.slash_command(name='givecreate', description='Создать розыгрыш')
    async def givecreate(self, interaction: nextcord.Interaction):
        role = interaction.guild.get_role(staff_role)
        if role in interaction.user.roles: 
            global channel_id
            channel_id = interaction.channel_id
            await interaction.response.send_modal(GCModal())
        else:
            await interaction.send('Ошибка доступа')

def setup(bot):
    bot.add_cog(Giveaway(bot))
