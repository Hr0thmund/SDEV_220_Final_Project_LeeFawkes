from django.shortcuts import render, redirect
from django.template import engines
from django.conf import settings
from .forms import RoleSelectionForm, PlatformSelectionForm, CardSelectionForm, CoreParamsForm, MarketParamsForm, EdgeParamsForm
from .models import Role, Platform, ModularPlatform, FixedPlatform, Card

# Note - hardcoding these due to time constraints. Ideally I should probably add some attributes to my models to store these.
MAIN_TEMPLATES = {
    ('market', '7750_SR-2s'): 'configurator/market-7750.j2',
    ('market', '7750_SR-7s'): 'configurator/market-7750.j2',
    ('core', 'QFX5200'): 'configurator/core-qfx5200.j2',
    ('edge', 'MX10003'): 'configurator/edge-mx10003.j2'
}

CARD_TEMPLATES = {
    'LC2103': 'configurator/juniper-lc2103.j2',
    'XCM-7s': 'configurator/nokia_xcm-7s.j2',
    'XCM-2s': 'configurator/nokia_xcm-2s.j2'
}


def main_form(request):
    current_step = request.session.get('step', 'role')

    if request.method == 'POST':
        if current_step == 'role':
            form = RoleSelectionForm(request.POST)
            if form.is_valid():
                selected_role = form.cleaned_data['role']
                request.session['selected_role'] = selected_role.id
                request.session['step'] = 'platform'
                return redirect('main_form')

        elif current_step == 'platform':
            role_id = request.session.get('selected_role')
            role = Role.objects.get(pk=role_id)
            form = PlatformSelectionForm(request.POST, role=role)
            if form.is_valid():
                selected_platform = form.cleaned_data['platform']
                request.session['selected_platform'] = selected_platform.id
                # If modular, go to card selection; then hostname/loopback
                # If fixed, go directly to hostname/loopback
                if selected_platform.is_modular:
                    request.session['step'] = 'modular_cards'
                else:
#                    request.session['step'] = 'fixed_params'
                    # If fixed, we can skip directly to the final_params view
                    # which will prompt for parameters based on role/platform.
                    return redirect('final_params')
                return redirect('main_form')

        elif current_step == 'modular_cards':
            platform_id = request.session.get('selected_platform')
            platform = ModularPlatform.objects.get(pk=platform_id)
            form = CardSelectionForm(request.POST, platform=platform)
            if form.is_valid():
                slot_assignments = {}
                for slot_num in range(1, platform.num_slots + 1):
                    card_id = form.cleaned_data.get(f"slot_{slot_num}")
                    slot_assignments[slot_num] = int(card_id) if card_id else None
                request.session['slot_assignments'] = slot_assignments

                # After selecting cards on a modular platform, go to hostname/loopback form
#                request.session['step'] = 'modular_params'
                # After selecting cards on a modular platform, go directly to final_params
                return redirect('final_params')
                return redirect('main_form')

        elif current_step == 'modular_params':
            form = HostnameLoopbackForm(request.POST)
            if form.is_valid():
                request.session['hostname'] = form.cleaned_data['hostname']
                request.session['loopback'] = form.cleaned_data['loopback']
                request.session['step'] = 'summary'
                return redirect('main_form')

        elif current_step == 'fixed_params':
            form = HostnameLoopbackForm(request.POST)
            if form.is_valid():
                request.session['hostname'] = form.cleaned_data['hostname']
                request.session['loopback'] = form.cleaned_data['loopback']
                request.session['step'] = 'summary'
                return redirect('main_form')

        elif current_step == 'summary':
            if 'confirm' in request.POST:
                # Render final config
                return final_config_view(request)
                # print("User clicked confirm! Hooray!")
            if 'start_over' in request.POST:
                request.session.flush()
                return redirect('main_form')
    if current_step == 'generate_config':
        # We shouldn't be here. Probably stale session data, let's clear and restart.
        print("The value of current_step is", current_step)
        request.session.flush()
        return redirect('main_form')

    # GET requests:
    if current_step == 'role':
        form = RoleSelectionForm()
        return render(request, 'configurator/select_role.html', {'form': form})

    elif current_step == 'platform':
        role_id = request.session.get('selected_role')
        role = Role.objects.get(pk=role_id)
        form = PlatformSelectionForm(role=role)
        return render(request, 'configurator/select_platform.html', {'form': form, 'role': role})

    elif current_step == 'modular_cards':
        platform_id = request.session.get('selected_platform')
        platform = ModularPlatform.objects.get(pk=platform_id)
        form = CardSelectionForm(platform=platform)
        return render(request, 'configurator/modular_cards.html', {'form': form, 'platform': platform})

    elif current_step == 'modular_params':
        form = HostnameLoopbackForm()
        return render(request, 'configurator/hostname_loopback.html', {'form': form, 'modular': True})

    elif current_step == 'fixed_params':
        form = HostnameLoopbackForm()
        return render(request, 'configurator/hostname_loopback.html', {'form': form, 'modular': False})

    elif current_step == 'summary':
        role_id = request.session.get('selected_role')
        platform_id = request.session.get('selected_platform')
        role = Role.objects.get(pk=role_id)
        platform = Platform.objects.get(pk=platform_id)
        slot_assignments = request.session.get('slot_assignments', None)
        hostname = request.session.get('hostname', '')
        loopback = request.session.get('loopback', '')
        # Convert card IDs to card model names
        resolved_slot_assignments = {}
        for slot, card_id in slot_assignments.items():
            if card_id:
                card = Card.objects.get(pk=card_id)
                resolved_slot_assignments[slot] = card.model
            else:
                resolved_slot_assignments[slot] = "No Card"

        return render(request, 'configurator/summary.html', {
            'role': role,
            'platform': platform,
            'slot_assignments': resolved_slot_assignments,
            'hostname': hostname,
            'loopback': loopback
        })
        print("The value of current_step is", current_step)

