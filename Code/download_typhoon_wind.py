import requests
from bs4 import BeautifulSoup
import pandas as pd
import json 

def download(year, typhoon, path):
	headers ={
	'Host': 'rdc28.cwb.gov.tw',
	'Connection': 'keep-alive',
	'Content-Length': '1384',
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Origin': 'http://rdc28.cwb.gov.tw',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Referer': 'http://rdc28.cwb.gov.tw/TDB/ntdb/pageControl/windsearch',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2',
	'Cookie': 'PHPSESSID=2sadm2sl1rmn8akj1gavvcn8f7; TS01b0fe7f=0107dddfeffcc5fc50c21c7bfa7ec134102e299e6c0058ed8750ff423e6101edf045b7dfb73b46da30f3046cee4269420f4e85bbbbed2b530d44a2677f33741ca7ae3c1c2e'}

	payload ={
		'params_serialized':"search_type=HR&wind_type%5B%5D=WSMax&WSMax_value=0&WSMax_value_ms=0&wind_type%5B%5D=WSGust&WSGust_value=0&WSGust_value_ms=0&radio_typhoon_year=year_typhoon&typhoon_year={0}&typhoon_name={1}{2}&station_selection_type=text&measure_type=CWB&location_group=%E5%8C%97%E5%8D%80&stno%5B%5D=460010&stno%5B%5D=467060&stno%5B%5D=467080&stno%5B%5D=466990&stno%5B%5D=467540&stno%5B%5D=467610&stno%5B%5D=467620&stno%5B%5D=467660&stno%5B%5D=460020&stno%5B%5D=467530&stno%5B%5D=467480&stno%5B%5D=467490&stno%5B%5D=467770&stno%5B%5D=467550&stno%5B%5D=467650&stno%5B%5D=466850&stno%5B%5D=466880&stno%5B%5D=466900&stno%5B%5D=466910&stno%5B%5D=466920&stno%5B%5D=466921&stno%5B%5D=466930&stno%5B%5D=466940&stno%5B%5D=466950&stno%5B%5D=467050&stno%5B%5D=467570&stno%5B%5D=467571&stno%5B%5D=467110&stno%5B%5D=467300&stno%5B%5D=467350&stno%5B%5D=467990&stno%5B%5D=467410&stno%5B%5D=467411&stno%5B%5D=467420&stno%5B%5D=467780&stno%5B%5D=467440&stno%5B%5D=467590&stno%5B%5D=467790".format(year, year, typhoon)
	}

	r = requests.post('http://rdc28.cwb.gov.tw/TDB/ntdb/create_wind_datatable',data=payload, headers=headers)
	x = r.json()[u'json_content']
	df = pd.read_json(json.dumps(x))
	df.to_csv('/Users/charlie/Desktop/Taipower/data/typhoon_wind/'+path, encoding='big5',index=False)

#download('2017', 'NESAT+++++++++++', 'NESAT.csv')

download(	'2017'	,	'NESAT+++++++++++'	,	'NESAT.csv'	)
download(	'2017'	,	'HAITANG+++++++++'	,	'HAITANG.csv'	)
download(	'2016'	,	'MEGI++++++++++++'	,	'MEGI.csv'	)
download(	'2016'	,	'MERANTI+++++++++'	,	'MERANTI.csv'	)
download(	'2016'	,	'MALAKAS+++++++++'	,	'MALAKAS.csv'	)
download(	'2016'	,	'NEPARTAK++++++++'	,	'NEPARTAK.csv'	)
download(	'2015'	,	'SOUDELOR++++++++'	,	'SOUDELOR.csv'	)
download(	'2015'	,	'CHAN-HOM++++++++' 	,	'CHAN-HOM.csv'	)
download(	'2015'	,	'DUJUAN++++++++++'	,	'DUJUAN.csv'	)
download(	'2014'	,	'MATMO+++++++++++'	,	'MATMO.csv'	)
download(	'2014'	,	'FUNG-WONG+++++++'	,	'FUNG-WONG.csv'	)
download(	'2014'	,	'HAGIBIS+++++++++'	,	'HAGIBIS.csv'	)






