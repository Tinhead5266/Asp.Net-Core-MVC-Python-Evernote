'''
@Author: your name
@Date: 2019-07-25 13:53:49
@LastEditTime: 2020-03-29 20:03:01
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: \asp.net core mvc python evernote\mysql_helper.py
'''
# -*- coding: utf-8 -*-
import pymysql
import configparser
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='auto_update_evernote.log',
    format=
    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class MySqlHelper:
    def __init__(self):
        test_cfg = "./config.ini"
        config_raw = configparser.RawConfigParser()
        config_raw.read(test_cfg, encoding='utf-8')

        self.host = config_raw.get('MySqlSection', 'host')
        self.user = config_raw.get('MySqlSection', 'user')
        self.port = config_raw.getint('MySqlSection', 'port')
        self.pwd = config_raw.get('MySqlSection', 'password')
        self.db = config_raw.get('MySqlSection', 'db')
        self.charset = config_raw.get('MySqlSection',
                                      'charset')
        self._conn = self.GetConnect()
        if self._conn:
            self._cur = self._conn.cursor()
            self.is_connected = True
        else:
            self.is_connected = False

    def GetConnect(self):
        conn = False
        try:
            conn = pymysql.connect(host=self.host,
                                   port=self.port,
                                   user=self.user,
                                   password=self.pwd,
                                   database=self.db,
                                   charset=self.charset)
            # conn = pymysql.connect(self.host, self.user, self.pwd, self.db, self.port)
        except Exception as err:
            logging.info('Connection Failed, [%s]' % err)
        else:
            return conn

    def ExecQuery(self, sql):
        res = ""
        try:
            self._cur.execute(sql)
            res = self._cur.fetchall()
        except Exception as err:
            logging.info("ExecQuery Failed, [%s] sql:[%s]" % err, sql)
        else:
            return res

    def ExecNonQuery(self, sql, args, get_insert_id=False):
        flag = False
        try:
            self._cur.execute(sql, args)
            flag = self._conn.insert_id() if get_insert_id else True
            self._conn.commit()
        except Exception as err:
            flag = False
            self._conn.rollback()
            logging.info("ExecNonQuery Failed, [%s] sql:[%s]" % err, sql)
        else:
            return flag

    def GetConnectInfo(self):
        logging.info("ConnectionInfo:")
        logging.info("Host:[%s] , UserName:[%s] , DB:[%s] " %
                     (self.host, self.user, self.db))

    def Close(self):
        if (self._conn):
            try:
                if (type(self._cur) == 'object'):
                    self._cur.close()
                if (type(self._conn) == 'object'):
                    self._conn.close()
            except Exception as err:
                raise ("Close Failed, [%s],[%s],err : [%s]" %
                       (type(self._cur), type(self._conn), err))

    def FormatSqlStr(self, sql, args):
        new_args = []
        if args:
            for arg in args:
                if isinstance(arg, str):
                    new_args.append(pymysql.escape_string(arg))
                else:
                    new_args.append(arg)
        if new_args:
            sql = sql.format(new_args)
        return sql
