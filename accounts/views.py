import datetime
import json
import threading

import dateutil
import requests
from django.contrib.auth import login
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from yahoo_fin import stock_info as si

from accounts.forms import CustomAuthForm, UserDetailsForm, IdentityDetailsForm
# Create your views here.
from accounts.models import IdentityDetails, UserDetails, StockNames, StockHistory, StockInfo, \
    TopSearched, Transaction, Position, TransactionHistory, GainLossHistory, TotalGainLoss, GainLossChartData
from sterling_square import tokens


class CustomLogin(auth_views.LoginView):
    """Login View."""

    redirect_authenticated_user = True
    form_class = CustomAuthForm

    def form_valid(self, form):
        login(self.request, form.get_user())

        return HttpResponseRedirect(self.get_success_url())


class LoginView(TemplateView):
    """
    Login page
    """
    template_name = 'login.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        response = {}
        loginform = CustomAuthForm(request, data=request.POST)
        if loginform.is_valid():
            try:
                user = User.objects.get(email=request.POST.get("username"))
                login(request, user)
                response['status'] = True
            except:
                response['status'] = False
        else:
            response['status'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")


class UpdateStockScheduler(TemplateView):
    """
    Login page
    """
    template_name = 'signup.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStockScheduler, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateStockScheduler, self).get_context_data(**kwargs)
        from sterling_square.celery_file import stock_update
        stock_update()
        return context


class SignupView(TemplateView):
    """
    Login page
    """
    template_name = 'signup.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        response = {}
        userdetails_form = UserDetailsForm(request.POST)
        # basicdetails_form = BasicDetailsForm(request.POST)
        identitydetails_form = IdentityDetailsForm(request.POST)

        # ssn = str(request.POST.get("ssn1"))+str(request.POST.get("ssn2"))+str(request.POST.get("ssn3"))
        # dob = str(request.POST.get("dob_date"))+"-"+str(request.POST.get("dob_month"))+"-"+str(request.POST.get("dob_year"))
        # dob_obj = datetime.datetime.strptime(dob, '%d-%m-%Y')
        if userdetails_form.is_valid() and identitydetails_form.is_valid():
            user_save = userdetails_form.save(commit=False)
            user_save.email = request.POST.get("email")
            user_save.username = request.POST.get("email")
            # basic_detail_save = basicdetails_form.save()
            identity_save = identitydetails_form.save()
            # identity_save.ssn = ssn
            # identity_save.dob = dob_obj
            # basic_obj = BasicDetails.objects.get(id=basic_detail_save.id)
            identity_obj = IdentityDetails.objects.get(id=identity_save.id)
            # user_save.basic_info = basic_obj
            user_save.identity = identity_obj
            user_save.set_password(request.POST.get("password"))
            user_save.save()
            UserDetails.objects.create(user=user_save, identity=identity_obj)
        return HttpResponse(json.dumps(response), content_type="application/json")


class DashboardView(TemplateView):
    template_name = 'dashboard.html'  # 'dashboard.html'

    def get(self, request, *args, **kwargs):
        context = {}
        if request.user.is_authenticated:
            # position_obj = request.user.userposition_rel.first()
            # if position_obj:
            #     stock_obj = StockNames.objects.get(symbol=position_obj.stockname.symbol)
            #     context = stock_obj.history.history_json['data']
            #     # response = stock_obj.history.history_json['response']
            #     context['has_position'] = True
            #     print("????????????????    ",position_obj.stockname.symbol )
            #     try:
            #         d_data = si.get_data(position_obj.stockname.symbol + ".NS", interval="1d")
            #         d_price_list = d_data.values.tolist()
            #         prev_day_price = d_price_list[len(d_price_list) - 2][4]
            #         context['prev_day_price'] = prev_day_price
            #     except:
            #         pass
            #     try:
            #         stockprice = context.get('stockprice')
            #     except:
            #         stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
            #         context['stockprice'] = stockprice
            #     context2 = get_position_details(request,stock_obj,position_obj,stockprice)
            #     context.update(context2)
            #     # response['prev_day_price'] = prev_day_price
            # else:
            #     context['stock_price_list'] = [0, 0]
            #     context['stockprice'] = 0
            value_list = []
            try:
                buyingpower = UserDetails.objects.get(user=request.user).identity.buyingpower
            except:
                buyingpower = 0
            print("buyingpower   ", buyingpower)
            date = datetime.datetime.timestamp(datetime.datetime.now())
            choice_arr = []
            start_date = datetime.date(2019, 1, 1)
            end_date = datetime.date(2020, 8, 16)

            time_between_dates = end_date - start_date
            days_between_dates = time_between_dates.days
            distict_arr = []

            # TotalGainLoss.objects.all().delete()
            # for i in range(0,366):
            #     while True:
            #         random_number_of_days = random.randrange(days_between_dates)
            #         if not random_number_of_days in distict_arr:
            #             distict_arr.append(random_number_of_days)
            #             break
            #     random_date = start_date + datetime.timedelta(days=i)
            #     if len(TotalGainLoss.objects.filter(userid=request.user)) <366:
            #         # for j in range(0, 5):
            #         tgl_obj = TotalGainLoss.objects.create(userid=request.user)
            #         tgl_obj.gainloss = random.randint(0, 100)
            #         # start_date_time = datetime.datetime.combine(random_date, datetime.datetime.now().time())
            #         date_time = datetime.datetime.now() - dateutil.relativedelta.relativedelta(hours=random.randint(0, 5),minutes=random.randint(0, 59))
            #         tgl_obj.created_at = datetime.datetime.combine(random_date, datetime.datetime.now().time())
            #         print("??????////   ",datetime.datetime.now() - dateutil.relativedelta.relativedelta(hours=random.randint(0, 5),minutes=random.randint(0, 59)))
            #         tgl_obj.save()
            #     else:
            #         break
            # for pos_obj in Position.objects.filter(userid=request.user):
            #     date = datetime.datetime.timestamp(pos_obj.created_at)
            # stock_obj = StockNames.objects.get(symbol=pos_obj.stockname.symbol)
            # data = stock_obj.history.history_json['data']
            # response = stock_obj.history.history_json['response']
            # try:
            #     pos_stockprice = data['stockprice']
            # except:
            #     pos_stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
            # temp_price_list.append(int(date) * 1000)
            # value_list.append([int(date) * 1000,float(pos_obj.price)+float(buyingpower)])
            # print("value_listvalue_list    ",value_list)
            # try:
            current_date = datetime.datetime.now()
            current_time = current_date.time()
            timeflag = 0
            if int(current_time.hour) >= 9 and int(current_time.hour) < 15:
                timeflag = 1
            elif int(current_time.hour) == 15:
                if int(current_time.minute) <= 30:
                    timeflag = 1
            if timeflag == 1:
                try:
                    gl_obj = GainLossChartData.objects.get(userid=request.user)
                    value_list = [[x[0], float(x[1]) + float(buyingpower)] for x in gl_obj.gainloss_data]
                except:
                    value_list = []
                    if TotalGainLoss.objects.filter(userid=request.user):
                        for t_gl_obj in TotalGainLoss.objects.filter(userid=request.user):
                            # print("::::  ",t_gl_obj.gainloss)
                            tgl_date = datetime.datetime.timestamp(t_gl_obj.created_at)
                            value_list.append([int(tgl_date) * 1000, float(t_gl_obj.gainloss) + float(buyingpower)])
            else:
                if TotalGainLoss.objects.filter(userid=request.user):
                    for t_gl_obj in TotalGainLoss.objects.filter(userid=request.user):
                        # print("::::  ",t_gl_obj.gainloss)
                        tgl_date = datetime.datetime.timestamp(t_gl_obj.created_at)
                        value_list.append([int(tgl_date) * 1000, float(t_gl_obj.gainloss) + float(buyingpower)])
            # print("><><><<<    ",value_list)
            # print("value_list--   ",value_list)
            # value_list = gl_obj.gainloss_data
            # except:
            #     value_list = []
            # if not GainLossChartData.objects.filter(userid=request.user):
            #     gl_obj = GainLossChartData.objects.create(userid=request.user)
            #     gl_obj.gainloss_data = value_list
            #     gl_obj.save()
            # else:
            #     gl_obj = GainLossChartData.objects.get(userid=request.user)
            #     current_date = datetime.datetime.now()
            #     if gl_obj.created_at.date() != current_date.date():
            #         gl_obj.delete()
            #         gl_obj = GainLossChartData.objects.create(userid=request.user)
            #         gl_obj.gainloss_data = value_list
            #         gl_obj.save()

            context['stock_price_list'] = value_list
            context['current_amount'] = buyingpower
            context['stockprice'] = value_list[-1][1] if value_list else 0.00

        else:
            context['stock_price_list'] = [0, 0]
            context['stockprice'] = 0
        # try:
        #     context['stockprice'] = num_quantize(context['stockprice'])
        # except:
        #     print("{{{   0",stock_obj.symbol)
        #     try:
        #         context['stockprice'] = num_quantize(round(si.get_live_price(stock_obj.symbol + ".NS"), 2))
        #     except:
        #         context['stockprice'] = 0
        # update_live_price()
        from nsetools import Nse
        nse = Nse()
        if request.user.is_authenticated:
            top_searched = TopSearched.objects.filter(userid=request.user)
            if len(top_searched) > 10:
                top_searched = top_searched[:10]
            context['top_searched'] = top_searched
        lenn = 0
        sym = ''
        # for i in StockHistory.objects.all():
        #     if len(i.current_data) > 5 and i.history_json['stock_price_list']:
        #         if lenn < len(i.current_data):
        #             lenn = len(i.current_data)
        #             sym = i.stock.symbol

        # import requests
        # go_to_url = "https://www1.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json"
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        #     "Upgrade-Insecure-Requests": "1", "DNT": "1",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #     "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
        # resp = requests.get(go_to_url,headers=headers)
        # print("RRRR   ",resp,resp.json())
        # context['top_gainers'] = resp.json()
        # print("............      ",nse.get_top_gainers()[:5])
        # context['top_gainers'] = nse.get_top_gainers()[:5]
        from custom_packages.yahoo_finance import TG_DATA
        context['top_gainers'] = TG_DATA
        if request.is_ajax():
            from custom_packages.yahoo_finance import YahooFinance
            from nsetools import Nse
            response = {}
            ajxtype = request.GET.get("type")
            symbol = request.GET.get("symbol")

            if ajxtype == "get_stock_details":
                stock_obj = StockNames.objects.get(symbol=symbol)
                cc = StockHistory.objects.get(stock=stock_obj).history_json
                if StockHistory.objects.filter(stock=stock_obj):

                    data = stock_obj.history.history_json['data']
                    response = stock_obj.history.history_json['response']
                    # tttt = get_stock_details_json(symbol,request)

                    latest_price = YahooFinance(symbol + '.NS', result_range='1d', interval='1m', dropna='True').result
                    # price_list = latest_price.values.tolist()
                    current_time = datetime.datetime.now().time()
                    count = 0
                    for i, j in latest_price.iterrows():
                        temp_price_list = []
                        dt_object1 = datetime.datetime.strptime(str(i), "%Y-%m-%d %H:%M:%S")
                        my_time = dt_object1.time()
                        my_datetime = datetime.datetime.combine(i, my_time)
                        date = datetime.datetime.timestamp(my_datetime)

                        temp_price_list.append(int(date) * 1000)
                        temp_price_list.append(latest_price.values.tolist()[count][2])
                        # print(temp_price_list)
                        # latest_price_list.append(temp_price_list)
                        # data['stock_price_list'].append(temp_price_list)

                    try:
                        stock_gen_info = StockInfo.objects.get(stock=stock_obj)
                    except:
                        stock_gen_info = {}
                    data['stock_gen_info'] = stock_gen_info
                    try:
                        TopSearched.objects.get(stock=stock_obj, userid=request.user)
                        data['added_to_watchlist'] = True
                    except:
                        data['added_to_watchlist'] = False
                    try:
                        t_s_obj = TopSearched.objects.get(stock=stock_obj, userid=request.user)
                        t_s_obj.count += 1
                        t_s_obj.save()
                        # response['status'] = "removed"
                    except:
                        TopSearched.objects.get_or_create(stock=stock_obj, userid=request.user)
                        # response['status'] = "added"
                    data['earnings_graph_data'] = False
                    # response = price_change('1D', symbol)
                    try:
                        if len(data['estimate_list']) > 0 and len(data['actual_list']) > 0:
                            data['earnings_graph_data'] = True
                    except:
                        data['earnings_graph_data'] = False
                    response['status'] = "removed"
                    data['has_pos'] = "False"
                    data['stockname'] = stock_obj.name
                    if Position.objects.filter(userid=request.user, stockname=stock_obj):
                        data['has_pos'] = "True"
                    try:
                        data['stockprice'] = response['stockprice']
                    except:
                        data['stockprice'] = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
                    response['line_chart_html'] = render_to_string('includes/dashboard_includes/line-chart-main.html',
                                                                   data)
                    response['stock_market_settings_html'] = render_to_string(
                        'includes/dashboard_includes/stock_market_settings.html', data)
                    response['company_info_html'] = render_to_string('includes/dashboard_includes/company_info.html',
                                                                     data)
                    response['scatter_plot_html'] = render_to_string(
                        'includes/dashboard_includes/scatter-plot-chart-main.html', data)
                    try:
                        response['color'] = data['color']
                    except:
                        response['color'] = "#038afe"
                    transaction_list = paginate_data(request)
                    # print(transaction_list,">???")
                    if transaction_list:
                        response['up_activity_html'] = render_to_string(
                            "includes/dashboard_includes/upcoming_activity.html", {
                                "transaction_list": transaction_list
                            })
                        response['tr_status'] = "True"
                    total_share = 0
                    try:
                        print(">>?><>>>>>>><")
                        position_obj = Position.objects.filter(userid=request.user, stockname=stock_obj)[0]
                        try:
                            pos_stockprice = response['stockprice']
                        except:
                            pos_stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
                        response2 = get_position_details(request, stock_obj, position_obj, pos_stockprice)
                        response['has_position'] = True
                        response2['stockprice'] = pos_stockprice
                        response['pos_table_details_html'] = render_to_string(
                            "includes/dashboard_includes/position-table-details.html", response2)
                        # response.update(response2)
                        from django.db.models import Sum

                        for pos_stock in Position.objects.filter(userid=request.user, stockname=stock_obj):
                            total_share += int(pos_stock.transaction_details.size)

                        print("RESPONSE  ------------------------------ \n   ", response['stock_num'])

                    except Exception as e:
                        print("GET STOCK DETAIL POS ERROR    ", e)
                    response['stock_num'] = total_share
                    response['has_history'] = "True"
                    # response['dashboard_html'] = render_to_string('dashboard.html',data)
                    # response['dashboard_html'] = render_to_string('dashboard.html',data)
                else:
                    response['has_history'] = "False"
            elif ajxtype == "get_stock_real_data":

                # tata_power = YahooFinance(symbol+'.NS', result_range="1d", interval='1m',
                #                           dropna='True').result
                current_time = datetime.datetime.now().time()
                print("???????????????????????????//", int(current_time.hour))
                if int(current_time.hour) >= 9 and int(current_time.hour) < 15:
                    live_price = si.get_live_price(symbol + ".NS")
                    # live_price= tata_power.values.tolist()[len(tata_power.values.tolist()) - 1][0]
                    process = threading.Thread(target=update_position_and_gainloss,
                                               args=(live_price, symbol, request.user,))
                    process.start()
                    process.join()
                    response['data'] = float(str(num_quantize(live_price)))
                    response['status'] = True
                elif int(current_time.hour) == 15:
                    if int(current_time.minute) <= 30:
                        live_price = si.get_live_price(symbol + ".NS")
                        process = threading.Thread(target=update_position_and_gainloss,
                                                   args=(live_price, symbol, request.user,))
                        process.start()
                        process.join()
                        # live_price = tata_power.values.tolist()[len(tata_power.values.tolist()) - 1][0]
                        response['data'] = float(str(num_quantize(live_price)))
                        response['status'] = True
                    else:
                        response['status'] = False
                else:
                    response['status'] = False
                # from custom_packages.yahoo_finance import YahooFinance
                # latest_price = YahooFinance(symbol+'.NS', result_range='1d', interval='1m', dropna='True').result
                # print(latest_price)
                # price_list = latest_price.values.tolist()
                # last_price = price_list[len(price_list)-1][0]
                # random_num = [1775.95,1779.30,1776.42,1775.23,1775.95,1779.30,1776.42,1775.23]
                # response['data'] = random.choice(random_num)
                #
                # response['data'] = si.get_live_price(symbol + ".NS")
                # response['status'] = True
            elif ajxtype == "get_watched_stock_real_data":
                symbols = request.GET.getlist("symbols[]")
                prices = []
                for symbol in symbols:
                    live_price = si.get_live_price(symbol + ".NS")
                    monthly_data = si.get_data(symbol + ".NS", interval="1d")
                    # print("_____    ", monthly_data.values.tolist())
                    price_list = monthly_data.values.tolist()
                    prev_day_price = price_list[len(price_list) - 2][4]
                    difference = live_price - prev_day_price
                    # percentage = (live_price / prev_day_price) * 100

                    color = '#ff5000'
                    if float(difference) > 0:
                        color = '#01ec36'
                        difference = "+" + str(difference)
                    difference = num_quantize(float(difference))
                    difference = str(difference)
                    prices.append(
                        {'symbol': symbol, 'price': round(live_price, 2), 'difference': difference, 'color': color})
                response['data'] = prices

            elif ajxtype == "add-to-watchlist":
                symbol = request.GET.get("symbol")
                stock_obj = StockNames.objects.get(symbol=symbol)
                try:
                    TopSearched.objects.get(stock=stock_obj, userid=request.user).delete()
                    response['status'] = "removed"
                except:
                    TopSearched.objects.create(stock=stock_obj, userid=request.user)
                    response['status'] = "added"
                # top_search_obj.userid = request.user
                # top_search_obj.count += 1
                # top_search_obj.save()

            elif ajxtype == "price_change":
                key = request.GET.get("key")
                live_price = request.GET.get("live_price")
                prev_price = request.GET.get("prev_price")

                response = price_change(key, symbol, live_price, prev_price)


            elif ajxtype == "buy_stock":

                symbol = request.GET.get("symbol")

                expires = request.GET.get("expires")

                order_type = request.GET.get("order_type")

                share = request.GET.get("share")

                current_price = request.GET.get("current_price")

                limit_price = request.GET.get("limit_price")

                stock = StockNames.objects.get(symbol=symbol)

                current_date = datetime.datetime.now()

                remove_date = datetime.datetime.now()

                if request.user.is_authenticated:

                    user = UserDetails.objects.get(user=request.user)

                    identity = IdentityDetails.objects.get(id=user.identity.id)

                    user_buyingpower = float(user.identity.buyingpower)

                    if expires == "1":

                        expires_val = "Good for day"

                    else:

                        expires_val = "Good till canceled"

                    if order_type == "market_order":

                        transaction_obj, status = Transaction.objects.get_or_create(stockticker=stock,
                                                                                    ordertype=order_type,

                                                                                    price=current_price, size=share,

                                                                                    userid=request.user,
                                                                                    expires=expires_val)

                    else:

                        transaction_obj = Transaction.objects.create(stockticker=stock, ordertype=order_type,

                                                                     price=current_price, size=share,

                                                                     userid=request.user, expires=expires_val)

                    if expires != "1":
                        transaction_obj.remove_date = current_date + datetime.timedelta(days=90)

                        transaction_obj.save()

                    current_time = current_date.time()

                    flag = 0

                    print("current_time.hour  ", current_time.hour)

                    if int(current_time.hour) >= 9 and int(current_time.hour) < 15:

                        flag = 1

                    elif int(current_time.hour) == 15:

                        if int(current_time.minute) <= 30:
                            flag = 1

                    # elif int(current_time.hour) > 15 or int(current_time.hour) < 9:

                    #

                    #     flag = 1

                    if order_type == "market_order":

                        if flag == 1:

                            transaction_obj.status = "executed"

                            position_obj, status = Position.objects.get_or_create(userid=request.user, stockname=stock,

                                                                                  ticker=symbol,

                                                                                  price=current_price,
                                                                                  ordertype=order_type)

                            position_obj.transaction_details = transaction_obj

                            position_obj.save()

                            try:

                                history_obj = TransactionHistory.objects.get_or_create(position_obj=position_obj,
                                                                                       stock_number=share, status="buy")

                            except:

                                pass

                            # try:

                            total_cash = float(current_price) * int(share)

                            gl_history = GainLossHistory.objects.create(userid=request.user, stock=stock,
                                                                        total_cash=total_cash)

                            gl_history.unrealised_gainloss = num_quantize(

                                (float(current_price) - float(position_obj.transaction_details.price)) * int(share))

                            gl_history.position_obj = position_obj

                            gl_history.save()

                            user_buyingpower -= total_cash

                            identity.buyingpower = user_buyingpower

                            identity.save()

                            # except:

                            #     pass

                        else:

                            transaction_obj.status = "pending"


                    elif order_type == "limit_order":

                        transaction_obj.limit_price = limit_price

                    transaction_obj.save()


            elif ajxtype == "table_paginate":
                transaction_list = paginate_data(request)
                if transaction_list:
                    response['up_activity_html'] = render_to_string(
                        "includes/dashboard_includes/upcoming_activity.html", {
                            "transaction_list": transaction_list
                        })
                    response['tr_status'] = "True"

            elif ajxtype == "delete_transaction_data":
                Transaction.objects.get(id=request.GET.get("id")).delete()
                # position_obj_list = []
                # for position_obj in Position.objects.filter(userid=request.user):
                #     stock_obj = StockNames.objects.get(symbol=symbol)
                #     datas = stock_obj.history.history_json['data']
                #     data = {
                #         "date":position_obj.transaction_details.time,
                #         "ordertype":position_obj.ordertype,
                #         "size":position_obj.transaction_details.size,
                #         "price":position_obj.transaction_details.price,
                #         "current_price":datas.get("stock_price"),
                #         "gainloss":position_obj.unrealised_gainloss,
                #         "symbol":position_obj.ticker,
                #     }
                #     position_obj_list.append(data)

            elif ajxtype == "sell-stock":
                symbol = request.GET.get("symbol")
                share_num = int(request.GET.get("share_num"))
                current_price = si.get_live_price(symbol + ".NS")
                user_obj = UserDetails.objects.get(user=request.user)
                identity_obj = IdentityDetails.objects.get(id=user_obj.identity.id)
                buyingpower = float(identity_obj.buyingpower)
                for pos_obj in Position.objects.filter(userid=request.user, ticker=symbol).order_by("id"):
                    print("share_num    ", share_num)

                    stock_num = int(pos_obj.transaction_details.size)
                    print("stock_num    ", stock_num)

                    if stock_num == share_num:
                        stock_num -= share_num
                        pos_obj.transaction_details.size = stock_num
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=share_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                share_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,1111111111        buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()

                        except:
                            pass
                    elif stock_num > share_num:
                        # share_num = stock_num - share_num
                        stock_num -= share_num
                        pos_obj.transaction_details.size = stock_num
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=share_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                share_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,2222222222222    buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()
                        except Exception as e:
                            print("ERRORRRR  SELL STOCK  ", e)
                            pass
                        break
                    else:
                        share_num = share_num - stock_num
                        pos_obj.transaction_details.size = 0
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=stock_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                stock_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,33333333333      buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()
                        except:
                            pass
                    print("===========share_num    ", share_num)
                    print("===========stock_num    ", stock_num)
                    # pos_obj.save()
                    if int(pos_obj.transaction_details.size) == 0:
                        print("###########    REMAINING SHARE    ", pos_obj.transaction_details.size)
                        pos_obj.delete()
                    print("BUYYYING POWERRRR   ", buyingpower)
                identity_obj.buyingpower = num_quantize(buyingpower)
                identity_obj.save()

            # elif ajxtype == "chart_sort_gainloss":
            #     sort_type = request.GET.get("sort_type")
            #     try:
            #         buyingpower = UserDetails.objects.get(user=request.user).identity.buyingpower
            #     except:
            #         buyingpower = 0
            #     value_list = []
            #     if sort_type == "1m":
            #         last_month = ""
            #         for t_gl_obj in TotalGainLoss.objects.filter(userid=request.user,created_at__lte=datetime.datetime.now(),created_at__gte=last_month):
            #             print("::::  ", t_gl_obj.gainloss)
            #             tgl_date = datetime.datetime.timestamp(t_gl_obj.created_at)
            #             value_list.append([int(tgl_date) * 1000, float(t_gl_obj.gainloss) + float(buyingpower)])
            #     elif sort_type == "3m":
            #         pass
            #     elif sort_type == "6m":
            #         pass
            #     elif sort_type == "1y":
            #         pass
            #     else:
            #         pass
            return HttpResponse(json.dumps(response), content_type="application/json")
        return render(request, self.template_name, context)


class PositionTablesDetailsView(TemplateView):
    template_name = 'table-stock-position-details.html'

    def get(self, request, *args, **kwargs):
        context = {}
        position_obj_list = Position.objects.filter(userid=request.user).order_by("-id")
        # print("position_obj_list   ",position_obj_list)
        context['position_list'] = position_obj_list
        try:
            context['current_amount'] = UserDetails.objects.get(user=request.user).identity.buyingpower
        except:
            context['current_amount'] = 0
        return render(request, self.template_name, context)


def get_stock_details_json(symbol, request):
    """

    :param symbol:
    :return:
    """
    response = {}
    stock_obj = StockNames.objects.get(symbol=symbol)

    data = stock_obj.history.history_json
    data['symbol'] = symbol
    data['stock_price_list'] = []
    # 1day
    d_data = si.get_data(symbol + ".NS", interval="1d")
    d_price_list = d_data.values.tolist()
    prev_day_price = d_price_list[len(d_price_list) - 2][4]
    response['prev_day_price'] = prev_day_price
    # 1m
    today = datetime.datetime.now()
    start_date = today.date() - dateutil.relativedelta.relativedelta(months=2)
    prev_month = today.date() - dateutil.relativedelta.relativedelta(months=1)
    m_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_month, interval="1d")
    m_price_list = m_data.values.tolist()
    prev_month_price = m_price_list[len(m_price_list) - 1][4]
    response['prev_month_price'] = prev_month_price
    # 3m
    start_date = today.date() - dateutil.relativedelta.relativedelta(months=4)
    prev_3month = today.date() - dateutil.relativedelta.relativedelta(months=3)
    three_m_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_3month, interval="1d")
    three_m_price_list = three_m_data.values.tolist()
    prev_3m_price = three_m_price_list[len(three_m_price_list) - 1][4]
    response['prev_3m_price'] = prev_3m_price
    # 6m
    start_date = today.date() - dateutil.relativedelta.relativedelta(months=7)
    prev_6month = today.date() - dateutil.relativedelta.relativedelta(months=6)
    six_m_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_6month, interval="1d")
    six_m_price_list = six_m_data.values.tolist()
    prev_6m_price = six_m_price_list[len(six_m_price_list) - 1][4]
    response['prev_6m_price'] = prev_6m_price
    # 1y
    start_date = today.date() - dateutil.relativedelta.relativedelta(years=1, months=1)
    prev_year = today.date() - dateutil.relativedelta.relativedelta(years=1)
    y_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_year, interval="1d")
    y_price_list = y_data.values.tolist()
    prev_y_price = y_price_list[len(y_price_list) - 1][4]
    response['prev_y_price'] = prev_y_price

    try:
        t_s_obj = TopSearched.objects.get(stock=stock_obj, userid=request.user)
        t_s_obj.count += 1
        t_s_obj.save()
        # response['status'] = "removed"
    except:
        TopSearched.objects.get_or_create(stock=stock_obj, userid=request.user)
        # response['status'] = "added"

    date = datetime.datetime.timestamp(datetime.datetime.now())

    from custom_packages.yahoo_finance import YahooFinance
    latest_price = YahooFinance(symbol + '.NS', result_range='1d', interval='1m', dropna='True').result
    # print(latest_price)
    # price_list = latest_price.values.tolist()

    count = 0
    for i, j in latest_price.iterrows():
        temp_price_list = []
        dt_object1 = datetime.datetime.strptime(str(i), "%Y-%m-%d %H:%M:%S")
        my_time = dt_object1.time()
        my_datetime = datetime.datetime.combine(i, my_time)
        date = datetime.datetime.timestamp(my_datetime)
        temp_price_list.append(int(date) * 1000)
        temp_price_list.append(latest_price.values.tolist()[count][2])
        # latest_price_list.append(temp_price_list)
        # data['stock_price_list'].append(temp_price_list)
        count += 1
    for t_gainloss in request.user.user_total_gl_rel.all():
        date = datetime.datetime.timestamp(t_gainloss.created_at)
        # temp_price_list.append(int(date) * 1000)
        data['stock_price_list'].append([int(date) * 1000, float(t_gainloss.gainloss)])
    data['stockprice'] = num_quantize(si.get_live_price(symbol + ".NS"))
    print("STOCK PRICE  ----  ", data['stock_price_list'])
    return data, response


