#!/usr/bin/env python
# encoding: utf-8

'''
@author: Jiacheng Xu
@software: PyCharm
@time: 2020/2/13
'''
import pandas as pd
import pymysql
from ..configs import DB_USERNAME, DB_DATABASE, DB_PASSWORD, logger
from tqdm import tqdm

class BaseDB(object):
	def __init__(self, *args, **kwargs):
		self.__connectDB()


	def __del__(self):
		self.__disconnectDB()


	def __connectDB(self):
		''' 连接数据库'''
		self.db = pymysql.connect("localhost", DB_USERNAME, DB_PASSWORD, DB_DATABASE)


	# def bankupDB(self):
	# 	''' 备份数据库(MySQL bin文件需添加到路径中)'''
	# 	dumpcmd = "mysqldump -u" + db_username + " -p" + db_password + " " + db_database_name + " > " + db_bankup + "/" + db_database_name + ".sql"
	# 	os.system(dumpcmd)


	def __disconnectDB(self):
		''' 断开数据库'''
		self.db.close()


	def executeSQLS(self, sql):
		''' 执行SQL语句'''
		cursor = self.db.cursor()
		cursor.execute(sql)
		cursor.close()


	def dropTable(self, table_name):
		''' 数据库中删除表'''
		sql = 'DROP TABLE %s' % table_name
		self.executeSQLS(sql)


	def truncateTable(self, table_name):
		''' 清空表中数据'''
		self.executeSQLS(f"TRUNCATE TABLE {table_name}")


	def createTable(self, table_name, table_head):
		''' 创建表SQL语句'''
		self.executeSQLS(f'CREATE TABLE {table_name} ({table_head}) IF NOT EXISTS {table_name}')


	def _insertSQL(self, table_name, table_head, values):
		''' SQL插入语句'''
		return f'''INSERT IGNORE INTO {table_name} ({table_head}) VALUES ({values})'''


	def _updateSQL(self, table_name, update_info, condition):
		''' SQL更新语句 '''
		return f'''UPDATE {table_name} SET {update_info} WHERE {condition}'''


	def deleteData(self, table_name, condtion):
		''' 删除某行'''
		self.executeSQLS(f'''DELETE FROM {table_name} WHERE {condtion}''')


	def insertData(self):
		''' 数据库中插入数据'''
		pass


	def updateData(self):
		''' 数据库中更新数据'''
		pass


	def queryData(self, condition, table_name, cond=None):
		''' 数据库中查询数据'''

		## 查询的sql语句
		if cond is None:
			sql = f'SELECT {condition} FROM {table_name}'
		else:
			sql = f'SELECT {condition} FROM {table_name} WHERE {cond}'

		## 开始查询
		cursor = self.db.cursor()
		cursor.execute(sql)
		result = cursor.fetchall()
		cursor.close()
		return result


	def queryDataCondition(self, col_name, table_name, condition):
		cursor = self.db.cursor()
		cursor.execute(f'SELECT {col_name} FROM {table_name}')
		result = cursor.fetchall()
		cursor.close()
		return result



	def queryColname(self, table_name):
		''' 查询table的列字段'''
		sql = f'''SELECT column_name FROM information_schema.COLUMNS WHERE table_name LIKE '{table_name}' '''
		cursor = self.db.cursor()
		cursor.execute(sql)
		result = cursor.fetchall()
		cursor.close()
		return result


	def renameTable(self, old, new):
		''' 修改表名'''
		self.executeSQLS(f"ALTER TABLE {old} RENAME TO {new}")


	def insert_multi_record(self, dataframe, table, nn=500):
		''' 一次性插入多条数据'''
		n_insert, n_fail = 0, 0

		cursor = self.db.cursor()
		n_records = dataframe.shape[0]
		columns = ','.join([f for f in dataframe.columns])

		# ## 每次插入的记录数
		# nn = 1000 if n_records >= 100000 else 100

		## SQL插入语句
		head = f'''INSERT IGNORE INTO {table} ({columns}) VALUES '''

		## 插入失败的数据
		error = pd.DataFrame()

		## 插入数据
		pbar = tqdm(total=int(n_records / nn), desc=f'Insert data into {table}')
		for i in range(0, n_records, nn):
			tmp = dataframe.iloc[i:i + nn, :].copy()
			tail = ",".join(
				[f'''({",".join([f'"{jj}"' if jj == '' or pd.notna(jj) else "Null" for jj in tmp.iloc[ii, :]])})''' for ii in
				 range(tmp.shape[0])])
			sql = head + tail + ";"

			try:
				pbar.update(1)
				cursor.execute(sql)
				self.db.commit()
				n_insert += tmp.shape[0]
			except Exception as ept:
				logger.error(ept)
				self.db.rollback()
				n_fail += tmp.shape[0]
				error = pd.concat([error, tmp], axis=0)

		pbar.close()
		cursor.close()

		logger.info(f'.. 数据库操作结束, 共处理数据{dataframe.shape[0]}条, 成功插入{n_insert}条, 失败{n_fail}条。')

		return error