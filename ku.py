# 导入:

from sqlalchemy import Column, String, create_engine, Integer, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
# 创建对象的基类:
Base = declarative_base()


class Songs(Base):
    # 表的名字:
    __tablename__ = 'songs'

    # 表的结构:
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(64))
    filehash = Column(String(512), index=True)
    fingerprinted = Column(Boolean, default=False)
    fingerprints = relationship('Fingerprints', backref='song',
                                primaryjoin='Songs.id == Fingerprints.song_id', foreign_keys='Fingerprints.song_id')


class Fingerprints(Base):
    __tablename__ = 'fingerprints'

    id = Column(Integer, autoincrement=True, primary_key=True)
    song_id = Column(Integer)
    fingerprint = Column(String(64), index=True)
    offset = Column(Integer)

# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/user')
print(engine)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
session = DBSession()
# song=Songs(1,'','','')
# session.add(song)
# session.commit()
# sql = 'select name from songs where id==4'
re=session.query(Songs).filter(Songs.id=="4").first()
print(re)
session.close()

