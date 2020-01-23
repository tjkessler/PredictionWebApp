from src import app
from src.forms import SubmitMoleculeForm
from flask import render_template, flash, redirect, request, url_for
from ecpredict import cetane_number, cloud_point, kinematic_viscosity,\
    pour_point, yield_sooting_index


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    form = SubmitMoleculeForm()
    if form.validate_on_submit():
        allowed_chars = [
            'C', 'c', 'h', 'H',
            'N', 'n', 'Na', 'na',
            'O', 'o', 'B', 'b',
            'P', 'p', 'Cl', 'cl',
            'Br', 'br', 'I', 'i',
            '.', '-', '=', '#',
            '$', ':', '/', '\\',
            '(', ')'
        ]
        for char in range(0, len(form.smiles.data)):
            if form.smiles.data[char] not in allowed_chars:
                try:
                    if int(form.smiles.data[char]):
                        continue
                except:
                    try:
                        if form.smiles.data[char] + form.smiles.data[char+1]\
                                not in allowed_chars:
                            flash('Invalid SMILES format')
                            return redirect(url_for('index'))
                        else:
                            continue
                    except:
                        flash('Invalid SMILES character: {}'.format(char))
                        return redirect(url_for('index'))
        if form.prop.data == 'cn':
            pred_fn = cetane_number
        elif form.prop.data == 'cp':
            pred_fn = cloud_point
        elif form.prop.data == 'kv':
            pred_fn = kinematic_viscosity
        elif form.prop.data == 'pp':
            pred_fn = pour_point
        elif form.prop.data == 'ysi':
            pred_fn = yield_sooting_index
        else:
            raise ValueError('Unknown property: {}'.format(form.prop.data))
        prediction, err = pred_fn([form.smiles.data])
        flash('Predicted {}: %.02f '.format(form.prop.data.upper())
              % prediction[0] + u'\u00B1' + ' %.02f' % err)
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)
