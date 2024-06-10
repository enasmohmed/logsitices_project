import django_tables2 as tables

from .models import Inbound, Outbound, Returns, Expiry, Damage, TravelDistance, Inventory, PalletLocationAvailability, \
    HSE


class NumberedTable(tables.Table):
    counter = tables.TemplateColumn('{{ row_counter|add:1 }}', orderable=False, verbose_name='#')

    class Meta:
        attrs = {'class': 'table'}


class InboundTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Inbound


class OutboundTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Outbound


class ReturnsTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Returns


class ExpiryTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Expiry


class DamageTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Damage


class TravelDistanceTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = TravelDistance


class InventoryTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = Inventory


class PalletLocationAvailabilityTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = PalletLocationAvailability


class HseTable(NumberedTable):
    class Meta(NumberedTable.Meta):
        model = HSE