def price_change(key, symbol, live_price, prev_price):
    response = {}
    difference = 0
    percentage = 0
    color = "#ff5000"
    btn_color = "#ff5000"
    scatter_s_color = "rgba(255, 80, 0, 0.58)"
    scatter_s_color_status = False
    live_price = float(live_price)
    if key == '1D':
        # live_price = si.get_live_price(symbol + ".NS")
        # monthly_data = si.get_data(symbol + ".NS", interval="1d")
        # # print("_____    ", monthly_data.values.tolist())
        # price_list = monthly_data.values.tolist()
        # prev_day_price = price_list[len(price_list) - 2][4]
        live_price = num_quantize(live_price)
        prev_day_price = num_quantize(prev_price)
        difference = live_price - prev_day_price
        # percentage = (live_price / prev_day_price)
        percentage = ((live_price - prev_day_price) / prev_day_price) * 100
    if key == '1m':
        # live_price = si.get_live_price(symbol + ".NS")
        # today = datetime.datetime.now()
        # start_date = today.date() - dateutil.relativedelta.relativedelta(months=2)
        # prev_month = today.date() - dateutil.relativedelta.relativedelta(months=1)
        # monthly_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_month, interval="1d")
        # price_list = monthly_data.values.tolist()
        # prev_day_price = price_list[len(price_list) - 1][4]
        live_price = num_quantize(live_price)
        prev_day_price = num_quantize(prev_price)
        difference = live_price - prev_day_price
        # percentage = (live_price/prev_day_price)
        percentage = ((live_price - prev_day_price) / prev_day_price) * 100

    if key == '3m':
        # live_price = si.get_live_price(symbol + ".NS")
        # today = datetime.datetime.now()
        # start_date = today.date() - dateutil.relativedelta.relativedelta(months=4)
        # prev_month = today.date() - dateutil.relativedelta.relativedelta(months=3)
        # # print("prev_month  ",prev_month)
        # monthly_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_month, interval="1d")
        # # print("_____    ", monthly_data)
        # price_list = monthly_data.values.tolist()
        # prev_day_price = price_list[len(price_list) - 1][4]
        live_price = num_quantize(live_price)
        prev_day_price = num_quantize(prev_price)
        difference = live_price - prev_day_price
        # percentage = (live_price/prev_day_price)
        percentage = ((live_price - prev_day_price) / prev_day_price) * 100

    if key == '6m':
        # live_price = si.get_live_price(symbol + ".NS")
        # today = datetime.datetime.now()
        # start_date = today.date() - dateutil.relativedelta.relativedelta(months=7)
        # prev_month = today.date() - dateutil.relativedelta.relativedelta(months=6)
        # # print("prev_month  ",prev_month)
        # monthly_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_month, interval="1d")
        # # print("_____    ", monthly_data)
        # price_list = monthly_data.values.tolist()
        # prev_day_price = price_list[len(price_list) - 1][4]
        live_price = num_quantize(live_price)
        prev_day_price = num_quantize(prev_price)
        difference = live_price - prev_day_price
        # percentage = (live_price/prev_day_price)
        percentage = ((live_price - prev_day_price) / prev_day_price) * 100

    if key == '1y':
        # live_price = si.get_live_price(symbol + ".NS")
        # today = datetime.datetime.now()
        # start_date = today.date() - dateutil.relativedelta.relativedelta(years=1, months=1)
        # prev_month = today.date() - dateutil.relativedelta.relativedelta(years=1)
        # # print("prev_month  ",prev_month,start_date)
        # monthly_data = si.get_data(symbol + ".NS", start_date=start_date, end_date=prev_month, interval="1d")
        # # print("_____    ", monthly_data)
        # price_list = monthly_data.values.tolist()
        # prev_day_price = price_list[len(price_list) - 1][4]
        live_price = num_quantize(live_price)
        prev_day_price = num_quantize(prev_price)
        difference = live_price - prev_day_price
        # percentage = (live_price/prev_day_price)
        percentage = ((live_price - prev_day_price) / prev_day_price) * 100

    difference = num_quantize(float(difference))
    percentage = num_quantize(float(percentage))
    if difference >= 0:
        difference = "+" + str(difference)
        percentage = "+" + str(percentage)
        # color = "#01ec36" #light green
        btn_color = "#28a745"
        color = "#00ff39"
        scatter_s_color = "rgba(40, 167, 69, 0.58)"
        scatter_s_color_status = True

    response['color'] = color
    response['btn_color'] = btn_color
    response['scatter_s_color'] = scatter_s_color
    response['scatter_s_color_status'] = scatter_s_color_status
    response['percentage'] = str(percentage)
    response['difference'] = str(difference)
    return response