def final_config_view(request):
    role_id = request.session.get('selected_role')
    platform_id = request.session.get('selected_platform')
    role = Role.objects.get(pk=role_id)
    platform = Platform.objects.get(pk=platform_id)
    slot_assignments = request.session.get('slot_assignments', {})
    hostname = request.session.get('hostname', '')
    loopback = request.session.get('loopback', '')
    resolved_slot_assignments = {}
    for slot, card_id in slot_assignments.items():
        if card_id:
            card = Card.objects.get(pk=card_id)
            resolved_slot_assignments[slot] = card.model
        else:
            resolved_slot_assignments[slot] = "No Card"

    context = {
        'role': role,
        'platform': platform,
        'slot_assignments': resolved_slot_assignments,
        'hostname': hostname,
        'loopback': loopback
    }

    jinja_env = engines['jinja2']  # ensure jinja2 is configured in settings.py
    template = jinja_env.get_template('configurator/final_config.j2')
    rendered_config = template.render(context)

    # Clear session after generating final config
    request.session.flush()

    return render(request, 'configurator/final.html', {'rendered_config': rendered_config})

def final_params(request):
    # Retrieve role and platform from session
    role_id = request.session.get('selected_role')
    platform_id = request.session.get('selected_platform')
    role = Role.objects.get(pk=role_id)
    platform = Platform.objects.get(pk=platform_id)

    # Determine which form to show based on role
    if request.method == 'POST':
        if 'start_over' in request.POST:
            # User clicked the start over button
            request.session.flush()
            return redirect('main_form')

        if role.name == 'market':
            form = MarketParamsForm(request.POST)
        elif role.name == 'core':
            form = CoreParamsForm(request.POST)
        elif role.name == 'edge':
            form = EdgeParamsForm(request.POST)
        else:
            # Default for error handling
            form = MarketParamsForm(request.POST) # fallback

        if form.is_valid():
            # Save the form data to session
            for field in form.cleaned_data:
                request.session[field] = form.cleaned_data[field]

            # Move on to a final "generate config" step
            request.session['step'] = 'generate_config'
            return redirect('generate_config')

    else:
        # GET request: show appropriate form
        if role.name == 'market':
            form = MarketParamsForm()
        elif role.name == 'edge':
            form = EdgeParamsForm()
        elif role.name == 'core':
            form = CoreParamsForm()
        else:
            form = MarketParamsForm()

    return render(request, 'configurator/final_params.html', {'form': form, 'role': role, 'platform': platform})


def generate_config(request):
    # Retrieve everything from session
    role_id = request.session.get('selected_role')
    platform_id = request.session.get('selected_platform')
    role = Role.objects.get(pk=role_id)
    platform = Platform.objects.get(pk=platform_id)

    jinja_env = engines['jinja2']

    # Select the main template based on role and platform model
    key = (role.name, platform.model)
    #This refers to the dictionary at the top of the file
    main_template_name = MAIN_TEMPLATES.get(key)
    if not main_template_name:
        # Handle unknown combination
        main_template_name = 'default_template.j2'  # fallback or raise an error

    # Gather parameters
    hostname = request.session.get('hostname', '')
    lo0_ip = request.session.get('lo0_ip', '')
    uplink_iface = request.session.get('uplink_iface', '')
    uplink_ip_cidr = request.session.get('uplink_ip_cidr', '')
    asn = request.session.get('asn', '')

    # slot_assignments: {slot_num: card_id or None}
    slot_assignments = request.session.get('slot_assignments', {})

    # Render main configuration snippet
    context = {
        'hostname': hostname,
        'lo0_ip': lo0_ip,
        'uplink_iface': uplink_iface,
        'uplink_ip_cidr': uplink_ip_cidr,
        'asn': asn
    }

    main_template = jinja_env.get_template(main_template_name)
    main_config = main_template.render(context)

    # Render card configurations
    # We assume `card_num` = slot_number - slot_index offset if necessary.
    # For simplicity, let's say card_num = slot_number directly.
    # If you need to adjust numbering, do so here.
    card_configs = []
    for slot, card_id in slot_assignments.items():
        if card_id:
            card = Card.objects.get(pk=card_id)
            card_template_name = CARD_TEMPLATES.get(card.model)
            if card_template_name:
                card_template = jinja_env.get_template(card_template_name)
                card_config = card_template.render({'card_num': slot})
                card_configs.append(card_config)

    # Combine all configs
    final_config = main_config + "\n" + "\n".join(card_configs)

    # Display the final configuration
    return render(request, 'configurator/final.html', {'rendered_config': final_config})






def clear_session_view(request):
    request.session.flush()
    return redirect('main_form')

