from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response  
from .models import Item, Review, User, Transactions, CartItem, ItemSold, UserProfile
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.views.generic import View
import datetime

# Create your views here.

def index(request):
    items = Item.objects.all()

    return render(request, 'Website/index.html', {'items': items})


def item_details(request, pk):
    item = get_object_or_404(Item, pk=pk)
    reviews = Review.objects.filter(product=item)

    if request.user.is_authenticated:
        new_title = request.GET.get('title')
        new_content = request.GET.get('comment')
        usern = request.user.get_username()

        new_r = Review()
        new_r.title = new_title
        new_r.body = new_content
        new_r.user = User.objects.get(username=usern)
        new_r.product = item

        if new_r.title is not None:
            new_r.save()

    return render(request, 'Website/item_details.html', {'item': item, 'reviews': reviews})


class register(View):
    form_class = UserForm
    template_name = 'Website/register.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        already_member = True
        if form.is_valid():
            user = form.save(commit = False)
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username = username, password = password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')

        return render(request, self.template_name, {'form': form, 'already_member': already_member})


def add_to_cart(request, pk):
    product = Item.objects.get(pk=pk)

    cartItem = CartItem()
    cartItem.item = product
    cartItem.cart_present = request.user
    cartItem.save()

    return redirect('show_cart')


def remove_from_cart(request, pk):
    product = Item.objects.get(pk=pk)
    cart = Cart(request)
    cart.remove(product)

    return redirect('show_cart')


def get_cart(request):
    cart = CartItem.objects.filter(cart_present = request.user)

    total_cost = 0
    for product in cart:
        total_cost += product.item.unit_price

    # print cart

    return render(request, 'Website/show_cart.html', {'pay': str(total_cost), 'cart': cart})


def thanks_buy(request, pk):
    item = get_object_or_404(Item, pk=pk)

    item.quantity -= 1
    item.save()

    t = Transactions()
    t.transaction_id = len(Transactions.objects.all())
    t.items_included = 1
    t.save()

    it = ItemSold()
    it.selling_id = len(ItemSold.objects.all())
    it.item = item
    it.transaction = t
    it.save()

    return render(request, 'Website/thanks_buy.html', {'item': item})


def thanks_cart(request, cost):
    pass

    #     return render(request, 'Website/thanks_cart.html', {'cart': cart, 'cost': cost})
    # else:
    #     return render(request, 'Website/no_product.html', {})



def clear_cart(request):
    cart = Cart(request)
    cart.clear()

    return render(request, 'Website/clear_cart.html', {})


def contact_us(request):
    return render(request, 'Website/contact_us.html', {})

def search(request):
    if request.method == 'GET': 
        sq = request.GET.get('search', None)
        items = Item.objects.filter(name__icontains=sq)

        users = User.objects.all()

        print items

        if items:
            return render(request,'Website/search_result.html', {'items':items})
        else:
            return render(request, 'Website/search_none.html', {})