def logout_user(request):
    logout(request)
    return redirect("/")


def get_earnings(symbol, key, type):
    token = tokens.TOKEN_EOD_HISTORICAL_DATA
    a = requests.get("https://eodhistoricaldata.com/api/fundamentals/{}.NSE?api_token={}".format(symbol, token))
    js = json.loads(a.text)

    if type == "company_info":
        # print ( js.get("General"))
        info = js.get("General").get("Description")
        head_post = js.get("General").get("Officers").get("0").get("Title")
        head_name = js.get("General").get("Officers").get("0").get("Name")
        Headquarters = js.get("General").get("Address")
        officer_list = []
        for i, j in js.get("General").get("Officers").items():
            officer_dict = {
                'name': j.get("Name"),
                'title': j.get("Title")
            }
            officer_list.append(officer_dict)
        details_dict = {
            'about': info,
            'head_post': head_post,
            'head_name': head_name,
            'officer_list': officer_list,
            'Headquarters': Headquarters
        }
        result = details_dict
        # print (js.get("General"))
    else:
        history = js.get("Earnings").get("History")
        # print ("HISTORY   ",history)
        earnings_list = []
        for i, j in history.items():
            if j.get("epsEstimate") and j.get("epsActual"):
                temp_arr = []
                temp_arr.append(str(i))
                temp_arr.append(j.get(key))
                # earnings_dict = {
                #     'date':i,
                #     # 'estimated':i.get("epsEstimate"),
                #     key:j.get(key),
                #     # 'actual':i.get("epsActual")
                # }
                earnings_list.append(temp_arr)
        result = earnings_list
    return result


