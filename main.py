import discord, os, json, glob, requests, asyncio
from datetime import datetime
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont

from settings import *

if not(os.path.exists("temp") and os.path.isdir("temp")): os.mkdir("temp")
if not(os.path.exists("data") and os.path.isdir("data")): os.mkdir("data")
if not(os.path.exists("usertoggle") and os.path.isdir("usertoggle")): os.mkdir("usertoggle")
datajson()

bot = commands.Bot(command_prefix="!", help_command=None, intents = discord.Intents.all())
try: tree = app_commands.CommandTree(bot)
except: tree = bot.tree


@tasks.loop(seconds = AUTO_UPDATE_FREQUENCY())
async def autoupdate():
    folders = glob.glob("data/*")
    for fol in folders:
        files = glob.glob(fol+"/*.json")
        for fil in files:
            with open(fil, 'r', encoding='utf8') as f: tdata = json.load(f)
            for ss in tdata['summoned']:
                if ss['auto'] == True:
                    tchannel = bot.get_channel(ss['channel'])
                    if tchannel != None:
                        try:
                            tfile = summonpic(tdata, "update", fil)
                            message = await tchannel.fetch_message(ss['message_id'])
                            await message.edit(attachments=[tfile])
                            print(f"> Auto Update Time {str(datetime.now())} | Successed! (FILE:{str(fil)} | SID: {str(ss['sid'])})")
                        except: print(f"［！］Auto Update Time {str(datetime.now())} | Failed due to |channel not found| (FILE:{str(fil)} | SID: {str(ss['sid'])})")
                    else: print(f"［！］Auto Update Time {str(datetime.now())} | Failed due to |channel not found| (FILE:{str(fil)} | SID: {str(ss['sid'])})")
    print(f"> Auto Update Time {str(datetime.now())} | Loop Complete!")
@autoupdate.before_loop
async def autou_before():
    await bot.wait_until_ready()
    await asyncio.sleep(1)
    print("> Loop start!")

