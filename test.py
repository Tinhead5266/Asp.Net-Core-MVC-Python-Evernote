# -*- coding: utf-8 -*-
"""
搜索并复制指定的印象笔记模板，到指定的文件夹。
"""
import logging
import datetime
import time
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
import os

logging.basicConfig(level=logging.DEBUG,
                    filename='auto_update_evernote.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
"""
配置区域，请自行修改
- auth_token: 访问 https://app.yinxiang.com/api/DeveloperToken.action 生成
- diary_template_name：日记模板名称，请保证有且仅有一个标题为这个的笔记
- diary_notebook_name：复制生成的笔记要放入哪个笔记本，填写笔记本名称
"""
# auth_token = "your token here"
diary_template_name = '日记模板'
diary_notebook_name = 'XMind'

note_images_path = os.getcwd() + '\\note_images'
note_images_path = note_images_path.strip().rstrip("\\")
if not os.path.exists(note_images_path):
    os.makedirs(note_images_path)

# auth_token申请地址：https://dev.yinxiang.com/doc/articles/dev_tokens.php
auth_token = "S=s64:U=133f619:E=16c299788b0:C=16c058b02a0:P=1cd:A=en-devtoken:V=2:H=9d33d7358ebebc826206c2ae2da274e6"

# 关掉沙盒模式
sandbox = False
# True代表使用的国内的印象笔记，而不是Evernote国际版
china = True

# 日记标题。个人习惯用形如 『20170325（周六）』这样的标题，可以根据自己的需求修改。
weekday_chinese_map = {
    0: '周一',
    1: '周二',
    2: '周三',
    3: '周四',
    4: '周五',
    5: '周六',
    6: '周日',
}
now = datetime.datetime.now()
diary_title = '%s（%s）' % (now.strftime('%Y%m%d'),
                          weekday_chinese_map[now.weekday()])
logging.info('diary_title: %s', diary_title)

# 创建一个印象笔记client对象
client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china, service_host='app.yinxiang.com')
# client = EvernoteClient(token=auth_token, service_host='app.yinxiang.com')
# 用户信息
user_store = client.get_user_store()
# 笔记信息
note_store = client.get_note_store()
# 用户名称
user_info = user_store.getUser()

# 定位日记所在笔记本 guid
notebooks = note_store.listNotebooks()

listTags = note_store.listTags()

logging.info('Found %s notebooks', len(notebooks))
# 循环所有笔记本
for notebook in notebooks:
    # 笔记本guid
    guid = notebook.guid
    # 笔记本名称（并非单个笔记的名称）
    notebook_name = notebook.name
    # 笔记本组名称
    stack = notebook.stack
    logging.info('guid: [%s], notebook [%s]', guid, notebook_name)
    # 笔记名称不是XMind的跳过
    if notebook_name != diary_notebook_name:
        continue
    # 创建NoteFilter对象查询笔记的参数
    f = NoteStore.NoteFilter()
    f.notebookGuid = guid
    # 获取笔记本的所有标签
    tags_list = note_store.listTagsByNotebook(notebook.guid)
    # 获取笔记本下的所有笔记
    notes_info = note_store.findNotes(f, 0, 999)
    # 循环笔记本下的所有笔记
    for note in notes_info.notes:
        # 获取笔记内容
        note_content = note_store.getNoteContent(note.guid)
        # 笔记名称
        note_title = note.title
        # 笔记标签
        not_tag_names = note.tagNames

        logging.info('guid: [%s], notebook [%s],notebookName [%s]', guid, notebook_name, note_title)
        logging.info('content: [%s]', note_content)
        # 获取笔记数据资源信息（图片、语言、文件等）
        note_resources = note.resources
        try:
            if note_resources is not None:
                image_file_count = 0
                for res in note_resources:
                    image_file_count += 1
                    # 资源的guid
                    res_guid = res.guid
                    # 资源类型
                    res_mime = res.mime

                    logging.info(
                        'note_resources_guid: [%s], note_resources_width [%s], note_resources_height [%s], note_resources_type [%s]',
                        res_guid, res.width, res.height, res_mime)
                    # 获取资源
                    attachment = note_store.getResource(res_guid, True, False, True, False)
                    # attachments = note_store.getResourceRecognition(res.guid)
                    attachment_data = attachment.data.body
                    #
                    # base64_image_str = base64.encodestring(attachment_data)
                    # # base64_image_str = 'data:{0};base64,{1}'.format(res_mime, base64_image_str)
                    # image_data = base64.b64decode(base64_image_str)
                    if res_mime.find('image') >= 0:
                        file_name = note_images_path + '\\' + str(int(round(time.time()) * 1000)) + '.png'
                        image_file = open(file_name, "wb+")
                        image_file.write(attachment_data)
                        image_file.close()

        except Exception as e:
            logging.info('Exception: [%s]', e)
        finally:
            pass
    #
    # if notebook_name == diary_notebook_name:
    #     logging.info('found diary notebook! guid: [%s], notebook [%s]',
    #                  guid, notebook_name)
    #     diary_notebook_guid = guid
    # break
    # else:
    #     logging.critical('diary [%s] not found', diary_notebook_name)
    #     exit(1)

# 定位日记模板 guid
noteFilter = NoteStore.NoteFilter(words=diary_template_name)
spec = NoteStore.NotesMetadataResultSpec()

nmdList = note_store.findNotesMetadata(noteFilter, 0, 250, spec)
logging.debug('nmdList: %s', nmdList)
for n in nmdList.notes:
    note = note_store.getNote(n.guid, True, True, False, False)
    logging.debug('guid: [%s], title: [%s]', note.guid, note.title)
    if note.title == diary_template_name:
        logging.info('found diary template note! guid: [%s], title: [%s]',
                     note.guid, note.title)
        diary_template_guid = note.guid
        break
else:
    logging.critical('diary_template [%s] not found', diary_template_name)
    exit(1)

# 复制模板，生成笔记，修改标题
res_note = note_store.copyNote(diary_template_guid, diary_notebook_guid)
res_note.title = diary_title
res_note = note_store.updateNote(res_note)
logging.info('create diary for %s done!', now)