def num_quantize(value, n_point=2):
    """
    :param value:
    :param n_point:
    :return:
    """
    from decimal import localcontext, Decimal, ROUND_HALF_UP
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        if value:
            d_places = Decimal(10) ** -n_point
            # Round to two places
            value = Decimal(value).quantize(d_places)
        return value


def paginate_data(request, stock_symbol=None):
    from django.core.paginator import Paginator
    symbol = request.GET.get("symbol")
    if not request.GET.get("symbol"):
        symbol = stock_symbol
    stock_obj = StockNames.objects.get(symbol=symbol)
    user_list = Transaction.objects.filter(userid=request.user, stockticker=stock_obj, status="pending")
    page = request.GET.get('page', 1)
    paginator = Paginator(user_list, 5)
    from django.core.paginator import PageNotAnInteger
    from django.core.paginator import EmptyPage
    try:
        transaction_list = paginator.page(page)
    except PageNotAnInteger:
        transaction_list = paginator.page(1)
    except EmptyPage:
        transaction_list = paginator.page(paginator.num_pages)
    return transaction_list


def get_position_details(request, stock_obj, position_obj, stock_price):
    context = {}
    transaction_list = paginate_data(request, stock_symbol=stock_obj.symbol)
    if transaction_list:
        context['up_activity_html'] = render_to_string("includes/dashboard_includes/upcoming_activity.html", {
            "transaction_list": transaction_list
        })
        context['tr_status'] = "True"
    # context['position_details'] = position_obj
    share_num = 0
    total_cost = 0
    data = {}
    for pos in Position.objects.filter(userid=request.user, stockname=position_obj.stockname):
        if pos.transaction_details:
            share_num += int(pos.transaction_details.size)
            total_cost += float(pos.transaction_details.price) * int(pos.transaction_details.size)
    if share_num > 0 and total_cost > 0:
        average_cost = float(total_cost / share_num)
        context['average_cost'] = str(num_quantize(average_cost))
        context['share_num'] = str(share_num)
        total_return = 0
        # print ("FILTERED   ",Position.objects.filter(userid=request.user, stockname=stock_obj))
        try:
            for pos_obj in Position.objects.filter(userid=request.user, stockname=stock_obj):
                # print("pos_obj.unrealised_gainloss   ",pos_obj.unrealised_gainloss)
                if pos_obj.unrealised_gainloss:
                    total_return += float(pos_obj.unrealised_gainloss)
        except Exception as e:
            print("TOTAL RETURN ERROR    ", e)
            pass
        total_ret_perc = num_quantize((total_return / total_cost) * 100)
        # if total_return >= 0:
        #     total_return = "+"+str(total_return)
        #     total_ret_perc = "+"+str(total_ret_perc)
        # else:
        #     total_return = "-" + str(total_return)
        #     total_ret_perc = "-" + str(total_ret_perc)
        context['total_return'] = total_return
        context['total_return_percentage'] = total_ret_perc

        # context['pos_table_details_html'] = render_to_string("includes/dashboard_includes/position-table-details.html",data)
        # print("total_return   ",total_return)
        # context['today_return'] = num_quantize((float(stock_price) - average_cost) / average_cost)
    # print("context   ",context)
    return context


