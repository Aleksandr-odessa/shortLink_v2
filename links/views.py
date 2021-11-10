from django.shortcuts import render, redirect
from django import forms
from django.urls import path
from .short_link import short_link
from django.db import connection
from django.forms import ModelForm
from django.http import HttpResponse

class LinkForm(forms.Form):
	Url=forms.CharField(label='', widget=forms.Textarea(attrs={'class':'myclass',}))

CREATE_TABLE = '''
CREATE TABLE if not exists links_link(
'id' int primary key,
"Url" TEXT,
"url_key" CHAR(7)
);'''
	
def create_table(request):
	with connection.cursor() as cur:
		cur.execute(CREATE_TABLE)
	return HttpResponse('The table is created')


RECORD_LINK = '''INSERT INTO links_link (Url, URL_key) VALUES(%s,%s)'''
REQ_BD = ''' SELECT Url FROM links_link where URL_key = %s'''
REQ_Long_BD = ''' SELECT URL_key FROM links_link where Url = %s'''


def recordLink (link_long):
	long_link=(link_long,)
	with connection.cursor() as cur:
		cur.execute(REQ_Long_BD,long_link)
		URL_key = cur.fetchone()
		if URL_key:
			output_key = URL_key[0]
		else:
			key = short_link(link_long)
			if key:
				links = (link_long, key)
				cur.execute(RECORD_LINK, links)
				output_key = key
			else:
				output_key = False	
	return (output_key)
	
		
def search_link(request,key):
	form = LinkForm()
	with connection.cursor() as cur:
		short_key = (key,)
		cur.execute(REQ_BD,short_key)
		link_URL = cur.fetchone()
		if link_URL:
			return redirect(link_URL[0])
		else:
			return redirect('/')
			
	
def index(request):
	if request.method == 'GET':
		form = LinkForm()
		output_index = {'form':form,}
	elif request.method == 'POST':
		form = LinkForm(request.POST)
		if form.is_valid():
			link = form.cleaned_data['Url']
			output_key=recordLink(link)
			form = LinkForm()
			output_index = {'form':form, 'key': output_key, 'link':link,}
	return render(request, 'index.html', output_index)