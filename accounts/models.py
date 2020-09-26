import datetime
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


# Create your models here.


class BasicDetails(models.Model):
    residential_address1 = models.TextField(null=True, blank=True)
    residential_address2 = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_company = models.BooleanField(default=False)
    is_firm = models.BooleanField(default=False)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    firm_name = models.CharField(max_length=50, null=True, blank=True)
    person_name = models.CharField(max_length=50, null=True, blank=True)
    person_relation = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.phone_number if self.phone_number else "None"


class IdentityDetails(models.Model):
    dob = models.DateField(null=True, blank=True)
    ssn = models.CharField(max_length=50, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    dependents = models.CharField(max_length=5, null=True, blank=True)
    investment_experience = models.CharField(max_length=50, null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True, blank=True)
    accountno = models.TextField(null=True, blank=True)
    pancard = models.TextField(null=True, blank=True)
    aadharcard = models.TextField(null=True, blank=True)
    buyingpower = models.CharField(default=0,max_length=100,null=True, blank=True)
    portfolio_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user_identity_rel.all()[0].user.first_name if self.user_identity_rel.all() else "None"


class UserDetails(models.Model):
    # first_name = models.CharField(max_length=30,null=True,blank=True)
    # last_name= models.CharField(max_length=30,null=True,blank=True)
    # email= models.CharField(max_length=30,unique=True)
    user = models.OneToOneField(User, related_name='user_details', on_delete=models.CASCADE)
    basic_info = models.ForeignKey(BasicDetails, null=True, blank=True, on_delete=models.CASCADE)
    identity = models.ForeignKey(IdentityDetails,related_name='user_identity_rel', null=True, blank=True, on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'

    def __str__(self):
        return str(self.user.email) if self.user.email else "None"


class StockNames(models.Model):
    name = models.TextField(null=True, blank=True)
    symbol = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.symbol


STATUS = (
    ('pending', 'pending'),
    ('executed', 'executed')
)


class StockHistory(models.Model):
    stock = models.OneToOneField(StockNames, related_name='history', on_delete=models.CASCADE)
    history_json = JSONField()
    current_data = JSONField(null=True,blank=True)
    last_update = models.DateField(null=True,blank=True)

    def __str__(self):
        return self.stock.symbol


class StockInfo(models.Model):
    stock = models.OneToOneField(StockNames, related_name='stock_info', on_delete=models.SET_NULL,null=True,blank=True)
    trailing_pe = models.FloatField(null=True, blank=True)
    market_cap = models.FloatField(null=True, blank=True)
    price_to_book = models.FloatField(null=True, blank=True)
    company_info = models.TextField(null=True,blank=True)
    officers = JSONField(null=True,blank=True)
    employees = models.CharField(max_length=500,null=True, blank=True)
    headquaters = models.CharField(max_length=500,null=True, blank=True)
    pe_ratio = models.CharField(max_length=500,null=True, blank=True)
    open_price = models.CharField(max_length=500,null=True, blank=True)
    low_today = models.CharField(max_length=500,null=True, blank=True)
    high_today = models.CharField(max_length=500,null=True, blank=True)
    sector = models.CharField(max_length=500,null=True, blank=True)

    def __str__(self):
        return self.stock.symbol


class StockGeneral(models.Model):
    Stockticker = models.OneToOneField(StockNames, related_name='general', on_delete=models.SET_NULL,null=True,blank=True)
    GISC = models.CharField(max_length=500,null=True, blank=True)
    Industry = models.CharField(max_length=500,null=True, blank=True)
    ROE = models.CharField(max_length=500,null=True, blank=True)
    PE = models.CharField(max_length=500,null=True, blank=True)
    DE = models.CharField(max_length=500,null=True, blank=True)#(DebttoEquity)
    GPM = models.CharField(max_length=500,null=True, blank=True)#GrossProfitMargin
    companyname = models.CharField(max_length=500,null=True, blank=True)

    def __str__(self):
        return self.Stockticker.symbol

class Transaction(models.Model):
    userid = models.ForeignKey(User, related_name='transaction_rel', on_delete=models.CASCADE)
    accountno = models.TextField(null=True, blank=True)
    time = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)
    # stockticker = models.TextField(null=True, blank=True)
    stockticker = models.ForeignKey(StockNames,related_name="stock_transaction_rel",on_delete=models.SET_NULL,null=True,blank=True)
    size = models.TextField(null=True, blank=True)
    ordertype = models.TextField(null=True, blank=True)
    expires = models.CharField(max_length=50,null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    limit_price = models.FloatField(null=True, blank=True)
    status = models.TextField(choices=STATUS, default='pending', null=True, blank=True)
    remove_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return str(self.userid.first_name)+" >>> "+str(self.stockticker) if self.userid else str(self.stockticker)


class Position(models.Model):
    userid = models.ForeignKey(User, related_name='userposition_rel', on_delete=models.CASCADE)
    accountno = models.CharField(max_length=100,null=True, blank=True)
    stockname = models.ForeignKey(StockNames, related_name='stockposition_rel', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    transaction_details = models.ForeignKey(Transaction, related_name='stockposition_transaction_rel', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    ticker = models.CharField(max_length=100,null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    ordertype = models.CharField(max_length=100,null=True, blank=True)
    unrealised_gainloss = models.CharField(default=0,max_length=100,null=True, blank=True)
    margin = models.CharField(max_length=100,null=True, blank=True)
    interest = models.FloatField(null=True, blank=True)
    equity = models.CharField(max_length=100,null=True, blank=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now(),null=True,blank=True)

    def __str__(self):
        return str(self.userid.first_name)+" >>> "+str(self.stockname.symbol) if self.userid else str(self.stockname.symbol)


class Portolfio(models.Model):
    userid = models.ForeignKey(User, related_name='portfolio_rel', on_delete=models.CASCADE)
    accountno = models.TextField(null=True, blank=True)
    tensector = models.TextField(null=True, blank=True)
    gainloss = models.TextField(null=True, blank=True)


class TopSearched(models.Model):
    userid = models.ForeignKey(User, related_name='user_top_search_rel', on_delete=models.SET_NULL,null=True,blank=True)
    stock = models.ForeignKey(StockNames, related_name='stock_top_search_rel', on_delete=models.SET_NULL,null=True,blank=True)
    count = models.IntegerField(max_length=10,default=0,null=True,blank=True)

class TransactionHistory(models.Model):
    position_obj = models.ForeignKey(Position, related_name='histroy_position_rel', on_delete=models.SET_NULL, null=True,
                                  blank=True)
    stock_number = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10,null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)


class TotalGainLoss(models.Model):
    userid = models.ForeignKey(User, related_name='user_total_gl_rel', on_delete=models.SET_NULL, null=True,
                               blank=True)
    gainloss = models.CharField(default=0, max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)


class GainLossHistory(models.Model):
    userid = models.ForeignKey(User, related_name='user_gl_history_rel', on_delete=models.SET_NULL, null=True,
                               blank=True)
    stock = models.ForeignKey(StockNames, related_name='stock_gl_history_rel', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    position_obj = models.ForeignKey(Position, related_name='gl_history_position_rel', on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)
    unrealised_gainloss = models.CharField(default=0,max_length=100,null=True, blank=True)
    realised_gainloss = models.CharField(default=0,max_length=100,null=True, blank=True)
    total_cash = models.CharField(default=0,max_length=100,null=True, blank=True)
    is_calculated = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)

class GainLossChartData(models.Model):
    userid = models.ForeignKey(User, related_name='user_gl_chart_data_rel', on_delete=models.SET_NULL, null=True,
                               blank=True)
    gainloss_data = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True, blank=True)