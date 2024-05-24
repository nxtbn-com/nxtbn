from django.contrib import admin

from nxtbn.payment.models import PaymentSource, Payment

admin.site.register(PaymentSource)
admin.site.register(Payment)
