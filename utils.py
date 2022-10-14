
name_converter = {}
name_converter['CUR'] = {}
name_converter['SSH'] = {}
name_converter['OCDN'] = {}
name_converter['T0M1'] = {}
name_converter['OCHA'] = {}
name_converter['OHS'] = {}
name_converter['DIR'] = {}
name_converter['BHD'] = {}
name_converter['TWO'] = {}
name_converter['UBR'] = {}
name_converter['FOC'] = {}
name_converter['TAW'] = {}
name_converter['TUS'] = {}
name_converter['USS'] = {}
name_converter['LM'] = {}
name_converter['DRY'] = {}

name_converter['TAW']['ww3'] = ['WW3_TAWX', 'WW3_TAWY']
name_converter['TAW']['nemo'] = ['O_Tawx', 'O_TawY']

name_converter['OCHA']['ww3'] = 'WW3_OCHA'
name_converter['OCHA']['nemo'] = 'O_Charn'

name_converter['TWO']['ww3'] = ['WW3_TWOX', 'WW3_TWOY']
name_converter['TWO']['nemo'] = ['O_Twox', 'O_Twoy']

name_converter['OCDN']['ww3'] = 'WW3_OCDN'
name_converter['OCDN']['nemo'] = 'O_WDrag'

name_converter['FOC']['ww3'] = 'WW3__FOC'
name_converter['FOC']['nemo'] = 'O_PhiOce'

name_converter['USS']['ww3'] = ['WW3_USSX', 'WW3_USSY']
name_converter['USS']['nemo'] = ['O_Sdrfx', 'O_Sdrfy']

name_converter['T0M1']['ww3'] = 'WW3_T0M1'
name_converter['T0M1']['nemo'] = 'O_WPer'

name_converter['OHS']['ww3'] = 'WW3__OHS'
name_converter['OHS']['nemo'] = 'O_Hsigwa'

name_converter['BHD']['ww3'] = 'WW3__BHD'
name_converter['BHD']['nemo'] = 'O_Bhd'

name_converter['TUS']['ww3'] = ['WW3_TUSX', 'WW3_TUSY']
name_converter['TUS']['nemo'] = ['O_Tusd', 'O_Tvsd']

name_converter['CUR']['ww3'] = ['WW3_OSSU', 'WW3_OSSV']
name_converter['CUR']['nemo'] = ['O_OCurxw', 'O_OCuryw']

name_converter['SSH']['ww3'] = 'WW3__SSH'
name_converter['SSH']['nemo'] = 'O_Wlevel'


