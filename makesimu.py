#!/usr/bin/env python

import pybars
import os
import subprocess
from utils import name_converter, OASIS_fieldManager,manageCouplingFlag
from munch import munchify
import yaml
import shutil


def submitMakesimu():
    os.chdir('out')
    print (os.path.join(os.getcwd(), 'namelist_cfg_template.tmpl'))
    subprocess.call('chmod +x makesimu.sh', shell=True)
    subprocess.call('bash makesimu.sh', shell=True)


def setEXP(conf):
    os.makedirs('out', exist_ok=True)
    os.makedirs('templates',exist_ok=True)
    os.makedirs('out/tmp', exist_ok=True)
    oasis_fields= OASIS_fieldManager(conf)
    coupling_data=manageCouplingFlag(conf)
    data = {'experiment_name': os.getcwd().split('/')[-2],
            'start_date': conf.start_date,
            'end_date': conf.end_date,
            'reference_experiment': conf.models.nemo.reference_experiment,
            'simu_lenght': conf.models.simu_lenght,
            'timestep_o': conf.models.nemo.timestep,
            'jday': conf.paths.jday,
            'base': conf.paths.base,
            'domain': conf.files.nemo.domain,
            'initTemp': conf.files.nemo.initTemp,
            'initSal': conf.files.nemo.initSal,
            'viscosity': conf.files.nemo.viscosity,
            'diffusivity': conf.files.nemo.diffusivity,
            'runoff': conf.files.nemo.runoff,
            'paral_queue': conf.paral_queue,
            'serial_queue': conf.serial_queue,
            'cores_o': conf.models.nemo.cores,
            'atm_forcings_o': conf.files.nemo.atm_forcings.path,
            'atm_forcings_weights_bil': conf.files.nemo.atm_forcings.bil_weight,
            'atm_forcings_weights_bic': conf.files.nemo.atm_forcings.bic_weight,
            'mod_def': conf.files.ww3.mod_def,
            'atm_forcings_w':conf.files.ww3.atm_forcings,
            'ww3_exe': conf.models.ww3.exe,
            'timestep_w': conf.models.ww3.timestep,
            'r_ww3':conf.files.oasis.r_ww3,
            'r_nemo':conf.files.oasis.r_nemo,
            'grids':conf.files.oasis.grids,
            'masks':conf.files.oasis.masks,
            'outputs_w':conf.models.ww3.outputs,
            'hydro_fields': ' '.join(conf.coupling_fields.hydro),
            'wave_fields': ' '.join(conf.coupling_fields.wave),
            'coupling_freq': conf.models.coupling_frequency,
            'runtime': 3600* int(conf.models.simu_lenght)*24,
            'oceancores':conf.models.nemo.cores,
            'wavecores':conf.models.ww3.cores,
            'oasiscores': int(conf.models.nemo.cores)+int(conf.models.ww3.cores),
            'x_size': conf.models.x_size,
            'y_size': conf.models.y_size,
            'ww3_output_tot': int(conf.models.simu_lenght)*24,
            'rmp_ww3': conf.files.oasis.rmp_ww3_2_nem,
            'rmp_nemo': conf.files.oasis.rmp_nem_2_ww3,
            'oasis_nfields': oasis_fields.n,
            'namcouple_fields': oasis_fields.fillNAMCOUPLE(),
            }
    data={**data, **coupling_data}
    compiler = pybars.Compiler()

    listTemplates = [f for f in os.listdir('templates') if not f.startswith('.')]
    listTemplates.append('namcouple.base')
    [fillTemplate(tmpl, data, compiler) for tmpl in listTemplates]
    shutil.copy(os.path.join(os.getcwd(),'out', 'namcouple'), os.path.join(os.getcwd(),'out','tmp', 'namcouple'))


def submitEXP():
    try:
        shutil.rmtree('../../tmp')
    except:
        pass
    shutil.move(os.path.join(os.getcwd(), 'tmp'), '../../tmp')
    os.chdir('../../tmp')
    subprocess.call('bsub < Job_EXP_1', shell=True)


def fillTemplate(tmpl, data, compiler):
    print('compiling template %s' % tmpl)
    with open(os.path.join('templates', tmpl), 'r') as s:
        print (tmpl)
        template = compiler.compile(s.read())
        outTmpl = template(data)
        tmplName = tmpl.split('.')[0]
        if tmplName == 'makesimu':
            tmplName = tmplName + ".sh"
        elif tmplName in ['ww3_shel','ww3_ounf']:
            tmplName = tmplName + ".inp"
        elif tmplName=='namcouple':
            if tmpl.split('.')[1]=='tmpl':
                print ('namcouple')
                tmplName = tmplName + ".base"
                outputFile = open(os.path.join('templates', tmplName), "w")
                [outputFile.write(str(line)) for line in outTmpl]
                outputFile.close()
                return

        outputFile = open(os.path.join('out', tmplName), "w")
        [outputFile.write(str(line)) for line in outTmpl]
        outputFile.close()


def getConfigurationByID(path):
    globalConf = yaml.safe_load(open(os.path.join(path, "conf.yaml")))
    return munchify(globalConf['conf'])


def main():
    conf = getConfigurationByID(os.getcwd())


    setEXP(conf)
    submitMakesimu()
    submitEXP()


main()
