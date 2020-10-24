from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/stock-search/', views.StockSearchView.as_view(), name='stock_search'),
    path('dashboard/stocks/<str:stock_symbol>/', views.StockPageView.as_view(), name='stocks'),
    path('update-stock-data/', views.UpdateStockScheduler.as_view(), name='stock_schedule'),
    path('position-table/', views.PositionTablesDetailsView.as_view(), name='position_table'),
    path('latest-gain-loss/', views.GetLatestGainLossView.as_view(), name='top_gainers'),
    path('logout/', views.logout_user, name='logout')
    ]
