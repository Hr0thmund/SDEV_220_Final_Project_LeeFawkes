# run "python3 seed_db.py" to load db with test data
# run "python3 manage.py flush" to clear test data from db
# Note: this MVP hasn't implemented functionaly for sub-modules (like MDAs and PICs)
# It will assume a standard sub-module loadout for cards that feature that.

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webconf.settings')
django.setup()

from configurator.models import Role, Platform, ModularPlatform, FixedPlatform, Card

# FixedPlatform example: Juniper QFX5200
juniper_qfx5200 = FixedPlatform.objects.create(
    brand="Juniper",
    model="QFX5200",
    revision="R1",
    is_modular=False,
    num_ports=32,
    port_index=0,
    port_name_template="et-0/0/{{ port }}",
    speed_prefix_map={"100G": ""}
)

# ModularPlatform example: Juniper MX10003
juniper_mx10003 = ModularPlatform.objects.create(
    brand="Juniper",
    model="MX10003",
    revision="R1",
    is_modular=True,
    port_index=0,
    num_slots=2,
    slot_index=0
)

# Juniper MX10003 card:
juniper_lc2103 = Card.objects.create(
    brand="Juniper",
    model="LC2103",
    revision="1",
    is_supervisor=False,
    num_ports=12,
    port_name_template="et-{{ slot }}/1/{{ port }}",
    speed_prefix_map={"100G": "", "10G": ""}
)

# ModularPlatform for market (no hyphens in object names)
nokia_7750_sr2s = ModularPlatform.objects.create(
    brand="Nokia",
    model="7750_SR-2s",
    revision="1",
    is_modular=True,
    port_index=1,
    num_slots=2,
    slot_index=1
)

# Another 7750
nokia_7750_sr7s = ModularPlatform.objects.create(
    brand="Nokia",
    model="7750_SR-7s",
    revision="1",
    is_modular=True,
    port_index=1,
    num_slots=6,
    slot_index=1
)

# Card for Nokia 7750:
nokia_xcm7s = Card.objects.create(
    brand="Nokia",
    model="XCM-7s",
    revision="R1",
    is_supervisor=False,
    num_ports=36,
    port_name_template="{{ slot }}/1/{{ speedPrefix }}{{ port }}",
    speed_prefix_map={"100G": "c", "10G": ""}
)

# Another card for Nokia 7750:
nokia_xcm2s = Card.objects.create(
    brand="Nokia",
    model="XCM-2s",
    revision="R1",
    is_supervisor=False,
    num_ports=18,
    port_name_template="{{ slot }}/1/{{ speedPrefix }}{{ port }}",
    speed_prefix_map={"100G": "c", "10G": ""}
)

# Associate the cards with their platforms
nokia_xcm7s.supported_platforms.add(nokia_7750_sr2s)
nokia_xcm7s.supported_platforms.add(nokia_7750_sr7s)
nokia_xcm2s.supported_platforms.add(nokia_7750_sr2s)
nokia_xcm2s.supported_platforms.add(nokia_7750_sr7s)
juniper_lc2103.supported_platforms.add(juniper_mx10003)

nokia_7750_sr2s.supported_cards.add(nokia_xcm7s)
nokia_7750_sr2s.supported_cards.add(nokia_xcm2s)
nokia_7750_sr7s.supported_cards.add(nokia_xcm7s)
nokia_7750_sr7s.supported_cards.add(nokia_xcm2s)
juniper_mx10003.supported_cards.add(juniper_lc2103)

# Create Roles
edge_role = Role.objects.create(name="edge")
core_role = Role.objects.create(name="core")
market_role = Role.objects.create(name="market")

core_role.allowed_platforms.add(juniper_qfx5200)
edge_role.allowed_platforms.add(juniper_mx10003)
market_role.allowed_platforms.add(nokia_7750_sr2s)
market_role.allowed_platforms.add(nokia_7750_sr7s)
