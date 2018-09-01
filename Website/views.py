from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response  
from .models import Item, Review, User
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.views.generic import View

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
    cart = Cart(request)
    cart.add(product, product.unit_price, 1)

    return redirect('show_cart')


def remove_from_cart(request, pk):
    product = Item.objects.get(pk=pk)
    cart = Cart(request)
    cart.remove(product)

    return redirect('show_cart')


def get_cart(request):
    cart = Cart(request)

    pay = 0
    for item in cart:
        pay += int(item.total_price)

    return render(request, 'Website/show_cart.html', {'pay': str(pay), 'cart': Cart(request)})


def thanks_buy(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.xcord == 0:
        print "Sorry, I do not know where it is. Need to scan and search"
        return redirect('index')
    else:
        item.quantity -= 1
        item.save()

        with open('position.txt', 'r') as f:
            coords = f.read(2)
        xpos = int(coords[0])
        ypos = int(coords[1])

        qr = Arduino_call.go_to_product(xpos, ypos, item.xcord, item.ycord)

        if qr == item.QRcode:
                print 'Found '+item.name
                return render(request, 'Website/thanks_buy.html', {'item': item})
        else:
            print 'Unexpected product'
            item.ycord = 0
            item.xcord = 0
            item.save()

            new_item = Item.objects.get(QRcode=qr)
            new_item.ycord = item.ycord
            new_item.xcord = item.xcord
            new_item.save()

            print new_item.name+' is '+' present here, not '+item.name

        with open('position.txt', 'w') as f:
            f.write(str(new_item.xcord))
            f.write(str(new_item.ycord))

        return redirect('index')


def thanks_cart(request, cost):
    cart = Cart(request)
    flag = 0
    for item in cart:
        prod = Item.objects.get(name=item.product.name)

        if prod.xcord == 0:
            print "Sorry, I do not know where this is. Need to search and scan."
            return redirect('index')
        else:
            with open('position.txt', 'r') as f:
                coords = f.read(2)
            xpos = int(coords[0])
            ypos = int(coords[1])
            
            qr = Arduino_call.go_to_product(xpos, ypos, item.product.xcord, item.product.ycord)
            
            if qr == item.product.QRcode:
                print 'Found '+item.product.name
            else:
                flag = 1
                break
                print 'Unexpected product'
                to_remove = Item.objects.get(name=item.product.name)
                to_remove.ycord = 0
                to_remove.xcord = 0
                to_remove.save()

                new_item = Item.objects.get(QRcode=qr)
                new_item.ycord = item.product.ycord
                new_item.xcord = item.product.xcord
                new_item.save()

                print new_item.name+' is '+' present here, not '+item.product.name

            with open('position.txt', 'w') as f:
                f.write(str(prod.xcord)+str(prod.ycord))
    if flag == 0:
        return render(request, 'Website/thanks_cart.html', {'cart': cart, 'cost': cost})
    else:
        return render(request, 'Website/no_product.html', {})



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
