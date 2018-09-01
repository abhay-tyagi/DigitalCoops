from django.db import models
from django.contrib.auth.models import User

#from django.contrib.contenttypes.models import ContentType

# Create your models here.

class UserProfile(models.Model):
	COURSES = (
		('Select course', '-'),
		('Btech', 'Btech'),
		('Mtech', 'Mtect'),
		('MCA', 'MCA'),
	)

	ACCOUNTS = (
			('Select account', '-'),
			('Admin', 'Admin'),
			('Student', 'Student'),
	)	

	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	registration_number = models.IntegerField(default=0)
	wallet_balance = models.FloatField(default=0)
	course = models.CharField(max_length=50, choices=COURSES, default='-')
	category = models.CharField(max_length=50, choices=ACCOUNTS)
	# cart = models.IntegerField(null=True)

	def __str__(self) :
	    return self.user.username


class Item(models.Model):
	CATEGORIES = (
		('Select category', '-'),
		('Stationary', 'Stationary'),
		('Eatables', 'Eatables'),
	)

	name = models.CharField(max_length=50)
	category = models.CharField(max_length=50, choices=CATEGORIES, default='-')
	quantity = models.IntegerField()
	pic = models.FileField(upload_to = 'images/', null=True, blank=True)
	specs = models.TextField()
	unit_price = models.IntegerField()
	item_id = models.IntegerField(primary_key=True)
	
	def __str__(self):
		return self.name 

	@property
	def status(self):
		if self.quantity:
			return True
		return False


class CartItem(models.Model):
	cart_present = models.ForeignKey(UserProfile)
	item = models.ForeignKey(Item)


class Transactions(models.Model):
	transaction_id = models.IntegerField(primary_key=True)
	transaction_date = models.DateField(null=True)
	items_included = models.IntegerField()


class ItemSold(models.Model):
	selling_id = models.IntegerField(primary_key=True)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE)
	sell_date = models.DateField(null=True)


class Review(models.Model):
	title = models.CharField(max_length=30)
	body = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
	review_date = models.DateField(null=True)

	def __str__(self):
		return self.title