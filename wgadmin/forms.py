from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import Optional, NumberRange, Length

class InterfaceSearchForm(FlaskForm):
    class Meta:
        csrf = False
    query = StringField("Search")


class InterfaceInfoForm(FlaskForm):
    public_key = StringField("Public Key")
    host = StringField("Hostname",
                       validators=(Length(max=128),),
                       render_kw={"placeholder": "my-pc"})
    name = StringField("Interface Name",
                       validators=(Length(max=16),),
                       render_kw={"placeholder": "wg0"})
    description = StringField("Description",
                              validators=(Length(max=1024),))
    listen_port = IntegerField("Listen Port",
                               validators=(Optional(),NumberRange(0, (2**16)-1)),
                               render_kw={"placeholder": "51820"})
    persistent_keepalive = IntegerField("Persistent Keepalive",
                                        validators=(Optional(),NumberRange(0, (2**16)-1)))
    endpoint = StringField("Endpoint",
                           validators=(Length(max=253),),
                           render_kw={"placeholder": "example.com:51820"})
    linkable = BooleanField("Linkable", default=False)
    enabled = BooleanField("Enabled", default=True)
