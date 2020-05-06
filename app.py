# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import datetime
import errno
import json
import os
import sys
import tempfile
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import mechanize
import random as rd
from dotenv import load_dotenv
import drive
import io
import magic
load_dotenv()

# use creds to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("link").sheet1
sheetMessage = client.open("link").worksheet("message")
sheetList = client.open("link").worksheet("list")
sheetKelasc = client.open("link").worksheet("kelasc")
sheetAdmin = client.open("link").worksheet("dataAdmin")
botSetting = client.open("link").worksheet("botSetting")

# Server Setting
mirrorStatus = True

from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory, render_template
import flask
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage,VideoSendMessage)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("CHANNEL_SECRET")
channel_access_token = os.getenv("CHANNEL_ACCESS_SECRET")
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def checkAdmin(dataUser):
    dataAdmin = sheetAdmin.col_values(2)
    if dataUser in dataAdmin:
        return True
    else:
      return False
        
# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/")
def hello():
    return render_template("index.html")


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='User ID: ' + event.source.user_id),
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == 'hai' or text == 'Hai':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [TextSendMessage(text='Hai, ' + profile.display_name)]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=os.getenv("KUNCI")))
 
#===============Group Stuff==============================================================================
    elif text == "rin" or text == "Rin":
        bubble_string = """
        {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "Daftar Command",
                "weight": "bold",
                "color": "#1DB446",
                "size": "sm"
              },
              {
                "type": "separator",
                "margin": "xxl"
              },
              {
                "type": "box",
                "layout": "vertical",
                "margin": "xl",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "daftar list",
                        "size": "sm",
                        "color": "#1DB446",
                        "flex": 0
                      },
                      {
                        "type": "text",
                        "text": "Untuk daftar list",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                      }
                    ]
                  },
                  {
                    "type": "separator",
                    "margin": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "list done",
                        "size": "sm",
                        "color": "#1DB446",
                        "flex": 0
                      },
                      {
                        "type": "text",
                        "text": "Buat yang udah beres list",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                      }
                    ],
                    "margin": "xl"
                  },
                  {
                    "type": "separator",
                    "margin": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "8ball (tulisan)",
                        "size": "sm",
                        "flex": 0,
                        "color": "#1DB446"
                      },
                      {
                        "type": "text",
                        "text": "Diramal oleh 8ball :v",
                        "size": "sm",
                        "align": "end"
                      }
                    ],
                    "margin": "xl"
                  },
                  {
                    "type": "separator",
                    "margin": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "xl",
                    "contents": [
                      {
                        "type": "text",
                        "text": "random kelompok (angka)",
                        "size": "sm",
                        "color": "#1DB446",
                        "wrap": true
                      },
                      {
                        "type": "text",
                        "text": "Buat ngerandom sesuai angkanya",
                        "size": "sm",
                        "wrap": true,
                        "align": "end"
                      }
                    ]
                  },
                  {
                    "type": "separator",
                    "margin": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "r!d (link file google drive)",
                        "size": "sm",
                        "color": "#1DB446",
                        "wrap": true
                      }
                    ],
                    "margin": "xl"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": "Buat mengatasi limit download google drive",
                        "size": "sm",
                        "color": "#555555",
                        "wrap": true
                      }
                    ]
                  }
                ]
              },
              {
                "type": "separator",
                "margin": "xl"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [
                  {
                    "type": "text",
                    "text": "「Rin",
                    "size": "xs",
                    "color": "#aaaaaa",
                    "flex": 0
                  },
                  {
                    "type": "text",
                    "text": "dirgabrajamusti.xyz",
                    "color": "#aaaaaa",
                    "size": "xs",
                    "align": "end"
                  }
                ]
              }
            ]
          },
          "styles": {
            "footer": {
              "separator": true
            }
          }
        }
        """
        message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble_string))
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == "daftar list" or text == "Daftar list":
      group_id = event.source.group_id
      profile = line_bot_api.get_group_member_profile(group_id, event.source.user_id)
      try:
          cariData = sheetList.find(profile.display_name)
          listData = sheetList.col_values(2)
          listNama = ""
          i = 1
          for x in listData:
              listNama = listNama + str(i) + ". " + x + "\n"
              i += 1
          line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text="Namamu sudah ada di list"),
            TextSendMessage(text="Daftar list: " + "\n" + listNama)
          ])
      except gspread.exceptions.CellNotFound:  # or except gspread.CellNotFound:
          userId = event.source.user_id
          jumlahCol = len(sheetList.col_values(1)) + 1
          dataInput = [jumlahCol, profile.display_name]
          sheetList.insert_row(dataInput, jumlahCol)
          #Cek data
          listData = sheetList.col_values(2)
          listNama = ""
          i = 1
          for x in listData:
              listNama = listNama + str(i) + ". " + x + "\n"
              i += 1
          line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text="List ditambahkan: " + profile.display_name),
            TextSendMessage(text="Daftar list: " + "\n" + listNama)])
    elif text == "list done" or text == "List done":
      group_id = event.source.group_id
      profile = line_bot_api.get_group_member_profile(group_id, event.source.user_id)
      try:
          cariData = sheetList.find(profile.display_name)
          sheetList.update_cell(cariData.row , cariData.col, profile.display_name + " (Done)")
          listData = sheetList.col_values(2)
          listNama = ""
          i = 1
          for x in listData:
            listNama = listNama + str(i) + ". " + x + "\n"
            i += 1
          line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text="Namamu sudah ada beres"),
            TextSendMessage(text="Daftar list:" + "\n" + listNama)])
      except gspread.exceptions.CellNotFound:  # or except gspread.CellNotFound:
          line_bot_api.reply_message(event.reply_token,[TextSendMessage(text="Langsung ketik cek list ya")])
    elif text == "cek list":
      listData = sheetList.col_values(2)
      listNama = ""
      i = 1
      for x in listData:
        listNama = listNama + str(i) + ". " + x + "\n"
        i += 1
      line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text="Daftar list: " + "\n" + listNama)
          ])
    elif "random kelompok" in text or "Random kelompok" in text:
      participants = sheetKelasc.col_values(2)
      members = int(text[16:])
      rd.shuffle(participants)
      kelompok = ""
      anggota = ""
      for i in range(len(participants) // members + 1):
          kelompok = kelompok + 'Kelompok {} Anggotanya: '.format(i + 1) + "\n"
          group = participants[i*members:i*members + members]
          for participant in group:
              kelompok = kelompok + "- " + participant + "\n"
      line_bot_api.reply_message(event.reply_token, TextSendMessage(text=kelompok))
      
#===============Admin group stuff==============================================================================
    elif text == "clear list":
      if checkAdmin(event.source.user_id):
        jumlahCol = sheetList.col_values(1)
        i = 1
        for x in jumlahCol:
            sheetList.update_cell(i, 1, '')
            sheetList.update_cell(i, 2, '')
            i += 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Data list telah dihapus"))
      else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Anda belum punya akses :p"))
    elif text == "get group id":
      if checkAdmin(event.source.user_id):
        id = event.source.group_id
        to = event.source.user_id
        line_bot_api.push_message(to, TextSendMessage(text='Group id: '+ id))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Group id telah dikirim"))
    elif text == "send to group":
      if checkAdmin(event.source.user_id):
        groupId = "C9ba4ae8b18cfc95f014c1c10f22ed8cf"
        line_bot_api.push_message(groupId, TextSendMessage(text="Test Message"))

        
        
#===============Games==============================================================================
    elif "8ball" in text.lower():
      responses = ["As I see it, yes.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don’t count on it.","It is certain.","It is decidedly so.","Most likely.","My reply is no.","My sources say no.","Outlook not so good.","Outlook good.","Reply hazy, try again.","Signs point to yes.","Very doubtful.","Without a doubt.","Yes.","Yes – definitely.","You may rely on it."]
      random = np.random.randint(0, 19)
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text=responses[random]))

      
#===============Personal Stuff==============================================================================
    elif "r!sl" in text or "R!sl" in text:
      if checkAdmin(event.source.user_id):
        try:
          br = mechanize.Browser()
          br.set_handle_robots(False)
          br.open(text[5:])
          userId = event.source.user_id
          jumlahCol = len(sheet.col_values(1)) + 1
          dataAbout = br.title()
          dataInput = [jumlahCol - 1, userId, text[5:], dataAbout]
          sheet.insert_row(dataInput, jumlahCol)
          line_bot_api.reply_message(event.reply_token, [
                        TextSendMessage(text='Link Disimpan: ' + text[5:]),
                        TextSendMessage(text='Pada Google Drive kolom ke: ' + str(jumlahCol)),
                        TextSendMessage(text='Website: ' + dataAbout)
                    ])
        except:
          userId = event.source.user_id
          jumlahCol = len(sheet.col_values(1)) + 1
          dataAbout = "Can't get website title"
          dataInput = [jumlahCol - 1, userId, text, dataAbout]
          sheet.insert_row(dataInput, jumlahCol)
          line_bot_api.reply_message(event.reply_token, [
                        TextSendMessage(text='Link Disimpan: ' + text),
                        TextSendMessage(text='Pada Google Drive kolom ke: ' + str(jumlahCol)),
                        TextSendMessage(text='Website: ' + dataAbout)
                    ])

    elif text == "r!cl" or text == "R!cl":
      userId = event.source.user_id
      hasil = ""
      for k in range(len(sheet.col_values(1))):
        row=sheet.row_values(k+1)
        if row[1] == userId:
            hasil = hasil + row[2] + " | " + row[3] + "\n"
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text="Daftar Link: " + hasil))
    
    elif "r!m" in text: 
      userId = event.source.user_id
      jumlahCol = len(sheetMessage.col_values(1)) + 1
      dataInput = [jumlahCol - 1, userId, text[4:]]
      sheetMessage.insert_row(dataInput, jumlahCol)
      line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Message Disimpan: ' + text[4:]))
      
    elif text == "r!cm" or text == "Cm":
      userId = event.source.user_id
      hasil = ""
      for k in range(len(sheetMessage.col_values(1))):
          row=sheetMessage.row_values(k+1)
          if row[1] == userId:
              hasil = hasil + row[2] + "\n"  
      line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Daftar Message: " + "\n" + hasil))
      
    elif "r!d" in text or "R!d" in text:
      id = text[4:]
      fileId = drive.extract_files_id(id)
      try:
        shareLink = drive.copyFileDriveGetLink(fileId[0])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="File telah di copy: " + shareLink))
      except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fileId))
  


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
  if checkAdmin(event.source.user_id) == True:
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        mimetype = "image/jpeg"
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
        mimetype = "video/mp4"
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
        mimetype = "audio/mp4"
    else:
        return
      
    message_content = line_bot_api.get_message_content(event.message.id)
    file = io.BytesIO()
    file.writelines(message_content.iter_content())
    fileName = event.message.id + '.' +ext
    upload = drive.uploadFile(fileName,file,mimetype)
    
    line_bot_api.reply_message(
        event.reply_token, [TextSendMessage(text="Link Mirror: " + upload)])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    if mirrorStatus:
      message_content = line_bot_api.get_message_content(event.message.id)
      with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
          for chunk in message_content.iter_content():
              tf.write(chunk)
          tempfile_path = tf.name

      message_content = line_bot_api.get_message_content(event.message.id)
      file = io.BytesIO()
      file.writelines(message_content.iter_content())
      fileName = event.message.file_name
      mimetype = magic.from_buffer(file.getvalue(), mime=True)
      upload = drive.uploadFile(fileName,file,mimetype)

      line_bot_api.reply_message(
          event.reply_token, [
              TextSendMessage(text='Link Mirror: ' + upload)
          ])


@handler.add(FollowEvent)
def handle_follow(event):
    app.logger.info("Got Follow event:" + event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    app.logger.info("Got Unfollow event:" + event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))


@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got memberJoined event. event={}'.format(
                event)))


@handler.add(MemberLeftEvent)
def handle_member_left(event):
    app.logger.info("Got memberLeft event")


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)
    