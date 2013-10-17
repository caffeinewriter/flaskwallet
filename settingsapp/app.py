from flask import Blueprint

from views import SettingDeleteView
from views import SettingEditView
from views import SettingListView


settingsapp = Blueprint(
    'settings',
    __name__,
    url_prefix='/settings',
    template_folder='templates/',
)

settingsapp.add_url_rule(
    '/list/',
    view_func=SettingListView.as_view('list')
)
settingsapp.add_url_rule(
    '/<string:name>/edit/',
    view_func=SettingEditView.as_view('edit')
)
settingsapp.add_url_rule(
    '/<string:name>/delete/',
    view_func=SettingDeleteView.as_view('delete')
)