class OASIS_fieldManager():
    def __init__(self,conf,ways=1):
        """
        :param conf: configuration files
        :param ways: if set to 1=> one-way coupling , if set to 2 => two-ways coupling
        """
        self.ways=ways
        self.conf=conf
        self.fieldsCounter()

    def ww3_field(self,field,nemo_name,ww3_name):
        return f"# Field : {field} WW3 -> NEMO\n"\
        "# ~~~~~~~~~~~\n"\
        f"{nemo_name} {ww3_name} 1 "\
        "{{coupling_freq}} 2 r_nemo.nc EXPORTED\n"\
        "{{x_size}} {{y_size}} {{x_size}} {{y_size}} nemt ww3t LAG=+{{timestep_o}}\n"\
        "R  0  R  0\n"\
        "LOCTRANS SCRIPR\n"\
        "AVERAGE\n"\
        "DISTWGT LR SCALAR LATLON 1 8\n#"

    def nemo_field(self,field,nemo_name,ww3_name):
        return f"# Field : {field} NEMO -> WW3\n"\
        "# ~~~~~~~~~~~\n"\
        f"{ww3_name} {nemo_name} 1 "\
        "{{coupling_freq}} 2 r_ww3.nc EXPORTED\n"\
        "{{x_size}} {{y_size}} {{x_size}} {{y_size}} nemt ww3t LAG=+{{timestep_w}}\n"\
        "R  0  R  0\n"\
        "LOCTRANS SCRIPR\n"\
        "AVERAGE\n"\
        "DISTWGT LR SCALAR LATLON 1 8\n#"

    def fillNAMCOUPLE(self):
        buffer=[]
        if isinstance(self.conf.coupling_fields.hydro,list):
            for field in self.conf.coupling_fields.hydro:
                oasis_name=name_converter[field]
                print (field)
                print (oasis_name)
                if isinstance(oasis_name['nemo'],list):
                    for i,fn in enumerate(oasis_name['nemo']):
                        buffer.append(self.nemo_field(field,fn,oasis_name['ww3'][i]))
                else:
                    buffer.append(self.nemo_field(field,oasis_name['nemo'], oasis_name['ww3']))
        else:
            field=self.conf.coupling_fields.hydro
            oasis_name = name_converter[field]
            if isinstance(oasis_name['nemo'], list):
                for i, fn in enumerate(oasis_name['nemo']):
                    buffer.append(self.nemo_field(field, fn, oasis_name['ww3'][i]))
            else:
                buffer.append(self.nemo_field(field, oasis_name['nemo'], oasis_name['ww3']))

        if self.ways>1:
            if isinstance(self.conf.coupling_fields.wave,list):
                for field in self.conf.coupling_fields.wave:
                    oasis_name = name_converter(field)
                    if isinstance(oasis_name['nemo'], list):
                        for i, fn in enumerate(oasis_name['nemo']):
                            buffer.append(self.nemo_field(field, fn, oasis_name['ww3'][i]))
                    else:
                        buffer.append(self.nemo_field(field, oasis_name['nemo'], oasis_name['ww3']))
            else:
                field=self.conf.coupling_fields.wave
                oasis_name = name_converter(field)
                if isinstance(oasis_name['nemo'], list):
                    for i, fn in enumerate(oasis_name['nemo']):
                        buffer.append(self.nemo_field(field, fn, oasis_name['ww3'][i]))
                else:
                    buffer.append(self.nemo_field(field, oasis_name['nemo'], oasis_name['ww3']))
        return '#\n'.join(buffer)

    def fieldsCounter(self):
        """
        :param conf:
        :return: number of field for oasis.
        """
        n=0
        if isinstance(self.conf.coupling_fields.hydro,list):
            for f in self.conf.coupling_fields.hydro:
                if f in ['OCDN', 'T0M1', 'OCHA', 'OHS', 'DIR', 'BHD', 'FOC', 'LM']:
                    n+=1
                elif f in ['TAW','TWO', 'TUS','USS' ]:
                    n+=2
        else:
            if self.conf.coupling_fields.hydro in ['OCDN', 'T0M1', 'OCHA', 'OHS', 'DIR', 'BHD', 'FOC', 'LM']:
                n += 1
            elif self.conf.coupling_fields.hydro in ['TAW', 'TWO', 'TUS', 'USS']:
                n += 2

            if self.ways>1:
                if isinstace(self.conf.coupling_fields.wave,list):
                    for f in self.conf.coupling_fields.wave:
                        if f =='SSH':
                            n+=1
                        elif f=='CUR':
                            n+=2
                else:
                    if  self.conf.coupling_fields.wave =='SSH':
                        n+=1
                    elif  self.conf.coupling_fields.wave=='CUR':
                        n+=2
        self.n=n

def manageCouplingFlag(conf):
    data={
    'sd': conf.coupling_physics.stokes_drift,
    'sc': conf.coupling_physics.stokes_coriolis,
    'sdt': conf.coupling_physics.stokes_transport,
    'vf': conf.coupling_physics.vortex_force,
    'cha': conf.coupling_physics.charnok,
    'cd': conf.coupling_physics.drag_coeff,
    'bhd': conf.coupling_physics.bernoulli_hd,
    'ss': conf.coupling_physics.stokes_shear,
    'foc': conf.coupling_physics.foc,
    'toc': conf.coupling_physics.tauoc,
    'taw': conf.coupling_physics.taw,
    'ssh': conf.coupling_physics.ssh,
    'cur': conf.coupling_physics.cur,
    }

    for k,v in data.items():
        if v.upper() in ['F','FALSE']:
            data[k]=['false','none']
        else:
            data[k] = ['true','coupled']
            if k in ['ss','sc']:
                data['sd'] = ['true', 'coupled']
    if data['sd'][0]:
        if not data['sdt'][0]:
            data['hs'] = ['true', 'coupled']
            data['tm'] = ['true', 'coupled']
        else:
            data['hs'] = ['false', 'none']
            data['tm'] = ['false', 'none']

    return data






