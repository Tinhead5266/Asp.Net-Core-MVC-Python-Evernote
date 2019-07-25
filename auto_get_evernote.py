# -*- coding: utf-8 -*-
import logging
import datetime
from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
import os
import note_info_manager
import base64
import hashlib
import re
import time
import ftplib
import configparser
import mail_helper

logging_path = os.getcwd() + '\\logs'
logging_path = logging_path.strip().rstrip("\\")
if not os.path.exists(logging_path):
    os.makedirs(logging_path)

logging.basicConfig(level=logging.DEBUG,
                    filename='auto_update_evernote.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
"""
配置区域，请自行修改
- auth_token: 访问 https://app.yinxiang.com/api/DeveloperToken.action 生成
- diary_template_name：日记模板名称，请保证有且仅有一个标题为这个的笔记
- diary_notebook_name：复制生成的笔记要放入哪个笔记本，填写笔记本名称
"""
# 创建临时存放数据的文件夹
temp_path = os.getcwd() + '\\temp'
temp_path = temp_path.strip().rstrip("\\")
if not os.path.exists(temp_path):
    os.makedirs(temp_path)
temp_path += '\\'

note_info_manager = note_info_manager.NoteInfoManager()
# 笔记更新记录
notes_update = note_info_manager.GetAllNoteUpdateInfo()
# 所有分类
classify_data = note_info_manager.GetAllClassifyInfo()
cfg = "./config.ini"
config_raw = configparser.RawConfigParser()
config_raw.read(cfg)

note_image_http_url = config_raw.get('FTPSection', 'note_image_http_url').encode('utf-8')
notes_http_url = config_raw.get('FTPSection', 'notes_http_url').encode('utf-8')
# ftp

ftp_host = config_raw.get('FTPSection', 'host').encode('utf-8')
ftp_user_name = config_raw.get('FTPSection', 'username').encode('utf-8')
ftp_password = config_raw.get('FTPSection', 'password').encode('utf-8')
ftp = ftplib.FTP(ftp_host, ftp_user_name, ftp_password)
# 关闭被动模式
ftp.set_pasv(False)

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
info_str = '开始更新笔记: %s' % diary_title
mail_send_str = ''
logging.info(info_str)


def MakeMailSendStr(str):
    global mail_send_str
    mail_send_str += str + '\r\n'


MakeMailSendStr(info_str)
notes_count = 0
insert_count = 0
update_count = 0
insert_failed_count = 0
update_failed_count = 0


class Item:

    def __init__(self):
        pass


def FtpUpload(file_name, data):
    buf_size = 1024  # 设置缓冲器大小
    ftp.storbinary('STOR ' + file_name, data, buf_size)


def GetClassifyInfo(guid):
    if classify_data:
        for classify_item in classify_data:
            if guid == classify_item.guid:
                return classify_item
    return False


def UpdateClassifyInfo(classify_name, parent_id, guid):
    parent_classify = GetClassifyInfo(guid)
    is_classify_insert_update = False
    if not parent_classify:
        is_classify_insert_update = True
        parent_classify = Item()
        parent_classify.id = ''
        parent_classify.classify_name = classify_name
        parent_classify.parent_id = parent_id
        parent_classify.guid = guid

    if parent_classify.classify_name != classify_name:
        is_classify_insert_update = True

    if is_classify_insert_update:
        result = note_info_manager.InsertOrClassifyInfo(parent_classify.id,
                                                        parent_classify.classify_name,
                                                        parent_classify.parent_id,
                                                        parent_classify.guid)
        if not result:
            info_str = '添加或更新笔记分类失败'
            logging.info(info_str)
            MakeMailSendStr(info_str)
            exit(1)
    else:
        result = parent_classify.id
    return result


def IsInsertNote(note_guid):
    if notes_update:
        for note in notes_update:
            if note_guid == note.note_guid:
                return False

    return True


def IsUpdateNote(note_guid, note_update):
    if notes_update:
        for note in notes_update:
            if note_guid == note.note_guid and note_update > note.update_time:
                return note

    return False


def GetBlogTagGuid(tags_list):
    if tags_list:
        for tag_item in tags_list:
            if tag_item.name == 'blog':
                return tag_item.guid

    return False


def GetNoteTagNames(tags_list, note_tag_guids):
    note_tag_names = []
    if tags_list and note_tag_guids:
        for tag_item in tags_list:
            for note_tag_guid in note_tag_guids:
                if tag_item.guid == note_tag_guid:
                    note_tag_names.append(tag_item.name)
    return note_tag_names


def IsBlogNote(blog_tag_guid, note_tag_guids):
    if note_tag_guids:
        for note_tag_guid in note_tag_guids:
            if note_tag_guid == blog_tag_guid:
                return True

    return False


def ReplaceBodyHtml(html, hash_code, image_data, image_type):
    if html == "":
        return ""

    en_media_pattern = "(.*)(?P<en_media><en-media[^>]*?hash=\"%(hash)s\".*?((/>)|(></en-media>)))(.*)" % {
        'hash': hash_code}
    proc = re.compile(en_media_pattern, re.DOTALL | re.MULTILINE)
    valid_data = proc.match(html)

    if valid_data is None:
        info_str = 'valid failed'
        logging.info(info_str)
        MakeMailSendStr(info_str)
        return html

    enmedia = valid_data.group('en_media')

    # base64_image_str = base64.encodestring(image_data)
    # base64_image_str = 'data:{0};base64,{1}'.format(image_type, base64_image_str)
    # image_data = base64.b64decode(base64_image_str)
    file_name = str(int(round(time.time()) * 1000)) + '.png'
    file_path = temp_path + file_name
    image_file = open(file_path, "wb+")
    image_file.write(image_data)
    image_file.close()
    image_file = open(file_path, "rb")
    FtpUpload('./images/note_images/' + file_name, image_file)
    image_file.close()
    os.remove(file_path)

    result = enmedia.replace("en-media", "img")
    # src = "src=\"%s\"" % (base64_image_str)
    src = "src=\"%s\"" % (note_image_http_url + file_name)
    result = result.replace("<img", "<img " + src)
    return html.replace(enmedia, result)


def DoUpdate():
    global notes_count
    global insert_count
    global update_count
    global insert_failed_count
    global update_failed_count

    # 创建一个印象笔记client对象
    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china, service_host='app.yinxiang.com')

    # 用户信息
    user_store = client.get_user_store()

    # 笔记信息
    note_store = client.get_note_store()

    # 用户名称
    user_info = user_store.getUser()

    # 获取所有笔记本
    notebooks = note_store.listNotebooks()

    # 获取笔记本的所有标签
    tags_list = note_store.listTags()
    blog_tag_guid = GetBlogTagGuid(tags_list)
    notes_count = len(notebooks)

    info_str = 'Found %s notebooks' % notes_count
    logging.info(info_str)
    MakeMailSendStr(info_str)
    # 循环所有笔记本
    for notebook in notebooks:
        # 笔记本guid
        guid = notebook.guid

        # 笔记本名称（并非单个笔记的名称）
        notebook_name = notebook.name
        # 笔记本组名称
        stack = notebook.stack
        stack_guid = guid + 'f'
        classify_parent_id = UpdateClassifyInfo(stack, 0, stack_guid)
        classify_child_id = UpdateClassifyInfo(notebook_name, classify_parent_id, guid)

        info_str = 'guid: [%s], notebook [%s]' % (guid, notebook_name)
        logging.info(info_str)
        MakeMailSendStr(info_str)

        # 创建NoteFilter对象查询笔记的参数
        filter = NoteStore.NoteFilter()
        filter.notebookGuid = guid
        # 获取笔记本下的所有笔记
        notes_info = note_store.findNotes(filter, 0, 999)
        # 循环笔记本下的所有笔记
        for note in notes_info.notes:
            note_guid = note.guid
            note_update_time = note.updated
            # 是否需要添加
            is_insert = IsInsertNote(note_guid)
            update_note_info = IsUpdateNote(note_guid, note_update_time)
            update_note_info_id = update_note_info.id if update_note_info else ''

            # 需要更新的笔记
            if is_insert or update_note_info:

                # 获取笔记内容
                note_content = note_store.getNoteContent(note_guid)
                index = note_content.find('<en-note>')
                end = note_content.find('</en-note>')
                note_content = note_content[index: end] + '</en-note>'
                # 笔记名称
                note_title = note.title
                # 笔记标签guid
                note_tag_guids = note.tagGuids

                is_blog = 0 if IsBlogNote(blog_tag_guid, note_tag_guids) else 1
                note_tag_names = GetNoteTagNames(tags_list, note_tag_guids)
                note_tag_names = ','.join(note_tag_names) if note_tag_names else ''
                note_create_time = note.created
                note_update_time = note.updated

                info_str = '%s笔记: [%s]' % ('添加' if is_insert else '更新', note_title)
                logging.info(info_str)
                MakeMailSendStr(info_str)

                note_resources = note.resources
                if note_resources is not None:
                    note_resources = note_store.getNote(note_guid, False, True, False, False).resources
                    image_file_count = 0
                    for res in note_resources:
                        image_file_count += 1
                        # 资源的guid
                        res_guid = res.guid
                        # 资源类型
                        res_mime = res.mime

                        attachment_data = res.data.body
                        # 替换图片
                        if res_mime.find('image') >= 0:
                            hash_str = hashlib.md5()
                            hash_str.update(attachment_data)
                            hash_code = hash_str.hexdigest()
                            note_content = ReplaceBodyHtml(note_content, hash_code, attachment_data, res_mime)

                # 保存笔记

                file_name = note_guid + '.note'
                file_path = temp_path + file_name
                notes_file = open(file_path, "wb+")
                notes_file.write(note_content)
                notes_file.close()
                notes_file = open(file_path, "rb")
                FtpUpload('./notes/' + file_name, notes_file)
                notes_file.close()
                os.remove(file_path)

                result = note_info_manager.InsertOrUpdateNoteInfo(note_guid,
                                                                  note_title, classify_child_id,
                                                                  is_blog,
                                                                  note_tag_names, file_name,
                                                                  note_create_time,
                                                                  note_update_time, is_insert)
                info_str = '笔记[%s]%s %s' % (note_title, '添加' if is_insert else '更新', '成功' if result else '失败')
                logging.info(info_str)
                MakeMailSendStr(info_str)
                if result:
                    if is_insert:
                        insert_count += 1
                    else:
                        update_count += 1
                else:
                    if is_insert:
                        insert_failed_count += 1
                    else:
                        update_failed_count += 1


try:
    DoUpdate()
    info_str = '更新完成，笔记共[%s] %s %s %s %s' % (
        notes_count,
        ', 添加[' + insert_count + ']' if insert_count > 0 else '',
        ', 更新[' + update_count + ']' if update_count > 0 else '',
        ', 添加失败[' + insert_failed_count + ']' if insert_failed_count > 0 else '',
        ', 更新失败[' + update_failed_count + ']' if update_failed_count > 0 else '')
    logging.info(info_str)
    MakeMailSendStr(info_str)
    mail = mail_helper.MailHelper()
    ftp.quit()
except Exception as e:
    info_str = 'Exception: [%s]' % e
    logging.info(info_str)
    MakeMailSendStr(info_str)
    ftp.quit()
finally:
    mail.SendEmail(mail_send_str)
    pass
