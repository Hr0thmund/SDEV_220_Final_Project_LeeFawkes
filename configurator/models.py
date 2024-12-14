from django.db import models

# For this MVP, we will assume all ports run at their native speeds -
# for example, QSFP56-DD ports are 400Gbe, we're not inserting QSFP28 optics.
# We also assume that no breakouts will be used. That's a whole can of worms.
# The various "index" fields are to account for differences in the way platforms count slots and ports.
# Juniper counts from 0, Nokia counts from 1, Cisco varies by platform

class Role(models.Model):
    # This class represents the role the device will serve in the network - core, aggregation, etc.
    name = models.CharField(max_length=100, unique=True)
    allowed_platforms = models.ManyToManyField('Platform', related_name='roles')

    def __str__(self):
        return self.name

class Platform(models.Model):
    # The device platform. IE, Cisco ASR-9910 V02
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    revision = models.CharField(max_length=100, blank=True, null=True)
    is_modular = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.model} (rev: {self.revision})"

class ModularPlatform(Platform):
    # For the case in Platform where is_modular == True
    num_slots = models.IntegerField(default=0)
    supported_cards = models.ManyToManyField('Card', related_name='supported_by_platforms', blank=True)
    slot_index =  models.IntegerField(default=0)

    def __str__(self):
        return f"Modular: {super().__str__()} with {self.num_slots} slots"

class FixedPlatform(Platform):
    # For the case in Platform where is_modular == False
    # port_name_template is mandatory, and is populated with a snippet of Jinja2 template.
    port_index = models.IntegerField(default=0)
    port_name_template = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"Fixed: {super().__str__()} starting port index: {self.port_index}"

class Card(models.Model):
    # Inventory item for modular platforms. IE Cisco A9K-20HG-FLEX-SE V04
    # TODO: Implement sub-modules, like PICs and MDAs
    # For this MVP, we will assume a standard module loadout, like MIC1 in the Juniper LC2103
    # port_name_template is mandatory, and is populated with a snippet of Jinja2 template.
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    revision = models.CharField(max_length=100, blank=True, null=True)
    is_supervisor = models.BooleanField(default=False)
    port_index = models.IntegerField(default=0) 
    port_name_template = models.TextField(blank=False, null=False)
    supported_platforms = models.ManyToManyField(Platform, related_name='supported_cards')

    # Speed-to-prefix map. For example:
    # {"100G": "Hu", "10G": "Te"} for Cisco,
    # {"100G": "c", "10G": ""} for Nokia.
    speed_prefix_map = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model} (rev: {self.revision})"


class SlotInventory(models.Model):
    # Objects of this type will be instantiated as the user populates cards in the form
    modular_platform = models.ForeignKey(ModularPlatform, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.IntegerField(unique=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.modular_platform} Slot {self.slot_number}: {self.card}"