def get_latest_gainloss(request):
    try:
        buyingpower = UserDetails.objects.get(user=request.user).identity.buyingpower
    except:
        buyingpower = 0
    total_gl = 0

    for position_obj in request.user.userposition_rel.all():
        # current_price = si.get_live_price(position_obj.stockname.symbol + ".NS")
        # total_gl += float(gl_obj.unrealised_gainloss)
        # total_gl += num_quantize(
        #     (float(current_price) - float(position_obj.transaction_details.price)) * int(
        #         position_obj.transaction_details.size))
        total_gl += float(position_obj.price)
    # date = datetime.datetime.timestamp(datetime.datetime.now())
    # print("?>?>?>?    ", float(total_gl) + float(buyingpower))
    return num_quantize(float(total_gl) + float(buyingpower))


def update_position_and_gainloss(current_price, symbol, user):
    # total_price = 0
    # date = datetime.datetime.timestamp(datetime.datetime.now())
    # value_list = []
    for pos_obj in Position.objects.filter(stockname__symbol=symbol, userid=user):
        try:
            gl_history = GainLossHistory.objects.get(position_obj=pos_obj)
            gl_history.unrealised_gainloss = num_quantize(
                (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                    pos_obj.transaction_details.size))
            gl_history.save()
        except Exception as e:
            print("ERROR in update_position_and_gainloss FUNCTION", e)
        # total_price += num_quantize(float(pos_obj.price))
    # value_list.append([int(date) * 1000, float(total_price)])
    # if not GainLossChartData.objects.filter(userid=user):
    #     # print("value_listvalue_list    ",value_list)
    #     gl_obj = GainLossChartData.objects.create(userid=user)
    #     gl_obj.gainloss_data = value_list
    #     gl_obj.save()
    # else:
    #     gl_obj = GainLossChartData.objects.get(userid=user)
    #     gl_obj.gainloss_data.append([int(date) * 1000, float(total_price)])
    #     gl_obj.save()


