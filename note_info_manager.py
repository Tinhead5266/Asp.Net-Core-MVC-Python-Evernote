# -*- coding: utf-8 -*-
import mysql_helper
import logging

logging.basicConfig(level=logging.DEBUG,
                    filename='auto_update_evernote.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class NoteInfoManager:
    def __init__(self):
        self.sql_helper = mysql_helper.MySqlHelper()
        if not self.sql_helper.is_connected:
            logging.info('数据库连接失败')
            exit(1)

    # 填充笔记更新记录
    def FullNoteUpdateInfo(self, data_db):
        data = []
        if data_db:
            for item_db in data_db:
                item = Item()
                item.id = item_db[0]
                item.update_time = int(item_db[1] if item_db[1] else 0)
                item.note_guid = (item_db[2] if item_db[2] else '').encode('utf-8')
                data.append(
                    item
                )
        return data

    # 填充笔记分类记录
    def FullClassifyInfo(self, data_db):
        data = []
        if data_db:
            for item_db in data_db:
                item = Item()
                item.id = item_db[0]
                item.classify_name = (item_db[1] if item_db[1] else '').encode('utf-8')
                item.parent_id = int(item_db[2] if item_db[2] else 0)
                item.guid = (item_db[3] if item_db[3] else '').encode('utf-8')
                data.append(
                    item
                )
        return data

    # 根据编号获取笔记更新记录
    def GetNoteUpdateInfoById(self, id):
        note_update_info_data = self.sql_helper.ExecQuery(
            "SELECT * FROM evernote_blog.note_update_info where id = %s;" % (
                id))
        note_update_info = self.FullNoteUpdateInfo(note_update_info_data)
        return note_update_info[0] if note_update_info else False

    # 获取所有笔记更新记录
    def GetAllNoteUpdateInfo(self):
        data = self.sql_helper.ExecQuery('SELECT id,update_time,note_guid FROM evernote_blog.note_info;')
        all_note_update_info = self.FullNoteUpdateInfo(data)
        return all_note_update_info

    # 添加修改笔记更新记录
    def InsertOrUpdateNoteUpdateInfo(self, id, note_guid, update_time):
        # 修改
        sql_str = ''
        if id:
            args = (note_guid, update_time, id)
            sql_str = "UPDATE `evernote_blog`.`note_update_info` SET `note_guid` = %s, `update_time` = %s WHERE (`id` = %s);"
            result = self.sql_helper.ExecNonQuery(sql_str, args)
            # not_update_info = self.GetNoteUpdateInfoById(note_id)
            if not result:
                logging.info('修改笔记更新记录失败：没有找到【note_id】为【%s】笔记，【note_guid】:%s,【sql_str】:%s',
                             (id, note_guid, sql_str))
                return False

        # 添加
        else:
            args = (note_guid, update_time)
            sql_str = "INSERT INTO `evernote_blog`.`note_update_info` (`note_guid`, `update_time`) VALUES (%s, %s);"
            result = self.sql_helper.ExecNonQuery(sql_str, args)
            if not result:
                logging.info('添加笔记更新记录失败：【note_guid】:%s,【sql_str】:%s', (note_guid, sql_str))
                return False

        return True

    # 添加修改笔记信息
    def InsertOrUpdateNoteInfo(self, note_guid, title, classify_id, is_blog, tags, content, snippet, create_time,
                               update_time, is_insert=False):
        # 修改
        sql_str = ''
        if not is_insert:
            args = (title, classify_id, is_blog, tags, content, snippet, create_time, update_time, note_guid)
            sql_str = "UPDATE `evernote_blog`.`note_info` SET `title` = %s, `classify_id` =  %s, `is_blog` =  %s, `tags` =  %s, `content` =  %s,`content_snippet` =  %s, `create_time` =  %s, `update_time` =  %s WHERE (`note_guid` =  %s);"
            result = self.sql_helper.ExecNonQuery(sql_str, args)

            if not result:
                logging.info('修改笔记失败：参数:%s,【sql_str】:%s', (args, sql_str))
                return False

        # 添加
        else:
            args = (title, classify_id, is_blog, tags, content, snippet, create_time, update_time, note_guid)
            sql_str = "INSERT INTO `evernote_blog`.`note_info` (`title`, `classify_id`, `is_blog`, `tags`, `content`,`content_snippet`, `create_time`, `update_time`, `note_guid`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            # sql_str = self.sql_helper.FormatSqlStr(sql_str, args)

            result = self.sql_helper.ExecNonQuery(sql_str, args)
            if not result:
                logging.info('添加笔记失败：参数:%s,【sql_str】:%s', (args, sql_str))
                return False

        return True

    # 查询所有笔记分类信息
    def GetAllClassifyInfo(self):
        data = self.sql_helper.ExecQuery('SELECT * FROM evernote_blog.classify_info;')
        classify_info = self.FullClassifyInfo(data)
        return classify_info

    # 添加修改笔记分类信息
    def InsertOrClassifyInfo(self, id, classify_name, parent_id, guid):
        # 修改
        sql_str = ''
        if id:
            args = (classify_name, parent_id, guid, id)
            sql_str = "UPDATE `evernote_blog`.`classify_info` SET `classify_name` = %s, `parent_id` = %s, `guid` = %s WHERE (`id` = %s);"
            result = self.sql_helper.ExecNonQuery(sql_str, args)
            if not result:
                logging.info('修改笔记分类信息失败：参数:%s,【sql_str】:%s', (args, sql_str))
                return False
            result = id

        # 添加
        else:
            args = (classify_name, parent_id, guid)
            sql_str = "INSERT INTO `evernote_blog`.`classify_info` (`classify_name`, `parent_id`, `guid`) VALUES (%s,%s,%s);"
            result = self.sql_helper.ExecNonQuery(sql_str, args, True)
            if not result:
                logging.info('添加笔记分类信息失败：参数:%s,【sql_str】:%s', (args, sql_str))
                return False

        return result


class Item:

    def __init__(self):
        pass
