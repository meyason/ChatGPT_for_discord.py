import discord
from discord import app_commands
from dotenv import load_dotenv
load_dotenv()
import openai
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
OWNER_ID = os.getenv("OWNER_ID")
MY_SERVER_ID = os.getenv("MY_SERVER_ID")
openai.api_key = os.environ[OPENAI_API_KEY]
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

# インスタンス生成
cgo = chatgptorg(OPENAI_API_KEY)

# GPT-4コマンド(API解放待ち)
@tree.command(name="gpt", description="GPT-4で文章を生成します")
async def gpt(interaction: discord.Interaction, text: str):
  # await interaction.response.defer()
  # response = openai.ChatCompletion.create(
  #     model = "gpt-4",
  #     messages=[
  #         {"role": "system", "content": "あなたは優秀なアシスタントです．"},
  #         {"role": "user", "content": text},
  #     ]
  # )
  # await interaction.followup.send(response["choices"][0]["message"]["content"])
  await interaction.response.send_message('api待ちです，ごめんね！')

# メンション呼び出し・メモリ付き
@client.event
async def on_message(message):
    if client.user in message.mentions:
        server = message.guild.id
        response = cgo.output(server, message.content)
        print(response)
        await message.channel.send(response)

# メモリ削除
@tree.command(name="talkreset", description="会話履歴を削除")
async def langchainstop_command(interaction: discord.Interaction):
  await interaction.response.defer()
  cgo.reset_history(interaction.guild.id)
  await interaction.followup.send("リセットしました。")

###############################################################

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
