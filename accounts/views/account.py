from accounts.forms import AccountForm
from accounts.models import Category, Entry, Account, Unit
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Count, Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

def dashboard(request):
	accounts = Account.objects.all()

	return render(request, 'ledger/accounts/dashboard/dashboard.html', locals())

def account(request, slug):
	account = get_object_or_404(Account, slug=slug)
	entries = account.entry_set.all().reverse()[:7]

	cs = Entry.objects.filter(account=account).values('category__name').annotate(count=Count('category')).order_by('category__name')
	categories = {}
	for c in cs:
		categories[c['category__name'].lower()] = c['count']
	category_data = [{'data':categories, 'name':'entries'}]

	ts = Entry.objects.filter(account=account).filter(tags__isnull=False).values('tags__name').annotate(count=Count('tags')).order_by('tags__name')
	tags = {}
	for t in ts:
		tags[t['tags__name'].lower()] = t['count']
	tag_data = [{'data':tags, 'name':'entries'}]

	return render(request, 'ledger/accounts/account/account.html', locals())

def entries(request, slug):
	account = get_object_or_404(Account, slug=slug)

	paginator = Paginator(account.entry_set.all(), 25)
	page = request.GET.get('page')
	try:
		entries = paginator.page(page)
		page = int(page)
	except PageNotAnInteger:
		page = paginator.num_pages
		entries = paginator.page(paginator.num_pages)
	except EmptyPage:
		page = paginator.num_pages
		entries = paginator.page(paginator.num_pages)

	try:
		last_prev = paginator.page(entries.previous_page_number()).object_list[24]
	except InvalidPage:
		last_prev = None

	try:
		first_next = paginator.page(entries.next_page_number()).object_list[0]
	except InvalidPage:
		first_next = None

	return render(request, 'ledger/accounts/account/entries.html', locals())

@csrf_protect
def add_account(request):
	if request.method == 'POST':
		form = AccountForm(request.POST)
		if form.is_valid():
			unit = get_object_or_404(Unit, id=form.cleaned_data['unit'])
			account = Account.objects.create(name=form.cleaned_data['name'], unit=unit)
			messages.add_message(request, messages.SUCCESS, 'The account %s has successfully been created.' % account.name)
			return redirect('account', slug=account.slug)
		else:
			return render(request, 'ledger/accounts/account/add.html', locals())
	else:
		form = AccountForm()
		return render(request, 'ledger/accounts/account/add.html', locals())