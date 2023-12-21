from django.urls import path,re_path
from ..views import *

app_name = 'src'
urlpatterns = [
    # cron jobs 
    path('cron/user-day-out', cron.userDayOut),
    path('cron/update-scheme-order-table', cron.updateSchemeOrderTable),
    path('cron/update-order-details-table', cron.updateOrderDetailsTable),
    
    path('api/login', auth.login),
    path('api/logout', auth.logout),
    path('api/update-user-profile', auth.updateUserProfile),
    path('api/update-user-location', auth.updateUserLocation),
    path('api/update-user-password', auth.updateUserPassword),
    path('api/product-list', order.productList),
    path('api/product-variant-list', order.productVariantList),
    path('api/product-variant-lists', order.productVariantLists),
    path('api/save-order', order.saveOrder),
    path('api/order-details', order.orderDetails),
    path('api/order-list', order.orderList),
    path('api/update-order', order.updateOrder),
    path('api/save-grievance', order.saveGrievance),
    path('api/order-scheme-list', order.orderSchemeList),
    path('api/user-order-list', order.userOrderList),
    path('api/check-attendance', auth.checkAttendance),
    path('api/user-attendance', auth.userAttendance),
    path('api/user-locations', auth.userLocations),
    path('api/user-list', auth.userList),
    path('api/untagged-user-list', auth.unTaggedUserList),
    path('api/save-user', auth.saveUser),
    path('api/save-user-tagging', auth.saveUserTagging),
    path('api/save-tracking-data', auth.saveUserTracking),

    path('api/payment-collection', auth.paymentCollection),
    path('api/search-user-list', auth.searchUserList),
    path('api/user-details', auth.userDetails),
    path('api/update-users-profile', auth.updateUsersProfile),
    path('api/get-master-data', auth.getMasterData),
    path('api/applied-leaves', auth.appliedLeaves),
    path('api/apply-leave', auth.applyLeave),
    path('api/user-dashboard-data', auth.userDashboardData),

    path('api/search-customer', order.customerlist),
    path('api/product-with-product-variant', order.productWithProductVariant),
    path('api/free-of-cost', order.freeOfCost),
    path('api/foc-request-list', order.focRequestList),
    path('api/apply-leave', auth.applyLeave),
    
    path('api/get-user-order-list', crate.getUserOrderList),
    path('api/send-otp', crate.sendOtp),
    path('api/dispatch-crates', crate.dispatchCrates),
    path('api/get-user-list', crate.getUserList),
    path('api/received-crates', crate.receivedCrates),
    path('api/get-user-vehicle-list', crate.getUserVehicleList),

    path('api/user-dashboard-details', order.userDashboardDetails),
    path('api/user-crate-ledger', order.userCrateLedger),

    path('api/notification-list', order.notificationList),
    path('api/approval-list', order.approvalList),
    path('api/update-approval-status', order.updateApprovalStatus),
]