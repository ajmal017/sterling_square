
from django import template
from accounts.models import StockHistory
from accounts.views import num_quantize

register = template.Library()



@register.simple_tag
def get_type_text(order_type):
    print("order_type    ",order_type)
    value = ""
    if str(order_type) == "limit_order":
        value = "limit buy"
    elif str(order_type) == "market_order":
        value = "market order"
    return value


@register.simple_tag
def get_stock_price(symbol):
    from yahoo_fin import stock_info as si
    try:
        return round(si.get_live_price(symbol + ".NS"), 2)
    except:
        return None

@register.simple_tag
def get_stock_name(symbol):
    try:
        stock_data_json = StockHistory.objects.get(stock__symbol=symbol).history_json.get("data")
        return stock_data_json.get("stockname")
    except:
        return None

@register.simple_tag
def check_pos_or_neg(pos_obj):
    if pos_obj.gl_history_position_rel.all():
        gainloss = pos_obj.gl_history_position_rel.all()[0].unrealised_gainloss
    else:
        gainloss = 0.00
    # if float(value) > 0:
    #     value = "+"+value
    # else:
    #     value = "-" + value
    return gainloss

@register.simple_tag
def get_amount(price,share_num):
    print("PRICEEEE   ",price,share_num)
    if price and share_num:
        return num_quantize(float(price)*int(share_num))
    else:
        return price
