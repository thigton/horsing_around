import pymysql
import pandas as pd
import sqlalchemy

# superseded mysql method
#engine = sqlalchemy.create_engine("mysql+mysqldb://Ed:EdTheHorse@146.148.124.146/horse_test")
#pd.read_sql('select * from horses',engine)

engine = sqlalchemy.create_engine("mysql+pymysql://Ed:EdTheHorse@146.148.124.146/horse_test")
df_out = pd.read_sql('select * from horses',engine)
df = pd.DataFrame(columns = ['horse_id', 'horse_age'])
df.loc[0] = ['steve',8]
df.to_sql('horses',con=engine,if_exists='append',index=False)
pd.read_sql('select * from horses',engine)

