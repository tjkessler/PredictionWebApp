from ecnet import Server
from ecnet.data_utils import DataFrame
from ecnet.limit_parameters import output

import subprocess
import csv
import os
import shutil
import time

PADEL_PATH = 'app\\auto_predict\\PaDEL-Descriptor\\PaDEL-Descriptor.jar'


def run_babel_padel(smiles_filename):
    '''
    SMILES -> 3D model from Open Babel -> QSPR descriptors from PaDel
    Descriptor

    Args:
        smiles_filename (str): path to TXT file containing SMILES strings

    Returns:
        tuple: (3D model MDL filename, QSPR descriptors CSV filename)
    '''

    TIMESTAMP = str(time.time())
    MDL_FILENAME = '.\\app\\auto_predict\\processing\\mols_{}.mdl'.format(
        TIMESTAMP
    )
    DESC_FILENAME = '.\\app\\auto_predict\\processing\\desc_{}.csv'.format(
        TIMESTAMP
    )

    print('\nGenerating 3D MDL data from SMILES data...')
    subprocess.check_output(
        [
            'obabel',
            '-i',
            'smi',
            smiles_filename,
            '-o',
            'mdl',
            '-O',
            MDL_FILENAME,
            '--gen3D'
        ]
    )
    print('MDL generation complete.')

    def desc_gen():
        try:
            print('\nGenerating descriptors from 3D MDL data...')
            subprocess.check_output(
                [
                    'java',
                    '-jar',
                    PADEL_PATH,
                    '-2d',
                    '-3d',
                    '-detectaromaticity',
                    '-retainorder',
                    '-retain3d',
                    '-dir',
                    MDL_FILENAME,
                    '-file',
                    DESC_FILENAME
                ],
                timeout=15
            )
        except:
            desc_gen()
    desc_gen()

    print('Descriptor generation complete.')
    return (MDL_FILENAME, DESC_FILENAME)


def predict(project_file, db_new):
    '''
    Predicts CN for ECNet-formatted CSV database using specified ECNet project

    Args:
        project_file (str): path to ECNet project (.prj) file
        db_new (str): path to ECNet-formatted CSV database

    Returns:
        list: list of sublists with dimensionality equal to the number of
              target values
    '''

    print('\nPredicting property for new data...')
    sv = Server(project_file=project_file)
    output(DataFrame(db_new), sv.DataFrame.input_names, db_new)
    sv.import_data(db_new, sort_type='explicit')
    results = sv.use_model()
    print('Predictions complete')
    return results


def get_db_value(smiles, db_name):
    '''
    If SMILES code supplied by the user is in our database, return the
    experimental value

    Args:
        smiles (str): SMILES string of a user-supplied molecule
        db_name (str): path to an ECNet-formatted database

    Returns:
        list: experimental value(s) (depends on target point dimensionality),
              or ['N/A'] if not found
    '''

    df = DataFrame(db_name)
    for point in df.data_points:
        for string in point.strings:
            if smiles == string:
                return point.targets
    return ['N/A']


def get_test_set_error(project_file, error_fn):
    '''
    Obtains specified error for the test set used during model training

    Args:
        project_file (str): path to ECNet project (.prj) file
        error_fn (str): 'RMSE', 'r2', 'mean_abs_error', 'med_abs_error'

    Returns:
        float: error of test set using specified error function
    '''

    sv = Server(project_file=project_file)
    return(sv.calc_error(error_fn, dset='test'))[error_fn]


def cleanup(*argv):
    '''
    Deletes temporary files (MDL, CSV, etc.)

    Args:
        *argv: paths for files to delete
    '''

    for arg in argv:
        if os.path.isfile(arg):
            os.remove(arg)
        elif os.path.isdir(arg):
            shutil.rmtree(arg)


def make_db(smiles_filename, db_filename, desc_filename, remove_const=True):
    '''
    Creates an ECNet-formatted database from SMILES supplied by the user

    Args:
        smiles_filename (str): TXT file of SMILES strings
        db_filename (str): path to database created with this function
        desc_filename (str): path to CSV file containing QSPR descriptors
        remove_const (bool): if True, ignores QSPR descriptors with no
                             variation
    '''

    print('\nFormatting data for ECNet input...')

    def check_if_const_vals(iterator):
        iterator = iter(iterator)
        try:
            first = next(iterator)
        except StopIteration:
            return True
        return all(first == rest for rest in iterator)

    with open(desc_filename, newline='') as csvfile:
        desc_raw = csv.reader(csvfile)
        desc_raw = list(desc_raw)

    desc_rows = [[] for _ in range(len(desc_raw))]
    for desc in range(len(desc_raw[0]) - 1):
        desc_vals = [sublist[desc + 1] for sublist in desc_raw]
        if remove_const:
            if check_if_const_vals(desc_vals[1:]):
                continue
            else:
                for index, row in enumerate(desc_rows):
                    if index == 0:
                        row.append(desc_vals[index])
                    else:
                        try:
                            row.append(float(desc_vals[index]))
                        except:
                            row.append(0)
        else:
            for index, row in enumerate(desc_rows):
                if index == 0:
                    row.append(desc_vals[index])
                else:
                    try:
                        row.append(float(desc_vals[index]))
                    except:
                        row.append(0)

    with open(smiles_filename, 'r') as file:
        molecule_smiles = file.read()
    file.close()
    molecule_smiles = molecule_smiles.split('\n')
    if len(molecule_smiles[-1]) == 0:
        del(molecule_smiles[-1])

    ecnet_rows = []

    type_row = []
    type_row.append('DATAID')
    type_row.append('ASSIGNMENT')
    type_row.append('STRING')
    type_row.append('TARGET')
    for _ in range(len(desc_rows[0])):
        type_row.append('INPUT')
    ecnet_rows.append(type_row)

    title_row = []
    title_row.append('DATAID')
    title_row.append('ASSIGNMENT')
    title_row.append('SMILES')
    title_row.append('TARGET')
    for name in desc_rows[0]:
        title_row.append(name)
    ecnet_rows.append(title_row)

    for idx, mol in enumerate(molecule_smiles):
        mol_row = []
        mol_row.append(idx)
        mol_row.append('T')
        mol_row.append(mol)
        mol_row.append(0)
        for desc in desc_rows[idx + 1]:
            mol_row.append(desc)
        ecnet_rows.append(mol_row)

    with open(db_filename, 'w') as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL, lineterminator='\n')
        for row in ecnet_rows:
            wr.writerow(row)
    file.close()
    print('ECNet formatting complete.')
