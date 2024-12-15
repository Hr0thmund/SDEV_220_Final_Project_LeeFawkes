from django.shortcuts import render, redirect
from django.template import engines
from .forms import RoleSelectionForm, PlatformSelectionForm, CardSelectionForm, HostnameLoopbackForm
from .models import Role, Platform, ModularPlatform, FixedPlatform, Card

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
                    request.session['step'] = 'fixed_params'
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
                request.session['step'] = 'modular_params'
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
            # If another action (like start over) was implemented, handle here
            if 'start_over' in request.POST:
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

        return render(request, 'configurator/summary.html', {
            'role': role,
            'platform': platform,
            'slot_assignments': slot_assignments,
            'hostname': hostname,
            'loopback': loopback
        })

def final_config_view(request):
    role_id = request.session.get('selected_role')
    platform_id = request.session.get('selected_platform')
    role = Role.objects.get(pk=role_id)
    platform = Platform.objects.get(pk=platform_id)
    slot_assignments = request.session.get('slot_assignments', {})
    hostname = request.session.get('hostname', '')
    loopback = request.session.get('loopback', '')

    context = {
        'role': role,
        'platform': platform,
        'slot_assignments': slot_assignments,
        'hostname': hostname,
        'loopback': loopback
    }

    jinja_env = engines['jinja2']  # ensure jinja2 is configured in settings.py
    template = jinja_env.get_template('configurator/final_config.j2')
    rendered_config = template.render(context)

    # Clear session after generating final config if desired
    request.session.flush()

    return render(request, 'configurator/final.html', {'rendered_config': rendered_config})

def clear_session_view(request):
    request.session.flush()
    return redirect('main_form')

