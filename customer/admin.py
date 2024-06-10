from django.contrib import admin

from customer.models import CustomerInbound, CustomerOutbound, CustomerReturns, CustomerExpiry, CustomerDamage, \
    CustomerTravelDistance, \
    CustomerInventory, CustomerPalletLocationAvailability, CustomerHSE, Customer

# Register your models here.


admin.site.register(Customer)
admin.site.register(CustomerInbound)
admin.site.register(CustomerOutbound)
admin.site.register(CustomerReturns)
admin.site.register(CustomerExpiry)
admin.site.register(CustomerDamage)
admin.site.register(CustomerTravelDistance)
admin.site.register(CustomerInventory)
admin.site.register(CustomerPalletLocationAvailability)
admin.site.register(CustomerHSE)
