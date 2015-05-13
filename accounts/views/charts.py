from django.db.models import Q
from django.http import HttpResponse
import json

def tag(request):
	if request.is_ajax():
		# q = request.GET.get('term', '')
		# books = Book.objects.filter(title__icontains=q).distinct('title')[:10]
		# results = []
		# for book in books:
		# 	book_json = {}
		# 	book_json['id'] = book.id
		# 	book_json['label'] = book.title
		# 	book_json['value'] = book.title
		# 	if not next((True for item in results if item['value'] == book.title), False):
		# 		results.append(book_json)

		# persons = Person.objects.filter(Q(firstname__icontains=q) | Q(lastname__icontains=q)).distinct('lastname', 'firstname')[:10]
		# for person in persons:
		# 	person_json = {}
		# 	person_json['id'] = person.id
		# 	person_json['label'] = str(person)
		# 	person_json['value'] = str(person)
		# 	if not next((True for item in results if item['value'] == str(person)), False):
		# 		results.append(person_json)

		# series = Series.objects.filter(name__icontains=q).distinct('name')[:10]
		# for s in series:
		# 	series_json = {}
		# 	series_json['id'] = s.id
		# 	series_json['label'] = s.name
		# 	series_json['value'] = s.name
		# 	if not next((True for item in results if item['value'] == s.name), False):
		# 		results.append(series_json)

		# publishers = Publisher.objects.filter(name__icontains=q).distinct('name')[:10]
		# for publisher in publishers:
		# 	publisher_json = {}
		# 	publisher_json['id'] = publisher.id
		# 	publisher_json['label'] = publisher.name
		# 	publisher_json['value'] = publisher.name
		# 	if not next((True for item in results if item['value'] == publisher.name), False):
		# 		results.append(publisher_json)

		# results = sorted(results, key=lambda result: result['label'])[:10]
		data = json.dumps([{'name':'Test', 'type':'column', 'data':[10,5,8,9,2,3,4,6]}])
		print(data)
	else:
		data = 'fail'

	mimetype = 'application/json'
	return HttpResponse(data, mimetype)