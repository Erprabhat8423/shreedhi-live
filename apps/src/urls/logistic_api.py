from django.urls import path,re_path
from ..views.api.logistic_api import *

urlpatterns = [
    path('api/logistic/login', login),
    path('api/logistic/get-master-data', getMasterData),
    path('api/logistic/dashboard-details', dashboardDetails),
    path('api/logistic/today-orders', todayOrders),
    path('api/logistic/save-tracking-data', saveTracking),
    path('api/logistic/send-order-otp', sendOrderOtp),
    path('api/logistic/deliver-order', deliverOrder),
    path('api/logistic/get-user-list', getUserList),
    path('api/logistic/send-otp', sendOtp),
    path('api/logistic/send-approval-request', sendApprovalRequest),
    path('api/logistic/receive-crates', receiveCrates),

    path('api/logistic/notification-list', notificationList),

]