def summonpic(tdata:dict, target:str, path):
    tuser = bot.get_user(tdata['user'])
    imgfile = requests.get(tuser.avatar.url)

    with open("data.json", "r", encoding="utf8") as f: data = json.load(f)
    data2 = data
    data2['tempid'] += 1
    with open("data.json", "w", encoding="utf8") as f: json.dump(data2, f, ensure_ascii=False)

    with open(f"temp/{str(data2['tempid'])}.png", 'wb') as f: f.write(imgfile.content)

    image = Image.open("basephoto.png")
    image2 = Image.open(f"temp/{str(data2['tempid'])}.png")
    img3 = image2.resize((268, 268))
    if tdata['convertL'] == True: img4 = img3.convert("L")
    else: img4 = img3
    image.paste(img4, POSITION.photopos())
    if tdata['texts'] != "": 
        texts = tdata['texts']
        fontsize = tdata['textedit']['size']

        draw = ImageDraw.Draw(image)
        setfont = ImageFont.truetype(FONTPATH(), fontsize)
        w = setfont.getlength(texts)
        draw.text(((image.size[0]-w)/2, tdata['textedit']['pos']), texts, font=setfont, fill = tdata['textedit']['color'])
    if tdata['opensti'] == True:
        if target == "update":
            now = datetime.now().timestamp()
            during = now - tdata['lastupdate']
            during2 = round(during)
            if during2 >= 1:
                delfire = during2 // 9
                #print(delfire, during2)
                for inum, ifire in enumerate(tdata['sticks']):
                    if (ifire['burn'] - delfire) <= 0: tdata['sticks'][inum]['burn'] = 0
                    else: tdata['sticks'][inum]['burn'] -= delfire

                tdata['lastupdate'] = datetime.now().timestamp()
                with open(path, "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)

        fireimg1 = Image.open("線香.png")
        fireimg2 = Image.open("香灰.png")
        for ss in tdata['sticks']:
            hpos = round(222*(ss['burn']*0.01))
            fhpos = abs(hpos-222)
            cfimg1 = fireimg1.crop((0, fhpos, 5, 294))
            cfimg1.paste(fireimg2, (0, 0))
            image.paste(cfimg1, (ss['pos'], 220+fhpos))

    with open("data.json", "r", encoding="utf8") as f: data = json.load(f)
    data2 = data
    data2['tempid'] += 1
    with open("data.json", "w", encoding="utf8") as f: json.dump(data2, f, ensure_ascii=False)
    image.save(f"temp/{str(data['tempid'])}.png")

    return discord.File(f"temp/{str(data['tempid'])}.png")

@bot.event
async def on_ready():
    print(f"> Logged as {str(bot.user)}")
    try: 
        await bot.tree.sync()
        print("> CommandTree Synced!")
        autoupdate.start()
    except: print("> [!]Failed to Sync CommandTree")

@tree.command(name="create", description="創建專屬遺照(X")
@app_commands.describe(user="Tag一名用戶!")
async def creare(interaction:discord.Interaction, user:str):
    if user.startswith("<@") and user.endswith(">"):
        tu = user.replace("<@", "").replace(">", "")
        try:
            uid = int(tu)
            user = bot.get_user(uid).name

            if os.path.exists(f"usertoggle/{uid}.json"): 
                with open(f"usertoggle/{uid}.json", 'r', encoding="utf8") as f: usertdata = json.load(f)
            else: usertdata = {"tfgrave":True}
            if usertdata['tfgrave'] == True:
                if not(os.path.exists(f"data/{str(interaction.user.id)}") and os.path.isdir(f"data/{str(interaction.user.id)}")): os.mkdir(f"data/{str(interaction.user.id)}")
                GDATA.create(f"data/{str(interaction.user.id)}", uid)
                embed = discord.Embed(color=0x32A431)
                embed.add_field(name="專屬~~遺照~~創建成功!", value=f"擁有者: {str(interaction.user.name)}\n對象: {str(bot.get_user(uid).name)}\n\n可執行的操作:\n``/list - 列出您擁有的遺照``\n``/summon - 召喚遺照(?``\n``/delete - 刪除遺照``\n``/edit - 編輯遺照``")
                await interaction.response.send_message(embed=embed)  
            else: await interaction.response.send_message(content="［！］此遺照的對象已將``使用者控制項: 允許/禁止被做成遺照``設定為``關閉``", ephemeral=True)
        except: await interaction.response.send_message(content="［！］發生錯誤！可能是錯誤的用戶名導致(請在user選項中tag一名用戶)，或是此機器人加入的所有伺服器中皆無此用戶!", ephemeral=True)
    else: await interaction.response.send_message(content="［！］錯誤的用戶名 => 請在user選項中tag一名用戶!", ephemeral=True)

@tree.command(name="list", description="遺照列表(?")
async def list(interaction:discord.Interaction):
    if os.path.exists(f"data/{str(interaction.user.id)}") and os.path.isdir(f"data/{str(interaction.user.id)}"):
        files = glob.glob(f"data/{str(interaction.user.id)}/*.json")
        if files != []:
            embed = discord.Embed(color = 0x32A431)
            msg = ""
            for tf in files:
                with open(tf,"r", encoding="utf8") as f: msgdata = json.load(f)
                tuser = bot.get_user(msgdata['user'])
                msg += f"墳墓ID{str(msgdata['grave'])} - 用戶ID {str(msgdata['user'])}({tuser}) 的專屬遺照\n"
            embed.add_field(name="遺照列表", value=msg)
            await interaction.response.send_message(embed = embed, ephemeral=True)
        else: await interaction.response.send_message(content="［！］您並沒有任何墓碑", ephemeral=True)
    else: await interaction.response.send_message(content="［！］您未創建過墓碑", ephemeral=True)

@tree.command(name="delete", description="刪除遺照")
@app_commands.describe(gid="輸入遺照ID")
async def deletethe(interaction: discord.Interaction, gid:int):
    files = glob.glob(f"data/{str(interaction.user.id)}/*.json")
    con = False
    for f in files:
        if f == f"data/{str(interaction.user.id)}\{str(gid)}.json": con = True
    if con == True: 
        async def confirm(interaction: discord.Interaction):
            if os.path.exists(f"data/{str(interaction.user.id)}\{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                os.remove(f"data/{str(interaction.user.id)}\{str(gid)}.json")
                embed = discord.Embed(color=0x32A431)
                embed.add_field(name = "已刪除遺照", value=f"遺照ID: {tdata['grave']}\n對象用戶ID: {tdata['user']}({str(bot.get_user(tdata['user']))})")

                await interaction.response.edit_message(embed = embed, view = None)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
        async def confirm2(interaction: discord.Interaction):
            if os.path.exists(f"data/{str(interaction.user.id)}\{str(gid)}.json"):
                view = View(timeout=None)
                button = Button(label = "確定", style = discord.ButtonStyle.danger)
                button.callback = confirm
                button2 = Button(label = "取消", style = discord.ButtonStyle.gray)
                button2.callback = cancelit
                view.add_item(button)
                view.add_item(button2)

                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)

                embed = discord.Embed(color=0xff0000)
                embed.add_field(name = "刪除遺照?", value=f"遺照ID: {tdata['grave']}\n對象用戶ID: {tdata['user']}({str(bot.get_user(tdata['user']))})")
                await interaction.response.edit_message(embed = embed, view=view)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
        
        async def cancelit(interaction: discord.Interaction):
            await interaction.response.edit_message(content = "［！］動作已取消!", view = None, embed = None)

        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
        if tdata['summoned'] != []:
            view = View(timeout=None)
            button = Button(label = "確定", style = discord.ButtonStyle.danger)
            button.callback = confirm2
            button2 = Button(label = "取消", style = discord.ButtonStyle.gray)
            button2.callback = cancelit
            view.add_item(button)
            view.add_item(button2)

            with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)

            embed = discord.Embed(color=0xff0000)
            embed.add_field(name = "此遺照還有尚未移除的生成項，是否忽略這些生成項不刪除，直接移除遺照資料?", value=f"遺照ID: {tdata['grave']}\n對象用戶ID: {tdata['user']}({str(bot.get_user(tdata['user']))})")
            await interaction.response.send_message(embed = embed, view=view, ephemeral=True)
        else:
            view = View(timeout=None)
            button = Button(label = "確定", style = discord.ButtonStyle.danger)
            button.callback = confirm
            button2 = Button(label = "取消", style = discord.ButtonStyle.gray)
            button2.callback = cancelit
            view.add_item(button)
            view.add_item(button2)

            with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)

            embed = discord.Embed(color=0xff0000)
            embed.add_field(name = "刪除遺照?", value=f"遺照ID: {tdata['grave']}\n對象用戶ID: {tdata['user']}({str(bot.get_user(tdata['user']))})")
            await interaction.response.send_message(embed = embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(content="［！］此墓碑不屬於您，或是不存在", ephemeral=True)

@tree.command(name="edit", description="編輯遺照")
@app_commands.describe(gid="輸入遺照ID")
async def edit(interaction: discord.Interaction, gid:int):
    files = glob.glob(f"data/{str(interaction.user.id)}/*.json")
    con = False
    for f in files:
        if f == f"data/{str(interaction.user.id)}\{str(gid)}.json": con = True
    if con == True: 
        #燒香編輯介面
        async def fireedit(interaction: discord.Interaction):
            #燒香開關
            async def confirm_fire(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    tdata['opensti'] = True
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                    embed, view = await fireditsummon()
                    await interaction.response.edit_message(embed = embed, view = view)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            async def clos_fire(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    tdata['opensti'] = False
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                    embed, view = await fireditsummon()
                    await interaction.response.edit_message(embed = embed, view = view)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            #清除線香
            async def cleanfire(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    tdata['sticks'] = []
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                    embed, view = await fireditsummon()
                    await interaction.response.edit_message(embed = embed, view = view)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            #線香列表
            async def listfire(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    embed = discord.Embed(color = 0x32A431)
                    msg = ""
                    for n, i in enumerate(tdata['sticks']): msg += f"[{str(n+1)}] X軸位置: {str(i['pos'])} | 線香長度: {str(i['burn'])}%\n"
                    embed.add_field(name = f"線香列表 | 遺照ID: {str(tdata['grave'])}", value=msg)
                    await interaction.response.send_message(embed = embed, ephemeral=True)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            #回到主頁面
            async def backmenu(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    embed, view = details()
                    await interaction.response.edit_message(content = None, view = view, embed = embed)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            #生成燒香編輯界面
            async def fireditsummon():
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)

                embed = discord.Embed(title = f"燒香系統編輯 - 遺照ID: {str(tdata['grave'])}", color = 0x32A431)
                if tdata['opensti'] == True: sti = "開啟"
                else: sti = "關閉"
                embed.add_field(name = "燒香系統", value=sti)
                embed.add_field(name = "線香數量", value = str(int(len(tdata['sticks']))))

                view = View(timeout=None)
                button1 = Button(label = "回上一頁", style = discord.ButtonStyle.gray)
                button1.callback = backmenu
                view.add_item(button1)
                if tdata['opensti'] == True: 
                    button2 = Button(label="燒香系統: 開啟", style = discord.ButtonStyle.green)
                    button2.callback = clos_fire
                else: 
                    button2 = Button(label="燒香系統: 關閉", style = discord.ButtonStyle.danger)
                    button2.callback = confirm_fire
                view.add_item(button2)
                button3 = Button(label = "清除所有線香", style = discord.ButtonStyle.danger)
                button3.callback = cleanfire
                view.add_item(button3)
                button4 = Button(label = "線香列表", style = discord.ButtonStyle.gray)
                button4.callback = listfire
                view.add_item(button4)
                
                return embed, view

            #燒香系統編輯
            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                embed, view = await fireditsummon()
                await interaction.response.edit_message(embed = embed, view = view)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

        #預覽
        async def prev(interaction: discord.Interaction):
            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                tuser = bot.get_user(tdata['user'])
                await interaction.response.defer(ephemeral=True, thinking=False)
                await interaction.followup.send(content = f"{tuser.name} 的專屬~~遺照~~", ephemeral=True, file = summonpic(tdata, "perv", None))
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

        #總表生成function
        def details():
            with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
            embed = discord.Embed(title = "遺照詳細資料", color = 0x32A431)
            embed.add_field(name = "ID", value=str(tdata['grave']), inline=True)
            embed.add_field(name = "對象", value=f"ID: {str(tdata['user'])}\n用戶名稱: {str(bot.get_user(tdata['user']))}", inline=True)
            gtext = tdata['texts']
            if gtext == "": gtext = "無"
            embed.add_field(name = "墓誌銘", value=gtext, inline=False)
            if tdata['opensti'] == True: sti = "開啟"
            else: sti = "關閉"
            embed.add_field(name = "燒香功能", value=sti, inline=True)
            if tdata['convertL'] == True: cL = "開啟"
            else: cL = "關閉"
            embed.add_field(name = "圖片灰階", value=cL, inline=True)

            view = View(timeout=None)
            button1 = Button(label="預覽", style = discord.ButtonStyle.blurple)
            button1.callback = prev
            button2 = Button(label="編輯墓誌銘", style = discord.ButtonStyle.gray)
            button2.callback = gtextedit
            button4 = Button(label="燒香系統設定", style = discord.ButtonStyle.gray)
            button4.callback = fireedit
            
            if tdata['convertL'] == True: 
                button5 = Button(label="圖片灰階: 開啟", style = discord.ButtonStyle.green)
                button5.callback = clos_convertL
            else: 
                button5 = Button(label="圖片灰階: 關閉", style = discord.ButtonStyle.danger)
                button5.callback = confirm_convertL
            button6 = Button(label = "管理生成遺照", style = discord.ButtonStyle.gray)
            button6.callback = summonedit
            view.add_item(button1)
            view.add_item(button2)
            view.add_item(button4)
            view.add_item(button5)
            view.add_item(button6)

            return embed, view
        
        #生成項目管理
        async def summonedit(interaction:discord.Interaction):
            #回到主頁面
            async def backmenu(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    embed, view = details()
                    await interaction.response.edit_message(content = None, view = view, embed = embed)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            async def summon_select(interaction:discord.Interaction):
                #回到生成管理子表
                async def backsue(interaction: discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"): await interaction.response.edit_message(content = None, view = mview, embed = membed)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                
                #功能調整
                #自動更新
                async def autorfunopen(interaction: discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        ts, tsn = None, None
                        for num, i in enumerate(tdata['summoned']):
                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                        if ts != None:
                            con = True
                            if LIMIT.summonautorefresh() == True:
                                for ss in tdata['summoned']:
                                    if ss['auto'] == True: con = False
                            if con == True:
                                tdata['summoned'][tsn]['auto'] = True
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                                embed, view = await summonselmenu()
                                await interaction.response.edit_message(embed = embed, view = view)
                            else: await interaction.response.send_message(content="［！］為避免CPU燒壞，每個專屬遺照生成出的項目僅能有一項開啟自動刷新", ephemeral=True)
                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                async def autorfunclose(interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        ts, tsn = None, None
                        for num, i in enumerate(tdata['summoned']):
                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                        if ts != None:
                            tdata['summoned'][tsn]['auto'] = False
                            with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                            embed, view = await summonselmenu()
                            await interaction.response.edit_message(embed = embed, view = view)
                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                
                #刪除生成項
                async def deletesummon(interaction: discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        ts, tsn = None, None
                        for num, i in enumerate(tdata['summoned']):
                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                        if ts != None:
                            try:
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                                #ts = tdata['summoned'][int(select.values[0])]

                                message = await bot.get_channel(int(ts['channel'])).fetch_message(int(ts['message_id']))
                                await message.delete()

                                tdata2 = tdata
                                del tdata2['summoned'][int(tsn):int(tsn)+1]

                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata2, f, ensure_ascii=False)

                                embed, view = details()
                                channel = bot.get_channel(int(ts['channel']))
                                if channel != None: ssmsg = f"{channel.guild.name} | {channel.name}"
                                else: ssmsg = "!! 無法存取 !!"
                                await interaction.response.edit_message(content = f"［！］已成功刪除生成項目(生成項ID: {ts['sid']}，生成於頻道ID: {ts['channel']}({ssmsg})，所屬專屬遺照ID: {tdata['grave']})", view = view, embed = embed)
                            except:
                                async def deletesummonconfirm(interaction:discord.Interaction):
                                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                                        ts, tsn = None, None
                                        for num, i in enumerate(tdata['summoned']):
                                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                                        if ts != None:
                                            #ts = tdata['summoned'][int(select.values[0])]

                                            tdata2 = tdata
                                            del tdata2['summoned'][int(tsn):int(tsn)+1]
                                            with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata2, f, ensure_ascii=False)

                                            embed, view = details()
                                            channel = bot.get_channel(int(ts['channel']))
                                            if channel != None: ssmsg = f"{channel.guild.name} | {channel.name}"
                                            else: ssmsg = "!! 無法存取 !!"
                                            await interaction.response.edit_message(content = f"［！］已成功從資料庫中移除生成項目(生成項ID: {ts['sid']}，生成於頻道ID: {ts['channel']}({ssmsg})，所屬專屬遺照ID: {tdata['grave']})", view = view, embed = embed)
                                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

                                async def deletesummonclose(interaction:discord.Interaction):
                                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                                        ts, tsn = None, None
                                        for num, i in enumerate(tdata['summoned']):
                                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                                        if ts != None:
                                            #ts = tdata['summoned'][int(select.values[0])]
                                            embed, view = details()
                                            await interaction.response.edit_message(content = None, view = view, embed = embed)
                                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                                view = View(timeout=None)
                                button = Button(label = "確定", style = discord.ButtonStyle.danger)
                                button.callback = deletesummonconfirm
                                button2 = Button(label = "取消", style = discord.ButtonStyle.gray)
                                button2.callback = deletesummonclose

                                view.add_item(button)
                                view.add_item(button2)

                                await interaction.response.edit_message(content = "［！］機器人無法存取此生成項之訊息(可能訊息已經遭刪除，或是在機器人的存取範圍之外)\n［？］是否從資料庫中移除此生成項(但可能無法刪除訊息)?", embed = None, view = view)
                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

                #強制更新
                async def forceupdate(interaction:discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        ts, tsn = None, None
                        for num, i in enumerate(tdata['summoned']):
                            if i["sid"] == int(select.values[0]): ts, tsn = i, num
                        if ts != None:
                            tchannel = bot.get_channel(tdata['summoned'][tsn]['channel'])
                            if tchannel != None:
                                await interaction.response.defer(thinking=False, ephemeral=True)
                                try:
                                    tfile = summonpic(tdata, "update", f"data/{str(interaction.user.id)}/{str(gid)}.json")
                                    message = await tchannel.fetch_message(tdata['summoned'][tsn]['message_id'])
                                    await message.edit(attachments=[tfile])
                                    await interaction.followup.edit_message(content="［！］強制刷新成功！", message_id=interaction.message.id)
                                except: await interaction.followup.send(content="［！］強制刷新失敗！", ephemeral=True)
                            else: await interaction.response.edit_message(content = "［！］此訊息無法被存取！", view = None, embed = None)
                        else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

                #生成項目細管理function
                async def summonselmenu():
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    ts = None
                    for i in tdata['summoned']:
                        if i["sid"] == int(select.values[0]): ts = i
                    if ts != None:
                        embed = discord.Embed(color = 0x32A431)
                        sschannel = bot.get_channel(ts['channel'])
                        if sschannel != None: 
                            sssmsg = f"{sschannel.guild.name} | {sschannel.name}"
                            try: 
                                await sschannel.fetch_message(ts['message_id'])
                                stamsg = "正常顯示"
                            except: stamsg = "無法存取"
                        else: sssmsg, stamsg = "!! 無法存取 !!", "無法存取"
                        if ts['auto'] == True: autor = "開啟"
                        else: autor = "關閉"
                        embed.add_field(name = f"遺照ID: {tdata['grave']} | 生成項ID: {ts['sid']}", value=f"遺照對象ID: {tdata['user']}({str(bot.get_user(tdata['user']))})\n生成於頻道ID:{str(ts['channel'])}({sssmsg})\n自動刷新: {autor}\n狀態: {stamsg}")

                        view = View(timeout=None)
                        button = Button(label = "回上一步", style = discord.ButtonStyle.gray)
                        button.callback = backsue
                        button2 = Button(label = "刷新", style = discord.ButtonStyle.blurple)
                        button2.callback = forceupdate
                        button3 = Button(label = "刪除", style = discord.ButtonStyle.danger)
                        button3.callback = deletesummon
                        if ts['auto'] == True: 
                            button4 = Button(label = "自動刷新: 開啟", style = discord.ButtonStyle.green)
                            button4.callback = autorfunclose
                        else: 
                            button4 = Button(label = "自動刷新: 關閉", style = discord.ButtonStyle.danger)
                            button4.callback = autorfunopen

                        view.add_item(button)
                        view.add_item(button2)
                        view.add_item(button3)
                        view.add_item(button4)

                        return embed, view
                    else: return None, None
                
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    ts = None
                    for i in tdata['summoned']:
                        if i["sid"] == int(select.values[0]): ts = i
                    if ts != None:
                        embed, view = await summonselmenu()
                        await interaction.response.edit_message(embed = embed, view = view)
                    else: await interaction.response.edit_message(content = "［！］此生成項目不存在！", view = None, embed = None)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            
            ###
            #生成管理子表function
            async def suemenu():
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                embed = discord.Embed(title = f"遺照ID: {tdata['grave']}", color = 0x32A431)
                if len(tdata['summoned']) != 0: 
                    embed.add_field(name = f"遺照生成管理 | 已生成: {str(len(tdata['summoned']))}個", value="請使用下拉選單選取", inline=True)

                    options = []
                    for n, s in enumerate(tdata['summoned']):
                        schannel = bot.get_channel(s['channel'])
                        if schannel != None: 
                            ssmsg = f"{schannel.guild.name} | {schannel.name}"
                            try: 
                                await schannel.fetch_message(s['message_id'])
                                stamsg = "正常顯示"
                            except: stamsg = "無法存取"
                        else: ssmsg, stamsg = "!! 無法存取 !!", "無法存取"
                        options.append(discord.SelectOption(label = f"ID: {s['sid']} | 狀態: {stamsg}", value=s['sid'], description=f"頻道ID: {s['channel']}({ssmsg}) | 訊息ID: {str(s['message_id'])}"))

                    select = Select(placeholder="請選擇一個項目．．．", options=options)
                    select.callback = summon_select
                    view = View(timeout=None)
                    button = Button(label="回上一步", style = discord.ButtonStyle.gray)
                    button.callback = backmenu
                    view.add_item(select)
                    view.add_item(button)
                    return embed, view, select
                else: 
                    embed.add_field(name = f"遺照生成管理 | 已生成: {str(len(tdata['summoned']))}個", value="此遺照尚未被生成", inline=True)

                    view = View(timeout=None)
                    button = Button(label="回上一步", style = discord.ButtonStyle.gray)
                    button.callback = backmenu
                    view.add_item(button)
                    return embed, view, None
            
            #生成管理子表
            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                await interaction.response.defer(thinking=False, ephemeral=True)
                await interaction.followup.edit_message(message_id=interaction.message.id, content="［！］請稍等候．．．", view = None)
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                membed, mview, select = await suemenu()

                await interaction.followup.edit_message(message_id=interaction.message.id, content=None, embed = membed, view = mview)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

        #灰階設定
        async def confirm_convertL(interaction:discord.Interaction):
            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                tdata['convertL'] = True
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                embed, view = details()
                await interaction.response.edit_message(embed = embed, view = view)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
        async def clos_convertL(interaction:discord.Interaction):
            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                tdata['convertL'] = False
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                embed, view = details()
                await interaction.response.edit_message(embed = embed, view = view)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

        #墓誌銘
        async def gtextedit(interaction:discord.Interaction):
            #回到主頁面
            async def backmenu(interaction:discord.Interaction):
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    embed, view = details()
                    await interaction.response.edit_message(content = None, view = view, embed = embed, attachments=[])
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

            #修改墓誌銘
            class gtextmodal(Modal, title = "編輯墓誌銘"):
                answer = discord.ui.TextInput(label = "在此填入自訂墓誌銘", style=discord.TextStyle.short, placeholder="輸入一些文字(留空可清除墓誌銘)...", required=False)
                async def on_submit(self, interaction:discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        tdata['texts'] = str(self.answer.value)
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                        embed, view = await gtexteditmenu(interaction)
                        await interaction.response.defer(thinking=False, ephemeral=True)
                        await interaction.followup.edit_message(embed = embed, view = view, attachments=[summonpic(tdata, "perv", None)], content=None, message_id=interaction.message.id)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            async def gtextmod(interaction:discord.Interaction): await interaction.response.send_modal(gtextmodal())

            #修改字體大小
            class tsizemodal(Modal, title = "編輯字體大小"):
                answer = discord.ui.TextInput(label = "在此填入正整數，決定字體大小", style=discord.TextStyle.short, placeholder="輸入一個數字．．．", required=True)
                async def on_submit(self, interaction:discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        try:
                            if int(self.answer.value) > 0:
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                                tdata['textedit']['size'] = int(self.answer.value)
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                                embed, view = await gtexteditmenu(interaction)
                                await interaction.response.defer(thinking=False, ephemeral=True)
                                await interaction.followup.edit_message(embed = embed, view = view, attachments=[summonpic(tdata, "perv", None)], message_id=interaction.message.id)
                            else: await interaction.response.edit_message(content = "［！］字體大小不能小於或等於零！")
                        except: await interaction.response.edit_message(content = "［！］輸入的數字並非整數！")
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            async def tsizemod(interaction:discord.Interaction): await interaction.response.send_modal(tsizemodal())

            #設定垂直位置
            class tposmodal(Modal, title = "編輯墓誌銘垂直位置"):
                answer = discord.ui.TextInput(label = "在此填入正整數，設定墓誌銘垂直位置", style=discord.TextStyle.short, placeholder="輸入一個數字．．．", required=True)
                async def on_submit(self, interaction:discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        try:
                            if int(self.answer.value) >= 0:
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                                tdata['textedit']['pos'] = int(self.answer.value)
                                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                                embed, view = await gtexteditmenu(interaction)
                                await interaction.response.defer(thinking=False, ephemeral=True)
                                await interaction.followup.edit_message(embed = embed, view = view, attachments=[summonpic(tdata, "perv", None)], message_id=interaction.message.id)
                            else: await interaction.response.edit_message(content = "［！］字體大小不能小於零！")
                        except: await interaction.response.edit_message(content = "［！］輸入的數字並非整數！")
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
            async def tposmod(interaction:discord.Interaction): await interaction.response.send_modal(tposmodal())

            async def gtextcolor(interaction:discord.Interaction):
                async def backgtext(interaction: discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"): await interaction.response.edit_message(content = None, view = mview, embed = membed)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                async def gtextcoloredit(interaction:discord.Interaction):
                    if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                        tdata['textedit']['color'] = select.values[0]
                        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                        embed, view = await gtexteditmenu(interaction)
                        await interaction.response.defer(thinking=False, ephemeral=True)
                        await interaction.followup.edit_message(embed = embed, view = view, attachments=[summonpic(tdata, "perv", None)], message_id=interaction.message.id)
                    else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])
                if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                    view = View()
                    options = []
                    for c in PHOTO_COLORS(): options.append(discord.SelectOption(label = c, value = c))
                    select = Select(placeholder="選擇一種顏色．．．", options=options)
                    select.callback = gtextcoloredit
                    view.add_item(select)

                    button = Button(label = "回上一頁", style = discord.ButtonStyle.gray)
                    button.callback = backgtext
                    view.add_item(button)
                    await interaction.response.edit_message(view = view)
                else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

            #墓誌銘編輯介面
            async def gtexteditmenu(interaction:discord.Interaction): 
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                gtext = tdata['texts']
                if gtext == "": gtext = "無"
                embed = discord.Embed(color=0x32A431, title = "墓誌銘編輯頁面", description=f"目前墓誌銘為: {gtext}")
                embed.add_field(name = "字體大小", value=str(tdata['textedit']['size']))
                embed.add_field(name = "顏色", value=tdata['textedit']['color'])
                embed.add_field(name = "垂直位置", value=str(tdata['textedit']['pos'])+"px")
                embed.set_footer(text="附圖為遺照實時預覽")

                view = View(timeout=None)
                button1 = Button(label = "設定字體大小", style = discord.ButtonStyle.gray)
                button1.callback = tsizemod
                button2 = Button(label = "設定顏色", style = discord.ButtonStyle.gray)
                button2.callback = gtextcolor
                button3 = Button(label = "設定垂直位置", style = discord.ButtonStyle.gray)
                button3.callback = tposmod
                button4 = Button(label = "編輯墓誌銘內容", style = discord.ButtonStyle.blurple)
                button4.callback = gtextmod
                button5 = Button(label = "回上一頁", style = discord.ButtonStyle.gray)
                button5.callback = backmenu

                view.add_item(button5)
                view.add_item(button1)
                view.add_item(button2)
                view.add_item(button3)
                view.add_item(button4)

                return embed, view

            if os.path.exists(f"data/{str(interaction.user.id)}/{str(gid)}.json"):
                with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
                membed, mview = await gtexteditmenu(interaction)
                await interaction.response.defer(ephemeral=True, thinking=False)
                await interaction.followup.edit_message(embed = membed, view = mview, attachments=[summonpic(tdata, "perv", None)], content=None, message_id=interaction.message.id)
            else: await interaction.response.edit_message(content = "［！］遺照不存在！", view = None, embed = None, attachments=[])

        #總表生成
        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
        embed, view = details()

        await interaction.response.send_message(embed = embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(content="［！］此墓碑不屬於您，或是不存在", ephemeral=True)

@tree.command(name="summon", description="遺照召喚師(?")
@app_commands.describe(gid="輸入遺照ID")
async def summon(interaction: discord.Interaction, gid:int):
    #上香
    async def thestickset(interaction:discord.Interaction, finalpos:int, tdata:dict, path:str): 
        now = datetime.now().timestamp()
        during = now - tdata['lastupdate']
        during2 = round(during)
        if during2 >= 1: delfire = during2 // 9
        else: delfire = 0

        stickf = GDATA.stick(finalpos)
        stickf['burn'] += delfire
        tdata['sticks'].append(stickf)
        with open(path, "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
        await interaction.followup.edit_message(attachments=[summonpic(tdata, "update", path)], message_id=interaction.message.id)
    async def setfire(interaction:discord.Interaction):
        await interaction.response.defer(thinking=False, ephemeral=True)
        found = False
        path = None
        for folder in glob.glob("data/*"):
            for item in glob.glob(folder+"/*.json"):
                with open(item, 'r', encoding='utf8') as f: fdata = json.load(f)
                for sss in fdata['summoned']: 
                    if sss['message_id'] == interaction.message.id: 
                        tdata = fdata
                        found = True
                        path = item
                        break
        if found: 
            if tdata['opensti'] == True: 
                con = True
                for ss in tdata['sticks']: 
                    if ss['pos'] == 240: con = False
                if con == False:
                    con2 = True
                    for ss in tdata['sticks']: 
                        if ss['pos'] == 250: con2 = False
                    if con2 == False:
                        posindex3, posindex4 = None, None
                        for i in range(1, 24):
                            con3 = True
                            for ss in tdata['sticks']:
                                if ss['pos'] == (25+i)*10: con3 = False
                            if con3 == True: 
                                posindex3 = i
                                break
                        for i in range(1, 24):
                            con3 = True
                            for ss in tdata['sticks']:
                                if ss['pos'] == (24-i)*10: con3 = False
                            if con3 == True: 
                                posindex4 = i
                                break
                        if posindex3 != None and posindex4 != None:
                            if posindex3 <= posindex4: await thestickset(interaction, (25+posindex3)*10, tdata, path)
                            else: await thestickset(interaction, (24-posindex4)*10, tdata, path)
                        elif posindex3 != None and posindex4 == None: await thestickset(interaction, (25+posindex3)*10, tdata, path)
                        elif posindex3 == None and posindex4 != None: await thestickset(interaction, (24-posindex4)*10, tdata, path)
                        else: await interaction.response.send_message(content = "［！］香爐已滿！", ephemeral=True)
                    else: await thestickset(interaction, 250, tdata, path)
                else: await thestickset(interaction, 240, tdata, path)
            else: await interaction.followup.send_message(content = "［！］此遺照的香爐沒有開放！", ephemeral=True)
        else: await interaction.followup.send_message(content = "［！］此生成項並未被記錄於資料庫！", ephemeral=True)
    
    #遺照更新
    async def summonupdate(interaction:discord.Interaction):
        await interaction.response.defer(thinking=False, ephemeral=True)
        found = False
        path = None
        for folder in glob.glob("data/*"):
            for item in glob.glob(folder+"/*.json"):
                with open(item, 'r', encoding='utf8') as f: fdata = json.load(f)
                for sss in fdata['summoned']: 
                    if sss['message_id'] == interaction.message.id: 
                        tdata = fdata
                        found = True
                        path = item
                        break
        if found: 
            tuser = bot.get_user(tdata['user'])
            tfile = summonpic(tdata, "update", path)

            await interaction.followup.edit_message(attachments=[tfile], message_id=interaction.message.id)
        else: await interaction.followup.send_message(content = "［！］此生成項並未被記錄於資料庫！", ephemeral=True)
    
    files = glob.glob(f"data/{str(interaction.user.id)}/*.json")
    con = False
    for f in files:
        if f == f"data/{str(interaction.user.id)}\{str(gid)}.json": con = True
    if con == True: 
        with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "r", encoding="utf8") as f: tdata = json.load(f)
        con2 = False
        try: 
            tuser = bot.get_user(tdata['user']).name
            con2 = True
        except: await interaction.response.send_message(content="［！］此墓碑之對象無法被機器人存取(可能機器人加入的所有伺服器皆無此用戶)", ephemeral=True)
        if con2 == True:
            if os.path.exists(f"usertoggle/{tdata['user']}.json"): 
                with open(f"usertoggle/{tdata['user']}.json", 'r', encoding="utf8") as f: usertdata = json.load(f)
            else: usertdata = {"tfgrave":True}
            if usertdata['tfgrave'] == True:
                if len(tdata['summoned']) <= LIMIT.maxsummon():
                    tuser = bot.get_user(tdata['user'])
                    await interaction.response.defer(ephemeral=True, thinking=False)
                    tfile = summonpic(tdata, "update", f"data/{str(interaction.user.id)}/{str(gid)}.json")

                    view = View(timeout=None)
                    button1 = Button(label = "上香", style = discord.ButtonStyle.blurple)
                    button1.callback = setfire
                    view.add_item(button1)
                    button2 = Button(label = "刷新", style = discord.ButtonStyle.green)
                    button2.callback = summonupdate
                    view.add_item(button2)
                    message = await bot.get_channel(interaction.channel_id).send(content=f"{tuser.name} 的專屬~~遺照~~", file = tfile, view = view)

                    with open("data.json", "r", encoding="utf8") as f: datasid = json.load(f)
                    datasid2 = datasid
                    datasid2['summonid'] += 1
                    with open("data.json", "w", encoding="utf8") as f: json.dump(datasid2, f, ensure_ascii=False)
                    summondata = GDATA.summon_format(interaction.channel_id, message.id, datasid['summonid'])
                    tdata['summoned'].append(summondata)
                    with open(f"data/{str(interaction.user.id)}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tdata, f, ensure_ascii=False)
                    await interaction.followup.send(content=f"［！］使用``/edit``可管理生成出的遺照", ephemeral=True)
                else: await interaction.response.send_message(content=f"［！］此專屬遺照您已生成{str(LIMIT.maxsummon())}個，無法繼續生成。\n［！］可使用``/edit``管理生成出的遺照", ephemeral=True)
            else: await interaction.response.send_message(content="［！］此遺照的對象已將``使用者控制項: 允許/禁止被做成遺照``設定為``關閉``", ephemeral=True)
    else: await interaction.response.send_message(content="［！］此遺照不屬於您，或是不存在", ephemeral=True)

@tree.command(name="info", description="系統資訊")
async def info(interaction:discord.Interaction):
    embed = discord.Embed(color = 0x32A431)
    embed.add_field(name = "關於 /toggle 指令...", value="每位用家皆有權利使用 ``/toggle`` 指令控制自己是否可被製成遺照", inline = False)
    embed.add_field(name = "機器人相關資訊", value=f"""Made by pour33142GX

Version: {VERSION()}""", inline = False)
    embed.add_field(name = "圖片引用資訊", value="遺照 from 迷因倉庫\n=> https://memes.tw/zh-Hans/wtf?template=5532", inline=False)
    await interaction.response.send_message(embed = embed)

@tree.command(name = "toggle", description="控制自己是否可被做成遺照")
async def toggle(interaction:discord.Interaction):
    async def toggleopen(interaction:discord.Interaction):
        with open(f"usertoggle/{str(interaction.user.id)}.json", "r", encoding = "utf8") as f: tdata = json.load(f)
        tdata['tfgrave'] = True
        with open(f"usertoggle/{str(interaction.user.id)}.json", "w", encoding = "utf8") as f: json.dump(tdata, f, ensure_ascii=False)
        view, embed = await togglesummon()
        await interaction.response.edit_message(view = view)
    async def toggleclose(interaction:discord.Interaction):
        with open(f"usertoggle/{str(interaction.user.id)}.json", "r", encoding = "utf8") as f: tdata = json.load(f)
        tdata['tfgrave'] = False
        with open(f"usertoggle/{str(interaction.user.id)}.json", "w", encoding = "utf8") as f: json.dump(tdata, f, ensure_ascii=False)
        view, embed = await togglesummon()
        await interaction.response.edit_message(view = view)
    async def togglesummon():
        with open(f"usertoggle/{str(interaction.user.id)}.json", "r", encoding = "utf8") as f: tdata = json.load(f)
        embed = discord.Embed(color=0x32A431)
        embed.add_field(name = "使用者控制項: 允許/禁止被做成遺照", value="使用者可控制自己是否能被其他用戶製作成遺照。若關閉，任何人(包括您自己)也無法使用``/create``新建您的專屬遺照。已經建立的您的專屬遺照皆將無法使用``/summon``指令進行生成，但仍可使用其他功能。您的專屬遺照已經生成出的生成項仍可使用包括但不限於上香、刷新、設定、刪除。")

        view = View(timeout=None)
        if tdata['tfgrave'] == True: 
            button = Button(label = "目前狀態:允許", style = discord.ButtonStyle.green)
            button.callback = toggleclose
        else: 
            button = Button(label = "目前狀態: 禁止", style = discord.ButtonStyle.danger)
            button.callback = toggleopen
        view.add_item(button)
        return view, embed

    if not(os.path.exists(f"usertoggle/{str(interaction.user.id)}.json")): 
        with open(f"usertoggle/{str(interaction.user.id)}.json", "w", encoding = "utf8") as f: json.dump(GDATA.toggle(), f, ensure_ascii=False)
    with open(f"usertoggle/{str(interaction.user.id)}.json", "r", encoding = "utf8") as f: tdata = json.load(f)
    view, embed = await togglesummon()
    
    await interaction.response.send_message(embed = embed, view = view, ephemeral=True)

bot.run(TOKEN())