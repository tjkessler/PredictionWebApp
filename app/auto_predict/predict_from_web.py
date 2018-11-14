from app.auto_predict import functions
from app.email import send_results
import time

PROJECT_NAME = '.\\app\\auto_predict\\processing\\cn_model_v5.5.6'
DB_NAME = '.\\app\\auto_predict\\processing\\cn_model_v5.5.csv'


def predict(email, form_data):
    '''
    Predicts CN from SMILES string, emails results to user

    Args:
        email (str): email address of user
        form_data (str): SMILES strings, one per line (separeted by \n)
    '''

    TIMESTAMP = str(time.time())
    SMILES_FILE = '.\\app\\auto_predict\\processing\\mols_{}.smiles'.format(
        TIMESTAMP
    )
    NEW_DB_FILE = '.\\app\\auto_predict\\processing\\mols_db_{}.csv'.format(
        TIMESTAMP
    )

    form_data = form_data.split('\n')
    with open(SMILES_FILE, 'w') as smilesfile:
        for idx, mol in enumerate(form_data):
            mol = mol.replace('\n', '').replace('\r', '')
            if mol != '':
                smilesfile.write(mol)
                smilesfile.write('\n')

    MDL_FILENAME, DESC_FILENAME = functions.run_babel_padel(SMILES_FILE)
    functions.make_db(
        SMILES_FILE,
        NEW_DB_FILE,
        DESC_FILENAME,
        remove_const=False
    )
    results = functions.predict(PROJECT_NAME, NEW_DB_FILE)
    db_vals = []
    for mol in form_data:
        mol = mol.replace('\n', '').replace('\r', '')
        if mol != '':
            db_vals.append(
                functions.get_db_value(
                    mol,
                    DB_NAME
                )
            )
    rmse = float(functions.get_test_set_error(PROJECT_NAME, 'rmse')[0])
    mae = float(functions.get_test_set_error(PROJECT_NAME, 'med_abs_error')[0])
    functions.cleanup(
        SMILES_FILE,
        NEW_DB_FILE,
        MDL_FILENAME,
        DESC_FILENAME
    )
    formatted_results = []
    for idx, result in enumerate(results[0]):
        one_result = []
        one_result.append(form_data[idx].replace('\r', ''))
        one_result.append(round(result[0], 2))
        one_result.append(db_vals[idx][0])
        formatted_results.append(one_result)
    send_results(email, formatted_results, round(rmse, 2), round(mae, 2))