class StockPageView(TemplateView):
    template_name = 'dashboardv1.html'

    def get(self, request, *args, **kwargs):
        context = {}
        stock_symbol = self.kwargs['stock_symbol']

        if request.user.is_authenticated:
            # position_obj = request.user.userposition_rel.first()
            # if position_obj:
            #     stock_obj = StockNames.objects.get(symbol=position_obj.stockname.symbol)
            #     context = stock_obj.history.history_json['data']
            #     # response = stock_obj.history.history_json['response']
            #     context['has_position'] = True
            #     print("????????????????    ",position_obj.stockname.symbol )
            #     try:
            #         d_data = si.get_data(position_obj.stockname.symbol + ".NS", interval="1d")
            #         d_price_list = d_data.values.tolist()
            #         prev_day_price = d_price_list[len(d_price_list) - 2][4]
            #         context['prev_day_price'] = prev_day_price
            #     except:
            #         pass
            #     try:
            #         stockprice = context.get('stockprice')
            #     except:
            #         stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
            #         context['stockprice'] = stockprice
            #     context2 = get_position_details(request,stock_obj,position_obj,stockprice)
            #     context.update(context2)
            #     # response['prev_day_price'] = prev_day_price
            # else:
            #     context['stock_price_list'] = [0, 0]
            #     context['stockprice'] = 0
            value_list = []
            try:
                buyingpower = UserDetails.objects.get(user=request.user).identity.buyingpower
            except:
                buyingpower = 0
            print("buyingpower   ", buyingpower)
            date = datetime.datetime.timestamp(datetime.datetime.now())
            choice_arr = []
            start_date = datetime.date(2019, 1, 1)
            end_date = datetime.date(2020, 8, 16)

            time_between_dates = end_date - start_date
            days_between_dates = time_between_dates.days
            distict_arr = []

            # TotalGainLoss.objects.all().delete()
            # for i in range(0,366):
            #     while True:
            #         random_number_of_days = random.randrange(days_between_dates)
            #         if not random_number_of_days in distict_arr:
            #             distict_arr.append(random_number_of_days)
            #             break
            #     random_date = start_date + datetime.timedelta(days=i)
            #     if len(TotalGainLoss.objects.filter(userid=request.user)) <366:
            #         # for j in range(0, 5):
            #         tgl_obj = TotalGainLoss.objects.create(userid=request.user)
            #         tgl_obj.gainloss = random.randint(0, 100)
            #         # start_date_time = datetime.datetime.combine(random_date, datetime.datetime.now().time())
            #         date_time = datetime.datetime.now() - dateutil.relativedelta.relativedelta(hours=random.randint(0, 5),minutes=random.randint(0, 59))
            #         tgl_obj.created_at = datetime.datetime.combine(random_date, datetime.datetime.now().time())
            #         print("??????////   ",datetime.datetime.now() - dateutil.relativedelta.relativedelta(hours=random.randint(0, 5),minutes=random.randint(0, 59)))
            #         tgl_obj.save()
            #     else:
            #         break
            # for pos_obj in Position.objects.filter(userid=request.user):
            #     date = datetime.datetime.timestamp(pos_obj.created_at)
            # stock_obj = StockNames.objects.get(symbol=pos_obj.stockname.symbol)
            # data = stock_obj.history.history_json['data']
            # response = stock_obj.history.history_json['response']
            # try:
            #     pos_stockprice = data['stockprice']
            # except:
            #     pos_stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
            # temp_price_list.append(int(date) * 1000)
            # value_list.append([int(date) * 1000,float(pos_obj.price)+float(buyingpower)])
            # print("value_listvalue_list    ",value_list)
            # try:
            current_date = datetime.datetime.now()
            current_time = current_date.time()
            timeflag = 0
            if int(current_time.hour) >= 9 and int(current_time.hour) < 15:
                timeflag = 1
            elif int(current_time.hour) == 15:
                if int(current_time.minute) <= 30:
                    timeflag = 1
            if timeflag == 1:
                try:
                    gl_obj = GainLossChartData.objects.get(userid=request.user)
                    value_list = [[x[0], float(x[1]) + float(buyingpower)] for x in gl_obj.gainloss_data]
                except:
                    value_list = []
                    if TotalGainLoss.objects.filter(userid=request.user):
                        for t_gl_obj in TotalGainLoss.objects.filter(userid=request.user):
                            # print("::::  ",t_gl_obj.gainloss)
                            tgl_date = datetime.datetime.timestamp(t_gl_obj.created_at)
                            value_list.append([int(tgl_date) * 1000, float(t_gl_obj.gainloss) + float(buyingpower)])
            else:
                if TotalGainLoss.objects.filter(userid=request.user):
                    for t_gl_obj in TotalGainLoss.objects.filter(userid=request.user):
                        # print("::::  ",t_gl_obj.gainloss)
                        tgl_date = datetime.datetime.timestamp(t_gl_obj.created_at)
                        value_list.append([int(tgl_date) * 1000, float(t_gl_obj.gainloss) + float(buyingpower)])
            # print("><><><<<    ",value_list)
            # print("value_list--   ",value_list)
            # value_list = gl_obj.gainloss_data
            # except:
            #     value_list = []
            # if not GainLossChartData.objects.filter(userid=request.user):
            #     gl_obj = GainLossChartData.objects.create(userid=request.user)
            #     gl_obj.gainloss_data = value_list
            #     gl_obj.save()
            # else:
            #     gl_obj = GainLossChartData.objects.get(userid=request.user)
            #     current_date = datetime.datetime.now()
            #     if gl_obj.created_at.date() != current_date.date():
            #         gl_obj.delete()
            #         gl_obj = GainLossChartData.objects.create(userid=request.user)
            #         gl_obj.gainloss_data = value_list
            #         gl_obj.save()

            context['stock_price_list'] = value_list
            context['current_amount'] = buyingpower
            context['stockprice'] = value_list[-1][1] if value_list else 0.00

        else:
            context['stock_price_list'] = [0, 0]
            context['stockprice'] = 0
        # try:
        #     context['stockprice'] = num_quantize(context['stockprice'])
        # except:
        #     print("{{{   0",stock_obj.symbol)
        #     try:
        #         context['stockprice'] = num_quantize(round(si.get_live_price(stock_obj.symbol + ".NS"), 2))
        #     except:
        #         context['stockprice'] = 0
        # update_live_price()
        from nsetools import Nse
        nse = Nse()
        if request.user.is_authenticated:
            top_searched = TopSearched.objects.filter(userid=request.user)
            if len(top_searched) > 10:
                top_searched = top_searched[:10]
            context['top_searched'] = top_searched
        lenn = 0
        sym = ''
        # for i in StockHistory.objects.all():
        #     if len(i.current_data) > 5 and i.history_json['stock_price_list']:
        #         if lenn < len(i.current_data):
        #             lenn = len(i.current_data)
        #             sym = i.stock.symbol

        # import requests
        # go_to_url = "https://www1.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json"
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        #     "Upgrade-Insecure-Requests": "1", "DNT": "1",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #     "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
        # resp = requests.get(go_to_url,headers=headers)
        # print("RRRR   ",resp,resp.json())
        # context['top_gainers'] = resp.json()
        # print("............      ",nse.get_top_gainers()[:5])
        # context['top_gainers'] = nse.get_top_gainers()[:5]
        from custom_packages.yahoo_finance import TG_DATA
        context['top_gainers'] = TG_DATA
        if request.is_ajax():
            from custom_packages.yahoo_finance import YahooFinance
            from nsetools import Nse
            response = {}
            ajxtype = request.GET.get("type")
            symbol = request.GET.get("symbol")

            if ajxtype == "get_stock_details":
                stock_obj = StockNames.objects.get(symbol=symbol)
                cc = StockHistory.objects.get(stock=stock_obj).history_json
                if StockHistory.objects.filter(stock=stock_obj):

                    data = stock_obj.history.history_json['data']
                    response = stock_obj.history.history_json['response']
                    # tttt = get_stock_details_json(symbol,request)

                    latest_price = YahooFinance(symbol + '.NS', result_range='1d', interval='1m', dropna='True').result
                    # price_list = latest_price.values.tolist()
                    current_time = datetime.datetime.now().time()
                    count = 0
                    for i, j in latest_price.iterrows():
                        temp_price_list = []
                        dt_object1 = datetime.datetime.strptime(str(i), "%Y-%m-%d %H:%M:%S")
                        my_time = dt_object1.time()
                        my_datetime = datetime.datetime.combine(i, my_time)
                        date = datetime.datetime.timestamp(my_datetime)

                        temp_price_list.append(int(date) * 1000)
                        temp_price_list.append(latest_price.values.tolist()[count][2])
                        # print(temp_price_list)
                        # latest_price_list.append(temp_price_list)
                        # data['stock_price_list'].append(temp_price_list)

                    try:
                        stock_gen_info = StockInfo.objects.get(stock=stock_obj)
                    except:
                        stock_gen_info = {}
                    data['stock_gen_info'] = stock_gen_info
                    try:
                        TopSearched.objects.get(stock=stock_obj, userid=request.user)
                        data['added_to_watchlist'] = True
                    except:
                        data['added_to_watchlist'] = False
                    try:
                        t_s_obj = TopSearched.objects.get(stock=stock_obj, userid=request.user)
                        t_s_obj.count += 1
                        t_s_obj.save()
                        # response['status'] = "removed"
                    except:
                        TopSearched.objects.get_or_create(stock=stock_obj, userid=request.user)
                        # response['status'] = "added"
                    data['earnings_graph_data'] = False
                    # response = price_change('1D', symbol)
                    try:
                        if len(data['estimate_list']) > 0 and len(data['actual_list']) > 0:
                            data['earnings_graph_data'] = True
                    except:
                        data['earnings_graph_data'] = False
                    response['status'] = "removed"
                    data['has_pos'] = "False"
                    data['stockname'] = stock_obj.name
                    if Position.objects.filter(userid=request.user, stockname=stock_obj):
                        data['has_pos'] = "True"
                    try:
                        data['stockprice'] = response['stockprice']
                    except:
                        data['stockprice'] = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
                    response['line_chart_html'] = render_to_string('includes/dashboard_includes/line-chart-main.html',
                                                                   data)
                    response['stock_market_settings_html'] = render_to_string(
                        'includes/dashboard_includes/stock_market_settings.html', data)
                    response['company_info_html'] = render_to_string('includes/dashboard_includes/company_info.html',
                                                                     data)
                    response['scatter_plot_html'] = render_to_string(
                        'includes/dashboard_includes/scatter-plot-chart-main.html', data)
                    try:
                        response['color'] = data['color']
                    except:
                        response['color'] = "#038afe"
                    transaction_list = paginate_data(request)
                    # print(transaction_list,">???")
                    if transaction_list:
                        response['up_activity_html'] = render_to_string(
                            "includes/dashboard_includes/upcoming_activity.html", {
                                "transaction_list": transaction_list
                            })
                        response['tr_status'] = "True"
                    total_share = 0
                    try:
                        print(">>?><>>>>>>><")
                        position_obj = Position.objects.filter(userid=request.user, stockname=stock_obj)[0]
                        try:
                            pos_stockprice = response['stockprice']
                        except:
                            pos_stockprice = round(si.get_live_price(stock_obj.symbol + ".NS"), 2)
                        response2 = get_position_details(request, stock_obj, position_obj, pos_stockprice)
                        response['has_position'] = True
                        response2['stockprice'] = pos_stockprice
                        response['pos_table_details_html'] = render_to_string(
                            "includes/dashboard_includes/position-table-details.html", response2)
                        # response.update(response2)
                        from django.db.models import Sum

                        for pos_stock in Position.objects.filter(userid=request.user, stockname=stock_obj):
                            total_share += int(pos_stock.transaction_details.size)

                        print("RESPONSE  ------------------------------ \n   ", response['stock_num'])

                    except Exception as e:
                        print("GET STOCK DETAIL POS ERROR    ", e)
                    response['stock_num'] = total_share
                    response['has_history'] = "True"
                    # response['dashboard_html'] = render_to_string('dashboard.html',data)
                    # response['dashboard_html'] = render_to_string('dashboard.html',data)
                else:
                    response['has_history'] = "False"
            elif ajxtype == "get_stock_real_data":

                # tata_power = YahooFinance(symbol+'.NS', result_range="1d", interval='1m',
                #                           dropna='True').result
                current_time = datetime.datetime.now().time()
                print("???????????????????????????//", int(current_time.hour))
                if int(current_time.hour) >= 9 and int(current_time.hour) < 15:
                    live_price = si.get_live_price(symbol + ".NS")
                    # live_price= tata_power.values.tolist()[len(tata_power.values.tolist()) - 1][0]
                    process = threading.Thread(target=update_position_and_gainloss,
                                               args=(live_price, symbol, request.user,))
                    process.start()
                    process.join()
                    response['data'] = float(str(num_quantize(live_price)))
                    response['status'] = True
                elif int(current_time.hour) == 15:
                    if int(current_time.minute) <= 30:
                        live_price = si.get_live_price(symbol + ".NS")
                        process = threading.Thread(target=update_position_and_gainloss,
                                                   args=(live_price, symbol, request.user,))
                        process.start()
                        process.join()
                        # live_price = tata_power.values.tolist()[len(tata_power.values.tolist()) - 1][0]
                        response['data'] = float(str(num_quantize(live_price)))
                        response['status'] = True
                    else:
                        response['status'] = False
                else:
                    response['status'] = False
                # from custom_packages.yahoo_finance import YahooFinance
                # latest_price = YahooFinance(symbol+'.NS', result_range='1d', interval='1m', dropna='True').result
                # print(latest_price)
                # price_list = latest_price.values.tolist()
                # last_price = price_list[len(price_list)-1][0]
                # random_num = [1775.95,1779.30,1776.42,1775.23,1775.95,1779.30,1776.42,1775.23]
                # response['data'] = random.choice(random_num)
                #
                # response['data'] = si.get_live_price(symbol + ".NS")
                # response['status'] = True
            elif ajxtype == "get_watched_stock_real_data":
                symbols = request.GET.getlist("symbols[]")
                prices = []
                for symbol in symbols:
                    live_price = si.get_live_price(symbol + ".NS")
                    monthly_data = si.get_data(symbol + ".NS", interval="1d")
                    # print("_____    ", monthly_data.values.tolist())
                    price_list = monthly_data.values.tolist()
                    prev_day_price = price_list[len(price_list) - 2][4]
                    difference = live_price - prev_day_price
                    # percentage = (live_price / prev_day_price) * 100

                    color = '#ff5000'
                    if float(difference) > 0:
                        color = '#01ec36'
                        difference = "+" + str(difference)
                    difference = num_quantize(float(difference))
                    difference = str(difference)
                    prices.append(
                        {'symbol': symbol, 'price': round(live_price, 2), 'difference': difference, 'color': color})
                response['data'] = prices

            elif ajxtype == "add-to-watchlist":
                symbol = request.GET.get("symbol")
                stock_obj = StockNames.objects.get(symbol=symbol)
                try:
                    TopSearched.objects.get(stock=stock_obj, userid=request.user).delete()
                    response['status'] = "removed"
                except:
                    TopSearched.objects.create(stock=stock_obj, userid=request.user)
                    response['status'] = "added"
                # top_search_obj.userid = request.user
                # top_search_obj.count += 1
                # top_search_obj.save()

            elif ajxtype == "price_change":
                key = request.GET.get("key")
                live_price = request.GET.get("live_price")
                prev_price = request.GET.get("prev_price")

                response = price_change(key, symbol, live_price, prev_price)


            elif ajxtype == "buy_stock":

                symbol = request.GET.get("symbol")

                expires = request.GET.get("expires")

                order_type = request.GET.get("order_type")

                share = request.GET.get("share")

                current_price = request.GET.get("current_price")

                limit_price = request.GET.get("limit_price")

                stock = StockNames.objects.get(symbol=symbol)

                current_date = datetime.datetime.now()

                remove_date = datetime.datetime.now()

                if request.user.is_authenticated:

                    user = UserDetails.objects.get(user=request.user)

                    identity = IdentityDetails.objects.get(id=user.identity.id)

                    user_buyingpower = float(user.identity.buyingpower)

                    if expires == "1":

                        expires_val = "Good for day"

                    else:

                        expires_val = "Good till canceled"

                    if order_type == "market_order":

                        transaction_obj, status = Transaction.objects.get_or_create(stockticker=stock,
                                                                                    ordertype=order_type,

                                                                                    price=current_price, size=share,

                                                                                    userid=request.user,
                                                                                    expires=expires_val)

                    else:

                        transaction_obj = Transaction.objects.create(stockticker=stock, ordertype=order_type,

                                                                     price=current_price, size=share,

                                                                     userid=request.user, expires=expires_val)

                    if expires != "1":
                        transaction_obj.remove_date = current_date + datetime.timedelta(days=90)

                        transaction_obj.save()

                    current_time = current_date.time()

                    flag = 0

                    print("current_time.hour  ", current_time.hour)

                    if int(current_time.hour) >= 9 and int(current_time.hour) < 15:

                        flag = 1

                    elif int(current_time.hour) == 15:

                        if int(current_time.minute) <= 30:
                            flag = 1

                    # elif int(current_time.hour) > 15 or int(current_time.hour) < 9:

                    #

                    #     flag = 1

                    if order_type == "market_order":

                        if flag == 1:

                            transaction_obj.status = "executed"

                            position_obj, status = Position.objects.get_or_create(userid=request.user, stockname=stock,

                                                                                  ticker=symbol,

                                                                                  price=current_price,
                                                                                  ordertype=order_type)

                            position_obj.transaction_details = transaction_obj

                            position_obj.save()

                            try:

                                history_obj = TransactionHistory.objects.get_or_create(position_obj=position_obj,
                                                                                       stock_number=share, status="buy")

                            except:

                                pass

                            # try:

                            total_cash = float(current_price) * int(share)

                            gl_history = GainLossHistory.objects.create(userid=request.user, stock=stock,
                                                                        total_cash=total_cash)

                            gl_history.unrealised_gainloss = num_quantize(

                                (float(current_price) - float(position_obj.transaction_details.price)) * int(share))

                            gl_history.position_obj = position_obj

                            gl_history.save()

                            user_buyingpower -= total_cash

                            identity.buyingpower = user_buyingpower

                            identity.save()

                            # except:

                            #     pass

                        else:

                            transaction_obj.status = "pending"


                    elif order_type == "limit_order":

                        transaction_obj.limit_price = limit_price

                    transaction_obj.save()


            elif ajxtype == "table_paginate":
                transaction_list = paginate_data(request)
                if transaction_list:
                    response['up_activity_html'] = render_to_string(
                        "includes/dashboard_includes/upcoming_activity.html", {
                            "transaction_list": transaction_list
                        })
                    response['tr_status'] = "True"

            elif ajxtype == "delete_transaction_data":
                Transaction.objects.get(id=request.GET.get("id")).delete()
                # position_obj_list = []
                # for position_obj in Position.objects.filter(userid=request.user):
                #     stock_obj = StockNames.objects.get(symbol=symbol)
                #     datas = stock_obj.history.history_json['data']
                #     data = {
                #         "date":position_obj.transaction_details.time,
                #         "ordertype":position_obj.ordertype,
                #         "size":position_obj.transaction_details.size,
                #         "price":position_obj.transaction_details.price,
                #         "current_price":datas.get("stock_price"),
                #         "gainloss":position_obj.unrealised_gainloss,
                #         "symbol":position_obj.ticker,
                #     }
                #     position_obj_list.append(data)

            elif ajxtype == "sell-stock":
                symbol = request.GET.get("symbol")
                share_num = int(request.GET.get("share_num"))
                current_price = si.get_live_price(symbol + ".NS")
                user_obj = UserDetails.objects.get(user=request.user)
                identity_obj = IdentityDetails.objects.get(id=user_obj.identity.id)
                buyingpower = float(identity_obj.buyingpower)
                for pos_obj in Position.objects.filter(userid=request.user, ticker=symbol).order_by("id"):
                    print("share_num    ", share_num)

                    stock_num = int(pos_obj.transaction_details.size)
                    print("stock_num    ", stock_num)

                    if stock_num == share_num:
                        stock_num -= share_num
                        pos_obj.transaction_details.size = stock_num
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=share_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                share_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,1111111111        buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()

                        except:
                            pass
                    elif stock_num > share_num:
                        # share_num = stock_num - share_num
                        stock_num -= share_num
                        pos_obj.transaction_details.size = stock_num
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=share_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                share_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,2222222222222    buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()
                        except Exception as e:
                            print("ERRORRRR  SELL STOCK  ", e)
                            pass
                        break
                    else:
                        share_num = share_num - stock_num
                        pos_obj.transaction_details.size = 0
                        pos_obj.transaction_details.save()
                        try:
                            history_obj = TransactionHistory.objects.get_or_create(position_obj=pos_obj,
                                                                                   stock_number=stock_num,
                                                                                   status="sell")
                        except:
                            pass
                        try:
                            realised_gainloss = (float(current_price) - float(pos_obj.transaction_details.price)) * int(
                                stock_num)
                            gl_obj = GainLossHistory.objects.get(position_obj=pos_obj)
                            gl_obj.realised_gainloss = num_quantize(realised_gainloss)
                            buyingpower += realised_gainloss
                            print(",,,,,,,,,,,,,,,,33333333333      buyingpower", buyingpower,
                                  num_quantize(realised_gainloss))
                            gl_obj.save()
                        except:
                            pass
                    print("===========share_num    ", share_num)
                    print("===========stock_num    ", stock_num)
                    # pos_obj.save()
                    if int(pos_obj.transaction_details.size) == 0:
                        print("###########    REMAINING SHARE    ", pos_obj.transaction_details.size)
                        pos_obj.delete()
                    print("BUYYYING POWERRRR   ", buyingpower)
                identity_obj.buyingpower = num_quantize(buyingpower)
                identity_obj.save()

        return render(request, self.template_name, context)


