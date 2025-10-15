# your_app/views.py

import datetime
from django.shortcuts import render
from django.urls import get_resolver, URLPattern

def eden_status_view(request):
    """
    Renders a cyberpunk-themed status page, dynamically listing all 
    available API endpoints.
    """
    # Dynamically discover all URL patterns in the project
    resolver = get_resolver()
    all_patterns = resolver.url_patterns

    # Filter for API endpoints, excluding the root path and admin
    api_endpoints = []
    for pattern in all_patterns:
        # Check if it's a direct URLPattern
        if isinstance(pattern, URLPattern):
            path = str(pattern.pattern)
            if path.startswith('api/'):
                # A simple heuristic to guess the primary method.
                # For more accuracy, you'd use DRF's router or inspect the view's allowed methods.
                view_name = pattern.name or ''
                if 'create' in view_name or 'add' in view_name:
                    method = 'POST'
                elif 'update' in view_name:
                    method = 'PUT'
                elif 'delete' in view_name:
                    method = 'DELETE'
                else:
                    method = 'GET'
                
                api_endpoints.append({'method': method, 'path': f'/{path}'})

    # Prepare context data for the template
    context = {
        'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S Z'),
        'api_endpoints': sorted(api_endpoints, key=lambda x: x['path']),
        'eden_art': """
███████╗██████╗ ███████╗███╗   ██╗
██╔════╝██╔══██╗██╔════╝████╗  ██║
█████╗  ██║  ██║█████╗  ██╔██╗ ██║
██╔══╝  ██║  ██║██╔══╝  ██║╚██╗██║
███████╗██████╔╝███████╗██║ ╚████║
╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝
""",
        'backend_art': """
██████╗ █████╗  ███████╗██╗   ██╗███████╗███╗   ██╗██████╗ 
██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║██╔══██╗
██████╔╝███████║█████╗  ███████║█████╗  ██╔██╗ ██║██║  ██║
██╔══██╗██╔══██║██╔══╝  ██╔══██║██╔══╝  ██║╚██╗██║██║  ██║
██████╔╝██║  ██║███████╗██║   ██║███████╗██║ ╚████║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ 
"""
    }

    return render(request, 'your_app/status.html', context)