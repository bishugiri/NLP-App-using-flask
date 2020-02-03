from flask import Flask, render_template, url_for, request
from werkzeug import secure_filename
import os
import re
import string
import statistics
import pandas as pd
app = Flask(__name__)


app.config['SECRET_KEY'] = 'b19197b2a381de384d1074e1'

@app.route('/')
def hello():
    return render_template('ocr_home.html')
	
@app.route('/nlp')
def home():
    return render_template('nlp_home.html')

#### NLP functions ###############################################

def feature(text, key, min_, max_, case_):

	try:

		tokens = text.split()
		tokens_lower = [i.lower() for i in tokens]
		keylist = key.lower().split('or')
		keylist = [i.strip() for i in keylist]
		filter_key = [i for i in tokens_lower if i in keylist]
		ix = tokens_lower.index(filter_key[0])
		st = ix+int(min_)
		en = ix+int(max_)
		out = tokens[st:en]
		if case_== 'lower':
			out = [i for i in out if i.islower()]
		elif case_== 'upper':
			out = [i for i in out if i.isupper()]
		elif case_== 'proper':
			out = [i for i in out if i.istitle()]
		else:
			out = out

		if len(out)>0:
			return ' '.join(out)
		else:
			return None
	except:
		return None



def output_format (df, path, keywd):

		df.reset_index(inplace = True)
		del df['index']
		df.to_csv(path+'/Output/df.csv')
		missing_percentage = int((df[keywd].isnull().sum())*100/df.shape[0])
		return render_template('nlp_result.html', summary = [df[[keywd]].describe().to_html(classes='data')], 
			tables = [df.head().to_html(classes ='data')], titles = df.columns.values, missing = missing_percentage)


def regex_output(text, regx):

	if request.method == 'POST':
		search_list = re.findall(regx, text)
		
		if len(search_list)>0:

			return search_list

		else:
			return None


def remove_punctuation(text,punc_list):
    punc_table = str.maketrans(dict.fromkeys(punc_list))
    return text.translate(punc_table)


@app.route('/result', methods = ['POST'])
def main_func():

	if request.method == 'POST':

		path = request.form['path']
		ext_ = request.form['extraction']
		keywd = request.form['keyword']
		punc_list = request.form['punctuations']
		

		file_list = os.listdir(path+'/Input')
		df = pd.DataFrame()
		for i in file_list:


			with open(path+"/Input/"+i) as f:

				txt = f.read()
				txt = remove_punctuation(txt,punc_list)

				if ext_ == "keyword":

					cs = request.form['case']
					min_ = request.form['min']
					max_ = request.form['max']
					tempdf = pd.DataFrame({'claimno':[i], 'text':[txt], keywd:[feature(txt,keywd,min_,max_, cs)]})
					df = pd.concat([df, tempdf], axis = 0)
		

				elif ext_ == 'regex':

					pattern = request.form['regx_pattern']
					tempdf = pd.DataFrame({'claimno':[i], 'text':[txt], keywd:[regex_output(txt,pattern)]})
					df = pd.concat([df, tempdf], axis = 0)
		
		return output_format(df, path, keywd)


############### OCR functions #####################################

@app.route('/ocr_validate', methods = ['POST'])
def ocr_validation():
	if request.method == 'POST':

		import webbrowser
		new = 2
		doc = request.form['document_number']
		url = "D:/Malaysia/tst_ocr/out/"+doc+'/'+doc+".html"
		webbrowser.open(url,new=new)
		return  render_template("ocr_home.html")


@app.route('/ocr_run', methods = ['POST'])
def ocr_run():
	if request.method == 'POST':
		wd = request.form['test']
		#os.chdir(wd)
		path = 'D:/Malaysia/tst_ocr/test'
		tot_doc = len(os.listdir(path))
		os.system('cmd /k "workon ocr && cd tst_ocr && run.bat"')
		#os.system('cmd /k "cd tst_ocr"')
		#os.system('cmd /k "run.bat"')
		return render_template('ocr_home.html', tot_doc =  tot_doc)




if __name__ == '__main__':
    app.debug = True
    app.run(port=4996)