class StockSearchView(View):

    def get(self, request, *args, **kwargs):
        response = {}
        all_stocks = StockNames.objects.all()
        search_q = str(request.GET.get("symbol")).lower()
        stock_list = []
        for i in all_stocks:
            if search_q in i.symbol.lower() or search_q in i.name.lower():
                if i.symbol != "SYMBOL" and i.name != "NAME OF COMPANY":
                    stock_dict = {
                        "symbol": i.symbol,
                        "name": i.name
                    }
                    stock_list.append(stock_dict)
                    # limit += 1
            if len(stock_list) > 10:
                stock_list = stock_list[:10]
            response['stock_list'] = stock_list

        return HttpResponse(json.dumps(response), content_type="application/json")


class GetLatestGainLossView(View):

    def get(self, request, *args, **kwargs):
        response ={}
        current_date = datetime.datetime.now()
        current_time = current_date.time()
        flag = 0
        if int(current_time.hour) >= 9 and int(current_time.hour) < 15:
            flag = 1
        elif int(current_time.hour) == 15:
            if int(current_time.minute) <= 30:
                flag = 1
        if flag == 1:
            try:
                buyingpower = UserDetails.objects.get(user=request.user).identity.buyingpower
            except:
                buyingpower = 0

            try:
                gl_data = GainLossChartData.objects.get(userid=request.user).gainloss_data
                response['gainloss_val'] = round(
                    float(num_quantize(float(gl_data[-1][1]) + float(buyingpower))), 2)
                response['gl_status'] = True
            except:
                response['gainloss_val'] = 0.00
                response['gl_status'] = False
        else:
            response['gl_status'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")
