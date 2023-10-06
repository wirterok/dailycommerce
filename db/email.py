from django.conf import settings
from db.local_settings.models import Languages, EmailTemplate
from db.settings.models import SMTP
from jinja2 import Template
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from db.local_settings import EmailTemplates
from django.core.mail import get_connection


class EmailManager:
    def __init__(self, tenant_id, template_name, user):
        self.tenant_id = tenant_id
        self.template_name = template_name
        self.user = user
        self.title = self._get_title(template_name)

    def _get_title(self, name):
        for data in EmailTemplates.TemplatesChoices:
            if data[0] == name:
                return data[1]
        
    def set_connection(self):
        smtp = SMTP.objects.filter(tenant_id=self.tenant_id)
        if smtp.exists():
            credentials = smtp.first()
            return get_connection(
                host=credentials.host,
                port=credentials.port,
                username=credentials.user,
                password=credentials.password
            )
        
        return get_connection()

    def get_html(self, data):
        lang = "EN"
        if user_lang := self.user.lang:
            if Languages.objects.filter(locale=user_lang).exists():
                lang = user_lang
        
        try: 
            template_instance = EmailTemplate.objects.get(template=self.template_name, lang=lang)
            template = Template(template_instance.html)
            html = template.render(**data)
        except:
            html = render_to_string(f"email/{lang}/{self.template_name}.html", data)

        return html
    
    def send(self, template_data, to_user: list, title=None, from_user=None):
        connection = self.set_connection()
        html = self.get_html(template_data)
        if title:
            self.title = title
        from_usr = from_user if from_user else settings.DEFAULT_FROM_EMAIL
        msg = EmailMessage(
            self.title,
            html,
            from_user,
            to_user,
            connection=connection,
        )
        msg.send(fail_silently=False)


            

        

        
        