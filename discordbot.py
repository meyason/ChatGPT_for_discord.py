import discord
from discord import app_commands
from dotenv import load_dotenv
load_dotenv()
import os
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MY_SERVER_ID = int(os.getenv("MY_SERVER_ID"))
import requests


intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# 起動時処理
@client.event
async def on_ready():
  # 起動確認
  print('ログインしました')
    
###############################################################
# ChatGPT関連
from langchainbot import chatgptorg
import openai
from openai import OpenAI
from PIL import Image
from io import BytesIO
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# インスタンス生成
cgo = chatgptorg(OPENAI_API_KEY)

# GPT-4
@tree.command(name="gpt", description="GPT-4で文章を生成します")
async def gpt(interaction: discord.Interaction, text: str):
  await interaction.response.defer()
  client = OpenAI()
  response = client.chat.completions.create(
      model = "gpt-4-1106-preview",
      messages=[
          {"role": "system", "content": "あなたはDiscordのbotで，饒舌に話します．"},
          {"role": "user", "content": text},
      ]
  )
  # discordの文字数上限2000字に引っかかったら分割して送信
  message = response.choices[0].message.content
  if len(message) > 2000:
    for i in range(0, len(message), 2000):
      await interaction.followup.send(message[i:i+2000])
  else:
    await interaction.followup.send(message)
    return

# メンション呼び出し・メモリ付き
@client.event
async def on_message(message):
    if client.user in message.mentions:
        server = message.guild.id
        message.content = message.content.replace("<@1074516884399063051>", "")
        response = cgo.output(server, message.content)
        # discordの文字数上限2000字に引っかかったら分割して送信
        if len(response) > 2000:
            for i in range(0, len(response), 2000):
                await message.channel.send(response[i:i+2000])
        else:
          await message.channel.send(response)
        return

# メモリ削除
@tree.command(name="talkreset", description="会話履歴を削除")
async def langchainstop_command(interaction: discord.Interaction):
  await interaction.response.defer()
  cgo.reset_history(interaction.guild.id)
  await interaction.followup.send("リセットしました。")

# DALL-E
@tree.command(name="img_gen", description="DALL-Eで画像を生成します")
async def dall_e_command(interaction: discord.Interaction, text: str):
  await interaction.response.defer()
  try:
    client = OpenAI()
    response = client.images.generate(
      model="dall-e-2",
      prompt=text,
      size="1024x1024",
      quality="standard",
      n=1,
    )
  except:
     await interaction.followup.send("画像生成に失敗しました。")
     return
  # 受け取った画像をdiscordに送信
  image_url = response.data[0].url
  image = Image.open(BytesIO(requests.get(image_url).content))
  image.save("image.png")
  await interaction.followup.send(file=discord.File("image.png"))

###############################################################

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# DeepL翻訳コマンド
@tree.command(name="translate", description="翻訳先の言語コードを指定すれば、翻訳できます")
# 説明文
@app_commands.describe(
  lang="翻訳先言語のコード",
  sentence="翻訳したい文章"
)
# 選択肢
@app_commands.choices(
  lang=[
    discord.app_commands.Choice(name="日本語", value="JA"),
    discord.app_commands.Choice(name="英語", value="EN"),
    discord.app_commands.Choice(name="中国語", value="ZH"),
    discord.app_commands.Choice(name="韓国語", value="KO"),
    discord.app_commands.Choice(name="ドイツ語", value="DE"),
    discord.app_commands.Choice(name="フランス語", value="FR"),
    discord.app_commands.Choice(name="イタリア語", value="IT"),
    discord.app_commands.Choice(name="スペイン語", value="ES"),
    discord.app_commands.Choice(name="ロシア語", value="RU"),
    discord.app_commands.Choice(name="ウクライナ語", value="UK"),
    discord.app_commands.Choice(name="ポルトガル語", value="PT-PT"),
    discord.app_commands.Choice(name="オランダ語", value="NL"),
    discord.app_commands.Choice(name="ポーランド語", value="PL"),
    discord.app_commands.Choice(name="スウェーデン語", value="SV"),
    discord.app_commands.Choice(name="フィンランド語", value="FI"),
    discord.app_commands.Choice(name="デンマーク語", value="DA"),
    discord.app_commands.Choice(name="チェコ語", value="CS"),
    discord.app_commands.Choice(name="ハンガリー語", value="HU"),
    discord.app_commands.Choice(name="ラトビア語", value="LV"),
    discord.app_commands.Choice(name="リトアニア語", value="LT"),
    discord.app_commands.Choice(name="エストニア語", value="ET"),
    discord.app_commands.Choice(name="ノルウェー語", value="NB"),
  ]
)
# コマンド本体
async def translate_command(interaction: discord.Interaction, lang:app_commands.Choice[str], sentence:str):
  await interaction.response.defer()
  lang = lang.value
  responce = requests.get(
    "https://api-free.deepl.com/v2/translate",
    params={
      "auth_key": DEEPL_API_KEY,
      "target_lang": lang,
      "text": sentence,
    },
  )
  translated = responce.json()["translations"][0]["text"]
  await interaction.followup.send(str(translated))

# 翻訳コマンドのヘルプ(使わない？)
@tree.command(name="trans_help", description="言語指定コードを表示します")
async def transhelp_command(interaction: discord.Interaction):
  await interaction.response.send_message(
    """
```
BG - Bulgarian
CS - Czech
DA - Danish
DE - German
EL - Greek
EN-GB - English (British)
EN-US - English (American)
ES - Spanish
ET - Estonian
FI - Finnish
FR - French
HU - Hungarian
ID - Indonesian
IT - Italian
JA - Japanese
KO - Korean
LT - Lithuanian
LV - Latvian
NB - Norwegian (Bokmål)
NL - Dutch
PL - Polish
PT-BR - Portuguese (Brazilian)
PT-PT - Portuguese (all Portuguese varieties excluding Brazilian Portuguese)
RO - Romanian
RU - Russian
SK - Slovak
SL - Slovenian
SV - Swedish
TR - Turkish
UK - Ukrainian
ZH - Chinese (simplified)
```
    """)

###############################################################
# デバッグ用コマンド

# bot停止(ギルドコマンド)
@tree.command(name="stop", description="debug")
@discord.app_commands.guilds(MY_SERVER_ID)
async def stop_command(interaction: discord.Interaction):
  client.clear()
  await client.close()

# コマンド同期(ギルドコマンド)(乱用厳禁)
@tree.command(name='sync', description='Owner only')
@discord.app_commands.guilds(MY_SERVER_ID)
async def sync(interaction: discord.Interaction):
    # 指定したユーザーのみ実行可能
    if interaction.user.id == OWNER_ID:
        await tree.sync()
        print('Command tree synced.')
    else:
        await interaction.response.send_message('You must be the owner to use this command!')


#自分のbotのトークン
client.run(DISCORD_TOKEN)
