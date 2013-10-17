from flask import flash
from flask import url_for
from flask import redirect
from flask import render_template
from flask import request
from flask.views import View

from flaskwallet import session

from models import Setting
from settingsapp.forms import EditForm


class SettingListView(View):
    methods = ['GET', 'POST']
    def dispatch_request(self):
        settings = Setting.query.filter(Setting.name != 'otpsecret').all()
        form = EditForm(request.form)
        if request.method == 'POST' and form.validate():
            setting = Setting(form.name.data, form.value_decrypted.data)
            session.add(setting)
            session.commit()
            return redirect(url_for('settings.list'))
        return render_template('settings/list.html', settings=settings,
                               form=form)


class SettingEditView(View):
    methods = ['GET', 'POST']
    def dispatch_request(self, name):
        setting = Setting.query.get(name)
        form = EditForm(request.form, setting)
        if request.method == 'POST' and form.validate():
            form.populate_obj(setting)
            session.commit()
            return redirect(url_for('settings.list'))
        return render_template('settings/edit.html', form=form, setting=setting)


class SettingDeleteView(View):
    methods = ['POST']
    def dispatch_request(self, name):
        setting = Setting.query.filter(Setting.name==name).first()
        session.delete(setting)
        session.commit()
        flash(u"%s: Setting deleted" % name, 'success')
        return redirect(url_for("settings.list"))
