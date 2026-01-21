# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 22:35:53 2025

@author: campo
"""
parameter_columns_PNORC = ['Identifier','Date','Time','Cell_number','CellPosition','Speed(m/s)','v2','v3','v4','Direction','Amplitude_unit','Amplitude','A2','A3','A4','C1','C2','C3','C4']
parameter_columns_PNORW = ['Identifier','Date','Time','Spectrum_basis_type','Processing_method','Hm0','H3','H10','Hmax','Tm02','Tp','Tz','DirTp','SprTp','Main_Direction','Unidirectivity_index','Mean_pressure','Number_of_no_detects','Number_of_bad_detects','Near_surface_current_speed','Near_surface_current_Direction','error_code']
parameter_columns_PNORB = ['Identifier','Date','Time','Spectrum_basis_type','Processing_method','Frequency_low','Frequency_high','Hm0','Tm02','Tp','DirTp','SprTp','Main_Direction','Error_code']
parameter_columns_PNORI = ['Identifier','Instrument_type','Head_ID','Number_of_beams','Number_of_cells','Blanking(m)','Cell_size(m)','Checksum']
parameter_columns_PNORS = ['Identifier','Date','Time','Error_code','Status_Code','Battery','Sound_Speed','Heading','Pitch','Roll','Pressure(dbar)','Temperature(C)','Analog_Input_1','Checksum']

from QC_FLAGS_UMISAN import import_and_merge_curr_parameter,import_and_merge_wave_parameter,organizar_String_adcp
def processar_correntes(dfs,parameter_columns_correntes):
    df_correntes = import_and_merge_curr_parameter(dfs["df_pnors"], dfs["df_pnorc"])
    df_correntes = df_correntes[
    [col for col in parameter_columns_correntes if col in df_correntes.columns]
]
    # df_correntes = df_correntes.assign(**{f"Flag_{col}": 0 for col in df_correntes.columns})
    return df_correntes

def processar_ondas(dfs):
    df_ondas = import_and_merge_wave_parameter(dfs["df_pnorb"], dfs["df_pnors"], dfs["df_pnorw"])
    # df_ondas = df_ondas.assign(**{f"Flag_{col}": 0 for col in df_ondas.columns})
    return df_ondas
def organizar_dados_adcp(input_file, parameter_columns):
    (df_pnori,df_pnors,df_pnorw,df_pnore,df_pnorc,df_pnorwb,df_pnorb,df_pnorf,df_datalogger,) = organizar_String_adcp(input_file,parameter_columns_PNORC,parameter_columns_PNORI,parameter_columns_PNORS,parameter_columns_PNORB,parameter_columns_PNORW,parameter_columns,)
    return {"df_pnori": df_pnori,"df_pnors": df_pnors,"df_pnorw": df_pnorw,"df_pnore": df_pnore,"df_pnorc": df_pnorc,"df_pnorwb": df_pnorwb,"df_pnorb": df_pnorb,"df_pnorf": df_pnorf,"df_datalogger": df_datalogger,    }
