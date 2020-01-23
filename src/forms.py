from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SubmitMoleculeForm(FlaskForm):
    '''Flask form for submitting SMILES strings'''

    smiles = StringField(
        'Enter SMILES string:',
        validators=[DataRequired()]
    )
    prop = SelectField(u'Fuel Property', choices=[
        ('cn', 'Cetane Number'),
        ('cp', 'Cloud Point'),
        ('kv', 'Kinematic Viscosity'),
        ('pp', 'Pour Point'),
        ('ysi', 'Yield Sooting Index')
    ], default='cn')
    submit = SubmitField('Predict Property')
