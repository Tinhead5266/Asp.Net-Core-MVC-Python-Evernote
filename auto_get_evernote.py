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
# 创建存放图片的文件夹
note_images_path = os.getcwd() + '\\note_images'
note_images_path = note_images_path.strip().rstrip("\\")
if not os.path.exists(note_images_path):
    os.makedirs(note_images_path)

note_info_manager = note_info_manager.NoteInfoManager()
# 笔记更新记录
notes_update = note_info_manager.GetAllNoteUpdateInfo()
# 所有分类
classify_data = note_info_manager.GetAllClassifyInfo()
test_cfg = "./config.ini"
config_raw = configparser.RawConfigParser()
config_raw.read(test_cfg)

note_image_http_url = config_raw.get('FTPSection', 'note_image_http_url').encode('utf-8')
# ftp

ftp_host = config_raw.get('FTPSection', 'host').encode('utf-8')
ftp_user_name = config_raw.get('FTPSection', 'username').encode('utf-8')
ftp_password = config_raw.get('FTPSection', 'password').encode('utf-8')
ftp = ftplib.FTP(ftp_host, ftp_user_name, ftp_password)
# ftp.login(ftp_user_name, ftp_password)
ftp.set_pasv(False)
# sdf = ftp.getwelcome()
# sdfs = ftp.dir()

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
logging.info('开始更新笔记: %s', diary_title)


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
            logging.info('添加或更新笔记分类失败')
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
        logging.info("valid failed")
        return html

    enmedia = valid_data.group('en_media')

    # base64_image_str = base64.encodestring(image_data)
    # base64_image_str = 'data:{0};base64,{1}'.format(image_type, base64_image_str)
    # image_data = base64.b64decode(base64_image_str)
    file_name = str(int(round(time.time()) * 1000)) + '.png'
    file_path = note_images_path + file_name
    image_file = open(file_path, "wb+")
    image_file.write(image_data)
    image_file.close()
    image_file = open(file_path, "rb")
    FtpUpload(file_name, image_file)
    image_file.close()
    os.remove(file_path)

    result = enmedia.replace("en-media", "img")
    # src = "src=\"%s\"" % (base64_image_str)
    src = "src=\"%s\"" % note_image_http_url + file_name
    result = result.replace("<img", "<img " + src)
    return html.replace(enmedia, result)


def DoUpdate():
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

    logging.info('Found %s notebooks', len(notebooks))
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

        logging.info('guid: [%s], notebook [%s]', guid, notebook_name)

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

                logging.info('%s笔记: [%s]', '添加' if is_insert else '更新', note_title)
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

                        # 获取资源
                        # attachment = note_store.getResource(res_guid, True, False, True, False)
                        attachment_data = res.data.body
                        # 替换图片
                        if res_mime.find('image') >= 0:
                            hash_str = hashlib.md5()
                            hash_str.update(attachment_data)
                            hash_code = hash_str.hexdigest()
                            note_content = ReplaceBodyHtml(note_content, hash_code, attachment_data, res_mime)

                        # 保存图片
                        # if res_mime.find('image') >= 0:
                        #     file_name = note_images_path + '\\' + str(int(round(time.time()) * 1000)) + '.png'
                        #     image_file = open(file_name, "wb+")
                        #     image_file.write(attachment_data)
                        #     image_file.close()

                # 保存笔记

                result = note_info_manager.InsertOrUpdateNoteInfo(note_guid,
                                                                  note_title, classify_child_id,
                                                                  is_blog,
                                                                  note_tag_names, note_content,
                                                                  note_create_time,
                                                                  note_update_time, is_insert)

                if result:
                    # 保存笔记更新信息
                    result = note_info_manager.InsertOrUpdateNoteUpdateInfo(update_note_info_id,
                                                                            note_guid,
                                                                            note_update_time)
                logging.info('笔记[%s]%s %s', note_title, '添加' if is_insert else '更新', '成功' if result else '失败')


try:
    DoUpdate()
except Exception as e:
    logging.info('Exception: [%s]', e)
finally:
    ftp.quit()
