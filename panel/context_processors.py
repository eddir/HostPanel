from HostPanel.settings import VERSION, PANEL_VERSION, CARETAKER_VERSION, MYSQL_VERSION


def version(request):
    return {
        'VERSION': VERSION,
        'PANEL_VERSION': PANEL_VERSION,
        'CARETAKER_VERSION': CARETAKER_VERSION,
        'MYSQL_VERSION': MYSQL_VERSION
    }
