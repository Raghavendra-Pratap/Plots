import multiprocessing
import os
import pdb
import sys

import numpy as np
import pandas as pd

sys.path.append('/Users/raghavendra_pratap/Developer/ulp_shopmaster')

input_file_path = 'input_files'

output_file_path = 'output'
mapping_file_path = 'mapping'
check_output = 'check_output'
client_input_files_checked = 'client_input_files_checked'

month = '_Mar25'
beatpla_month = 'Mar25'


def prepare_store_master(store_df):
    store_df['Outlet'] = store_df['Outlet'].str.strip()
    store_df['Outlet'] = store_df['Outlet'].str.replace('  ', ' ')
    store_df['Outlet'] = store_df['Outlet'].str.replace('–', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace('- ', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace(' -', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace(' - ', '-')
    store_df['Outlet'] = store_df['Outlet'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode(
        'utf-8')
    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.strip()
    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.replace('  ', ' ')
    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.replace('–', '-')

    list_col = [
        'Sales Region ID', 'Sales Region', 'Customer', 'Digital/ Manual',
        'Channel Group', 'Area/Customer Group', 'Distributor/Customer', 'Banner', 'Channel ID', 'Channel',
        'Sub Channel ID', 'Sub Channel', 'Field Execution Manager', 'CBM/ACDM', 'FEE and Store Ops/MAE',
        'Agency Code', 'User ID', 'User'

    ]

    for a in list_col:
        print('columns in store master ', a)
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.strip()
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.replace('  ', ' ')
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.replace('–', '-')

    store_df.loc[
        (store_df['Trade Format'] == 'MODERN TRADE') | (store_df['Trade Format'] == 'MT'), 'Trade Format'] = 'OG'
    store_df.loc[(store_df['Trade Format'] == 'LOCAL MODERN TRADE') | (
            store_df['Trade Format'] == 'LMT'), 'Trade Format'] = 'MAG'

    store_df.to_csv(client_input_files_checked + '/store_upd.csv', index=False)

    store_df['Outlet ID'] = store_df['Outlet ID'].astype('str')  ##########################

    print('no of unique outlet id', store_df[['Outlet ID', 'Outlet', 'STORE TYPE']]['Outlet ID'].nunique())
    print('no of unique outlet name', store_df[['Outlet ID', 'Outlet', 'STORE TYPE']]['Outlet'].nunique())
    print('no of unique store type',
          store_df[['Outlet ID', 'Outlet', 'STORE TYPE']]['STORE TYPE'].nunique())  # check number of type of stores
    store_df1 = store_df[['Outlet ID', 'Outlet', 'Sub Channel', 'Trade Format'
                          ]]  # take relevant columns from store group mapping

    return store_df, store_df1


def prepare_osa_npd(osa_npd_df):
    osa_npd_df['Trade Format'] = osa_npd_df['Trade Format'].apply(lambda x: 'MT' if x == 'MODERN TRADE' else 'LMT')

    return osa_npd_df


def prepare_audit_check_list(audit_check_list_df):
    audit_df = audit_check_list_df.copy()

    audit_df['Outlet Name'] = audit_df['Outlet Name'].str.strip()
    audit_df['Outlet Name'] = audit_df['Outlet Name'].str.replace('  ', ' ')
    audit_df['Outlet Name'] = audit_df['Outlet Name'].str.replace('–', '-')
    audit_df['Outlet Name'] = audit_df['Outlet Name'].str.normalize('NFKD').str.encode('ascii',
                                                                                       errors='ignore').str.decode(
        'utf-8')
    audit_df.rename(columns={
        'SOS': 'Share of Shelf (SOS)',
        'PSP': 'Primary Shelf Placement (PSP)',
        'SCPLC': 'Secondary Placement'
    }, inplace=True)

    audit_df['STORE TYPE'] = audit_df['STORE TYPE'].str.strip()
    audit_df['STORE TYPE'] = audit_df['STORE TYPE'].str.replace('  ', ' ')
    audit_df['STORE TYPE'] = audit_df['STORE TYPE'].str.replace('–', '-')

    list_col = ['Customer Name', 'Reporting Category ID', 'Reporting Category']

    for a in list_col:
        print(a)
        audit_df['{}'.format(a)] = audit_df['{}'.format(a)].str.strip()
        audit_df['{}'.format(a)] = audit_df['{}'.format(a)].str.replace('  ', ' ')
        audit_df['{}'.format(a)] = audit_df['{}'.format(a)].str.replace('–', '-')

    audit_df.loc[audit_df['Reporting Category'] == 'CONDITIONER', 'Reporting Category ID'] = 'CON'
    audit_df.loc[audit_df['Reporting Category'] == 'FACE CARE', 'Reporting Category ID'] = 'FCA'
    audit_df.loc[audit_df['Reporting Category'] == 'BABY CARE', 'Reporting Category ID'] = 'BBC'
    audit_df.loc[audit_df['Reporting Category'] == 'SHAMPOO', 'Reporting Category ID'] = 'SHA'
    audit_df.loc[audit_df['Reporting Category'] == 'DEODORANTS', 'Reporting Category ID'] = 'DEO'
    audit_df.loc[audit_df['Reporting Category'] == 'HAND & BODY CARE', 'Reporting Category ID'] = 'HBC'
    audit_df.loc[audit_df['Reporting Category'] == 'FABRIC SOLUTIONS', 'Reporting Category ID'] = 'FCL'
    audit_df.loc[audit_df['Reporting Category'] == 'DRESSINGS', 'Reporting Category ID'] = 'DRE'
    audit_df.loc[audit_df['Reporting Category'] == 'ORAL CARE', 'Reporting Category ID'] = 'ORA'
    audit_df.loc[audit_df['Reporting Category'] == 'HOUSEHOLD CARE', 'Reporting Category ID'] = 'HHC'
    audit_df.loc[audit_df['Reporting Category'] == 'FABRIC SENSATIONS', 'Reporting Category ID'] = 'FCO'
    audit_df.loc[audit_df['Reporting Category'] == 'COOKING AIDS', 'Reporting Category ID'] = 'COO'
    audit_df.loc[audit_df['Reporting Category'] == 'SKIN CLEANSING', 'Reporting Category ID'] = 'SCL'
    audit_df.loc[audit_df['Reporting Category'] == 'GENERAL', 'Reporting Category ID'] = 'GEN'

    audit_df.loc[(audit_df['Trade Format Code'] == 'MODERN TRADE') | (
            audit_df['Trade Format Code'] == 'MT'), 'Trade Format Code'] = 'OG'
    audit_df.loc[(audit_df['Trade Format Code'] == 'LOCAL MODERN TRADE') | (
            audit_df['Trade Format Code'] == 'LMT'), 'Trade Format Code'] = 'MAG'

    audit_df['Outlet ID'] = audit_df['Outlet ID'].astype('str')  ##########################

    audit_df1 = audit_df[['Outlet ID', 'Outlet Name', 'Reporting Category', 'OSA', 'NPD', 'CTA', 'Share of Shelf (SOS)',
                          'Primary Shelf Placement (PSP)', 'Secondary Placement', 'NPD target', 'OSA target',
                          'SOS Target', 'Digital/Manual', 'STORE TYPE']]

    audit_df1 = audit_df1.rename(columns={'SOS Target': 'SOS target'})
    # Trade Format Code	STORE TYPE	Customer ID	Customer Name	Outlet ID	Outlet Name	Digital/Manual	Reporting Category ID	Reporting Category	OSA	OSA target	NPD	NPD target	Share of Shelf (SOS)	SOS Target	PSP	PSP target	SCPLC	SCPLC target	CTA	CTA target

    audit_df1 = audit_df1.drop_duplicates()

    audit_df1['Secondary Placement'] = audit_df1['Secondary Placement'].astype(str)
    audit_df1['Secondary Placement'] = audit_df1['Secondary Placement'].str.replace('1.0', '1')

    audit_df1[['Outlet ID', 'Outlet Name', 'Reporting Category']].drop_duplicates()
    # audit_df1.to_csv(check_output + '/audit_df1.csv')
    audit_df.to_csv(client_input_files_checked + '/audit_df_upd.csv')

    return audit_df, audit_df1


def prepare_survey_master(survey_master):
    # store_col_needed = []

    survey_master['CATEGORY'] = survey_master['CATEGORY'].str.upper()
    return survey_master


# create output files

def create_sku_master(store_df1, audit_df1, old_new_sku_mapping):
    store_df1['Outlet ID'].nunique()
    audit_df1['Outlet ID'].nunique()
    aud_store = pd.merge(store_df1, audit_df1, how='inner', left_on=['Outlet ID'], right_on=['Outlet ID'])

    cgc = pd.read_csv(input_file_path + '/cat-grp-cls - dimensions.csv', header=0)
    cgc['Class'] = cgc['Class'].str.strip()
    cgc['Class'] = cgc['Class'].str.replace('  ', ' ')
    cgc['Class'] = cgc['Class'].str.replace('–', '-')
    # cgc.dropna(inplace=True)
    cgc.to_csv(client_input_files_checked + '/cat-grp-cls_used_to_cat.csv', index=False)

    aud_store['Outlet ID'] = aud_store['Outlet ID'].astype(str)

    aud_store['Reporting Category'] = aud_store['Reporting Category'].str.title()

    # aud_store.to_csv(check_output + '/aud_store.csv')
    aud_store_cgc = pd.merge(aud_store, cgc, left_on='Reporting Category', right_on='Category', how='outer')
    print('Reporting Category :', aud_store_cgc['Reporting Category'].unique())

    sku = pd.read_csv(input_file_path + '/DPS_SEA_OSA_NPD.csv', header=0)

    # sku.head()

    sku['Store Type'] = sku['Store Type'].str.strip()
    sku['Store Type'] = sku['Store Type'].str.replace('  ', ' ')
    sku['Store Type'] = sku['Store Type'].str.replace('–', '-')

    sku['Store Type'] = sku['Store Type'].str.normalize('NFKD').str.encode('ascii',
                                                                           errors='ignore').str.decode(
        'utf-8')

    list_col = ['KPI', 'CATEGORY', 'CATEG_CODE', 'DESCRIPTION']

    for a in list_col:
        print(a)
        sku['{}'.format(a)] = sku['{}'.format(a)].str.strip()
        sku['{}'.format(a)] = sku['{}'.format(a)].str.replace('  ', ' ')
        sku['{}'.format(a)] = sku['{}'.format(a)].str.replace('–', '-')

    sku['DESCRIPTION'] = sku['DESCRIPTION'].str.strip()
    sku['DESCRIPTION'] = sku['DESCRIPTION'].str.replace('  ', ' ')
    sku['DESCRIPTION'] = sku['DESCRIPTION'].str.replace('–', '-')

    sku['DESCRIPTION'] = sku['DESCRIPTION'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode(
        'utf-8')

    sku.loc[(sku['Trade Format'] == 'MODERN TRADE') | (sku['Trade Format'] == 'MT'), 'Trade Format'] = 'OG'
    sku.loc[(sku['Trade Format'] == 'LOCAL MODERN TRADE') | (sku['Trade Format'] == 'LMT'), 'Trade Format'] = 'MAG'

    df = sku.copy()
    df = df[df['DESCRIPTION'].notna()]
    df['Class'] = df['DESCRIPTION']
    df['Class'] = df['Class'].str.strip()
    df['Reporting Category'] = df['CATEGORY'].str.title()
    df = df.rename(columns={'KPI': 'KPI_GROUP'})
    df = df.rename(columns={'Store Type': 'STORE TYPE'})

    df.to_csv(client_input_files_checked + '/osa_npd_upd.csv', index=False)
    df.loc[df['KPI_GROUP'] == 'OSA', 'kpi_osa_npd_only'] = 'OSA_1'
    df.loc[df['KPI_GROUP'] == 'NPD', 'kpi_osa_npd_only'] = 'NPD_1'

    df_1 = df[['KPI_GROUP', 'STORE TYPE', 'Class', 'Reporting Category', 'kpi_osa_npd_only']]
    print('df_1[Class].nunique() line 253 : ', df_1['Class'].nunique())
    # correct sku name or class name
    a = list(df_1['Class'].drop_duplicates())
    b = list(aud_store_cgc['Class'].drop_duplicates())
    main_list = np.setdiff1d(a, b)
    print('len(main_list) 1st check :', len(main_list))
    # main_list

    diff_classes = pd.DataFrame(main_list, columns=['Class'])
    diff_classes.to_csv(client_input_files_checked + '/differingClasses1.csv', index=False)
    # print('diff_classes',diff_classes)
    diff_classes_mapping = pd.read_csv(input_file_path + '/differingClasses - mapping.csv')
    # diff_classes_mapping

    mapping_dict = diff_classes_mapping.set_index('Class').to_dict()['corrected']
    # mapping_dict

    df_1['Class'] = df_1['Class'].map(mapping_dict).fillna(df_1['Class'])  ####################have to check this
    print('df_1[Class].nunique() line 293 : ', df_1['Class'].nunique())

    df_2 = df_1.copy()
    # df_1

    a = list(df_1['Class'].drop_duplicates())
    b = list(aud_store_cgc['Class'].drop_duplicates())
    main_list = np.setdiff1d(a, b)
    print('len(main_list) line 281: ', len(main_list))

    diff_classes = pd.DataFrame(main_list, columns=['Class'])
    diff_classes.to_csv(client_input_files_checked + '/differingClasses1.csv', index=False)

    print('diff_classes should be zero :', diff_classes)  # should be zero now

    # aud_store_cgc = aud_store_cgc.rename(columns={'STORE TYPE_x': 'STORE TYPE'})

    aud_store_cgc_plano = pd.merge(aud_store_cgc, df_1, on=['STORE TYPE', 'Class', 'Reporting Category'],
                                   how='outer')
    ###################################################################################################################

    aud_store_cgc_plano = aud_store_cgc_plano[aud_store_cgc_plano['Outlet'].notna()]
    aud_store_cgc_plano = aud_store_cgc_plano.drop_duplicates()
    aud_store_cgc_plano['Secondary Placement'].unique()
    # print(aud_store_cgc_plano)

    test_1 = aud_store_cgc_plano.copy()
    test_1 = test_1.rename(columns={'Class': 'Class'})

    test_1.loc[(test_1['Share of Shelf (SOS)'] == 1), 'SOS'] = '1'
    test_1.loc[(test_1['Share of Shelf (SOS)'] != 1), 'SOS'] = '0'
    test_1.loc[(test_1['Secondary Placement'] == '1'), 'Core Flag'] = '1'
    test_1.loc[(test_1['Secondary Placement'] != '1'), 'Core Flag'] = '0'

    mask_nonCateg = test_1['Class'].str.contains(r'NonCategory', na=True)
    test_1.loc[mask_nonCateg, 'Regular OSA'] = '0'
    test_1.loc[mask_nonCateg, 'NPD Flag'] = '0'
    test_1.loc[mask_nonCateg, 'SOS'] = '0'

    mask_shelf = test_1['Class'].str.contains(r'Shelf', na=True)
    test_1.loc[mask_shelf, 'Regular OSA'] = '0'
    test_1.loc[mask_shelf, 'NPD Flag'] = '0'
    test_1.loc[mask_shelf, 'SOS'] = '0'

    # osa npd 0, sos 1, core 0; shelf/non-category - everthing 0
    mask_others = test_1['Class'].str.contains(r'Other', na=True)
    test_1.loc[mask_others, 'Regular OSA'] = '0'
    test_1.loc[mask_others, 'NPD Flag'] = '0'
    # test_1.loc[mask_others, 'SOS'] = '1'
    test_1.loc[(test_1['kpi_osa_npd_only'] == 'OSA_1'), 'Regular OSA'] = '1'
    test_1.loc[(test_1['kpi_osa_npd_only'] == 'NPD_1'), 'NPD Flag'] = '1'
    test_1.loc[(test_1['kpi_osa_npd_only'] != 'OSA_1'), 'Regular OSA'] = '0'
    test_1.loc[(test_1['kpi_osa_npd_only'] != 'NPD_1'), 'NPD Flag'] = '0'

    test_1.loc[(test_1['OSA'] != 1), 'Regular OSA'] = '0'
    test_1.loc[(test_1['NPD'] != 1), 'NPD Flag'] = '0'

    test_2 = test_1.copy()
    test_2 = test_2.drop_duplicates()

    test_2.loc[test_2['NPD target'] == 'na', 'NPD target'] = 0
    test_2['NPD target'] = test_2['NPD target'].fillna(0)

    test_2.loc[test_2['OSA target'] == 'na', 'OSA target'] = 0
    test_2['OSA target'] = test_2['OSA target'].fillna(0)

    test_2.loc[test_2['SOS target'] == 'na', 'SOS target'] = 0
    test_2['SOS target'] = test_2['SOS target'].fillna(0)

    test_2['Ideal OSA(%)'] = test_2['OSA target'].apply(lambda x: round(x * 100, 2))

    test_2['Ideal OSA NPD(%)'] = test_2['NPD target'].apply(lambda x: round(x * 100, 2))
    test_2['Ideal SOS(%)'] = test_2['SOS target'].apply(lambda x: round(x * 100, 2))

    test_2[['Ideal SOS(%)']] = test_2[['Ideal SOS(%)']].fillna(0.0).astype(str)

    test_2.loc[test_2['Ideal SOS(%)'] == '100.0', 'Ideal SOS(%)'] = '99.99'

    test_2['Ideal SOS(%)'] = test_2['Ideal SOS(%)'].astype(str)

    test_2['Ideal OSA(%)'] = test_2['Ideal OSA(%)'].astype(str)

    test_2['Ideal OSA NPD(%)'] = test_2['Ideal OSA NPD(%)'].astype(str)

    # test_2 = test_2.drop_duplicates()
    global test_survey
    test_survey = test_2.copy()
    test_3 = test_2.copy()
    # test_3.columns
    test_3['Perfect Store Threshold(%)'] = 99.99
    test_3['Category Heading'] = 'Primary Placement'
    test_3['rtq'] = 1
    test_3['qc'] = 0

    test_3['Customer'] = test_3['STORE TYPE']
    test_3['Shelf Section'] = 'Primary Shelf'

    test_3['L'] = test_3['L'].astype(int)
    test_3['H'] = test_3['H'].astype(int)

    test_3.rename(columns={'Digital/Manual': 'Shop Type'}, inplace=True)
    test_final_1 = test_3[
        ['Outlet ID', 'Outlet', 'Perfect Store Threshold(%)', 'Customer', 'Category Heading', 'Reporting Category',
         'Shelf Section', 'rtq', 'qc', 'Group', 'Class', 'Regular OSA', 'NPD Flag', 'SOS', 'Core Flag', 'L', 'H',
         'Ideal OSA(%)', 'Ideal SOS(%)', 'Ideal OSA NPD(%)', 'Shop Type']]
    test_final_1.columns = ['Shop Id', 'Shop Name', 'Perfect Store Threshold(%)', 'Retailer', 'Category Heading',
                            'Category Name', 'Shelf Section', 'rtq', 'qc', 'Group name',
                            'SKU Name', 'Regular OSA', 'NPD Flag', 'SOS', 'Core Flag',
                            'Length(mm)', 'Height(mm)', 'Ideal OSA(%)',
                            'Ideal SOS(%)', 'Ideal OSA NPD(%)', 'Shop Type']

    cat_shelf_image = pd.read_excel(mapping_file_path + '/cat-shelf-image.xlsx', sheet_name='Sheet1')

    test_final_2 = pd.merge(test_final_1, cat_shelf_image, on='Category Name', how='inner')
    test_final_2['Shop Address'] = ''
    test_final_2['Overall Ideal OSA NPD(%)'] = test_final_2['Ideal OSA NPD(%)']
    test_final_2['Overall Ideal OSA(%)'] = test_final_2['Ideal OSA(%)']
    test_final_2['Overall Ideal SOS(%)'] = test_final_2['Ideal SOS(%)']

    test_final_2 = test_final_2.drop_duplicates()

    test_final_3 = test_final_2.copy()

    test_final_3.loc[
        test_final_3['Shop Type'] == 'DIGITAL', 'Shelf Section'] = 'Primary Shelf,Extension of Primary,Secondary Shelf'
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'rtq'] = '1,1,1'
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'qc'] = '0,0,0'
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'Ideal OSA(%)'] = test_final_3['Ideal OSA(%)'] + ',' + \
                                                                               test_final_3['Ideal OSA(%)'] + ',' + \
                                                                               test_final_3['Ideal OSA(%)']
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'Ideal OSA NPD(%)'] = test_final_3[
                                                                                       'Ideal OSA NPD(%)'] + ',' + \
                                                                                   test_final_3[
                                                                                       'Ideal OSA NPD(%)'] + ',' + \
                                                                                   test_final_3['Ideal OSA NPD(%)']
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'Ideal SOS(%)'] = test_final_3['Ideal SOS(%)'] + ',0,0'
    test_final_3.loc[test_final_3['Shop Type'] == 'DIGITAL', 'Shelf Section Image Links'] = test_final_3[
                                                                                                'Shelf Section Image Links'] + ',' + \
                                                                                            test_final_3[
                                                                                                'Shelf Section Image Links'] + ',' + \
                                                                                            test_final_3[
                                                                                                'Shelf Section Image Links']

    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (
            test_final_3['Core Flag'] == '1'), 'Shelf Section'] = 'Primary Shelf,Secondary Shelf'

    ######################################added new #########################################################
    # test_final_3.loc[(test_final_3['Shop Type'] == 'DIGITAL') & (
    #         test_final_3['Core Flag'] == '1'), 'Shelf Section'] = 'Secondary Shelf'

    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'rtq'] = '1,1'
    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'qc'] = '0,0'
    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'Ideal OSA(%)'] = \
        test_final_3['Ideal OSA(%)'] + ',' + test_final_3['Ideal OSA(%)']
    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'Ideal OSA NPD(%)'] = \
        test_final_3['Ideal OSA NPD(%)'] + ',' + test_final_3['Ideal OSA NPD(%)']
    test_final_3.loc[(test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'Ideal SOS(%)'] = \
        test_final_3['Ideal SOS(%)'] + ',0'
    test_final_3.loc[
        (test_final_3['Shop Type'] == 'MANUAL') & (test_final_3['Core Flag'] == '1'), 'Shelf Section Image Links'] = \
        test_final_3['Shelf Section Image Links'] + ',' + test_final_3['Shelf Section Image Links']

    cols = pd.read_csv(mapping_file_path + '/SKU master columns.csv')
    # cols.columns

    test_final_3 = test_final_3[list(cols.columns)]

    test_final_3['Shop Id'] = test_final_3['Shop Id'].astype(str) + month
    test_final_3['Shop Name'] = test_final_3['Shop Name'] + month
    test_final_4 = test_final_3.copy()
    del test_final_2

    test_final_4['Shop Name'] = test_final_4['Shop Name'].replace("  ", " ")

    a = list(test_final_4['Shop Name'].drop_duplicates())
    b = list(test_final_3['Shop Name'].drop_duplicates())
    main_list = np.setdiff1d(a, b)
    print(len(main_list))
    del test_final_3

    test_final_4.reset_index(drop=True, inplace=True)

    # TO CREATE SKU MASTER UNCOMMENT THIS LOOP
    count = 0
    total_count = len(test_final_4.groupby(['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name']))

    for (shop, shop_name, category, group, class_name), df in test_final_4.groupby(
            ['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name']):
        reg_osa = df['Regular OSA'].astype('int').sum()
        osa_npd = df['NPD Flag'].astype('int').sum()

        if reg_osa == 1 and osa_npd == 1:
            test_final_4.loc[df.index, 'Regular OSA'] = '1'
            test_final_4.loc[df.index, 'NPD Flag'] = '1'

        count = count + 1
        print(count, ' / ', total_count)

    # test_final_4['Regular OSA'] = test_final_4.groupby(        ['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name']    ).transform(lambda x: '1' if (x['Regular OSA'].astype('int').sum() == 1) and (x['NPD Flag'].astype('int').sum() == 1)  else x,axis=1)

    # test_final_4['NPD Flag'] = test_final_4.groupby(
    #     ['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name']
    # ).transform(lambda x: '1' if (x['Regular OSA'].astype('int').sum() == 1) and (x['NPD Flag'].astype('int').sum() == 1)  else x,axis=1)

    # grouped = test_final_4.groupby(['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name'])

    # test_final_4['Regular OSA'] = grouped['Regular OSA'].transform(        lambda x: '1' if (x.astype('int').sum() == 1) and (x['NPD Flag'].astype('int').sum() == 1) else x)
    # test_final_4['NPD Flag'] = grouped['NPD Flag'].transform(        lambda x: '1' if (x['Regular OSA'].astype('int').sum() == 1) and (x.astype('int').sum() == 1) else x)

    #

    #
    test_final_4.drop_duplicates(subset=['Shop Id', 'Shop Name', 'Category Name', 'Group name', 'SKU Name'],
                                 inplace=True)
    test_final_4.reset_index(drop=True, inplace=True)

    ###########################new changes dated 19-09-2022###################################
    #############jira ticket no PTS-243 ################
    ################ point 1 ###################
    #
    # secondary_shelf_client_shop_id_df = audit_df1[        (                    audit_df1['Secondary Placement'] == 1) & (audit_df1['Digital/Manual'] == 'DIGITAL')][        ['Outlet ID', 'Reporting Category']]
    # secondary_shelf_client_shop_id_df['Outlet ID'] = secondary_shelf_client_shop_id_df['Outlet ID'] + month
    # secondary_shelf_client_shop_id_df['Reporting Category'] = secondary_shelf_client_shop_id_df['Reporting Category'].str.title()
    # for i, row in secondary_shelf_client_shop_id_df.iterrows():
    #
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']),  'Shelf Section'] = 'Secondary Shelf'
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal OSA NPD(%)'] = 0.0
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal SOS(%)'] = 0.0
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal OSA(%)'] = 0.0
    #
    # ############### point 2 ###########################
    #
    # primary_shelf_client_shop_id_df = audit_df1[        (audit_df1['OSA'] != 1) & (audit_df1['NPD'] != 1) & (audit_df1['Share of Shelf (SOS)'] != 1) & (                    audit_df1['Secondary Placement'] != 1) & (audit_df1['Digital/Manual'] == 'DIGITAL')][        ['Outlet ID', 'Reporting Category']]
    # primary_shelf_client_shop_id_df['Outlet ID'] = primary_shelf_client_shop_id_df['Outlet ID'] + month
    # primary_shelf_client_shop_id_df['Reporting Category'] = primary_shelf_client_shop_id_df['Reporting Category'].str.title()
    #
    # for i, row in primary_shelf_client_shop_id_df.iterrows():
    #
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']),  'Shelf Section'] = 'Primary Shelf'
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal OSA NPD(%)'] = 0.0
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal SOS(%)'] = 0.0
    #     test_final_4.loc[(test_final_4['Shop Id'] == row['Outlet ID']) & (test_final_4['Category Name'] == row['Reporting Category']), 'Ideal OSA(%)'] = 0.0
    #
    #

    test_final_4 = test_final_4.sort_values(['Shop Name', 'Category Name', 'Group name'])

    test_final_4['Shop Type'] = test_final_4['Shop Type'].str.title()

    test_final_4 = test_final_4[['Shop Id',
                                 'Category Heading', 'Category Name', 'Group name', 'SKU Name', 'NPD Flag',
                                 'Regular OSA', 'SOS', 'Core Flag',
                                 'Shelf Section Image Links', 'Shelf Section',
                                 'Perfect Store Threshold(%)', 'Ideal OSA(%)', 'Overall Ideal OSA(%)',
                                 'Ideal SOS(%)', 'Overall Ideal SOS(%)', 'Ideal OSA NPD(%)',
                                 'Overall Ideal OSA NPD(%)']]
    ##############################start pts 1591###############################################
    old_sku_list = old_new_sku_mapping[['old_sku_name', 'new_sku_name', 'new_group_name']].drop_duplicates(
        subset=['old_sku_name', 'new_sku_name'])
    new_df = pd.DataFrame({})
    test_final_4 = test_final_4[~test_final_4['SKU Name'].isin(old_new_sku_mapping['new_sku_name'].unique().tolist())]
    for i, row in old_sku_list.iterrows():
        change_df = test_final_4[test_final_4['SKU Name'] == row['old_sku_name']].copy()
        change_df['SKU Name'] = row['new_sku_name']
        change_df['Group name'] = row['new_group_name']
        new_df = pd.concat([new_df, change_df])
    new_df.to_csv('concat_new_sku_df.csv')
    test_final_4 = test_final_4._append(new_df)
    # test_final_4.drop_duplicates(subset=['Shop Id', 'Category Heading', 'Category Name', 'Group name', 'SKU Name'],
    #                              inplace=True)

    test_final_4 = test_final_4[['Shop Id',
                                 'Category Heading', 'Category Name', 'Group name', 'SKU Name', 'NPD Flag',
                                 'Regular OSA', 'SOS', 'Core Flag',
                                 'Shelf Section Image Links', 'Shelf Section',
                                 'Perfect Store Threshold(%)', 'Ideal OSA(%)', 'Overall Ideal OSA(%)',
                                 'Ideal SOS(%)', 'Overall Ideal SOS(%)', 'Ideal OSA NPD(%)',
                                 'Overall Ideal OSA NPD(%)']]

    ##############################end pts 1591###############################################

    n = 700000  # chunk row size
    test_final_4.sort_values(by=['Shop Id', 'Category Name', 'SKU Name'], ascending=True, inplace=True)

    list_df = [test_final_4[i:i + n] for i in range(0, test_final_4.shape[0], n)]
    common_shop_id_df = pd.DataFrame({})
    last_check = len(list_df) - 1
    for i in range(len(list_df)):
        if i != last_check:
            shop_ids_set1 = set(list_df[i]['Shop Id'])
            shop_ids_set2 = set(list_df[i + 1]['Shop Id'])
            common_shop_ids = shop_ids_set1.intersection(shop_ids_set2)

            temp_common_shop_id_df_1 = list_df[i][list_df[i]['Shop Id'].isin(common_shop_ids)]
            temp_common_shop_id_df_2 = list_df[i + 1][list_df[i + 1]['Shop Id'].isin(common_shop_ids)]

            list_df[i] = list_df[i][~list_df[i]['Shop Id'].isin(common_shop_ids)]
            list_df[i + 1] = list_df[i + 1][~list_df[i + 1]['Shop Id'].isin(common_shop_ids)]
            common_shop_id_df = pd.concat([common_shop_id_df, temp_common_shop_id_df_1, temp_common_shop_id_df_2])
        list_df[i].to_csv(output_file_path + '/SKU Master ' + str(i) + '.csv', index=False)
    common_shop_id_df.to_csv(output_file_path + '/SKU Master ' + str(len(list_df)) + '.csv', index=False)
    return test_final_4


def create_survey_master(survey_master, test_final_4, audit_df1):
    survey_master = survey_master.rename(
        columns={'STORE TYPE': 'Store Type', 'STORE CODE': 'Store_code', 'CATEGORY': 'Category', 'BRAND 1': 'Brand',
                 'SURVEY QUESTIONS': 'Survey Questions'})

    survey_q = survey_master[
        ['CATEG_CODE', 'Category', 'KPI', 'Store Type', 'Store_code', 'Survey Questions', 'Brand']]

    survey_q['Store Type'] = survey_q['Store Type'].str.strip()
    survey_q['Store Type'] = survey_q['Store Type'].str.replace('  ', ' ')
    survey_q['Store Type'] = survey_q['Store Type'].str.replace('–', '-')
    survey_q['Store_code'] = survey_q['Store_code'].astype('str')
    list_col = ['Store Type', 'Store_code', 'CATEG_CODE', 'Category', 'Brand', 'Survey Questions']

    for a in list_col:
        print(a)
        survey_q['{}'.format(a)] = survey_q['{}'.format(a)].str.strip()
        survey_q['{}'.format(a)] = survey_q['{}'.format(a)].str.replace('  ', ' ')
        survey_q['{}'.format(a)] = survey_q['{}'.format(a)].str.replace('–', '-')
    survey_q['Survey Questions'] = survey_q['Survey Questions'].str.normalize('NFKD').str.encode('ascii',
                                                                                                 errors='ignore').str.decode(
        'utf-8')

    survey_q.to_csv(client_input_files_checked + '/survey_q_upd.csv')

    # code for manual store survey_master
    survey_1_scplc = survey_q.loc[survey_q['Store_code'] != "*"]
    audit_df1['Outlet ID'] = audit_df1['Outlet ID'].astype(str)
    survey_1_scplc['Store_code'] = survey_1_scplc['Store_code'].astype(str)
    audit_df2 = audit_df1[audit_df1['Secondary Placement'] == '1'][['Outlet ID', 'Outlet Name', 'Reporting Category']]

    survey_1_scplc = pd.merge(audit_df2, survey_1_scplc, left_on=['Outlet ID', 'Reporting Category'],
                              right_on=['Store_code', 'Category'], how='inner')
    survey_1_scplc = survey_1_scplc.drop_duplicates()

    # survey_1_scplc.loc[survey_1_scplc['KPI_GROUP'] == 'PSP', 'Sections'] = 'Primary Shelf'
    survey_1_scplc.loc[survey_1_scplc['KPI'] == 'SCPLC', 'Sections'] = 'Secondary Shelf'

    survey_1_scplc['Question Type'] = 'single'
    survey_1_scplc['Answers'] = 'Yes,No'
    survey_1_scplc['Group'] = 'NA'
    survey_1_scplc['Class'] = 'NA'
    survey_1_scplc['KPI'] = 'Survey'
    survey_1_scplc['Question flag'] = 'mandatory'
    survey_1_scplc['Store_code'] = survey_1_scplc['Outlet ID'].astype(str) + month
    survey_1_scplc = survey_1_scplc.rename(columns={'Store_code': 'Shop ID', 'Outlet Name': 'Shop Name'})

    ##########################################scplc que if client demand####################################################
    # survey_1_scplc = survey_1_scplc[list(survey_sample.columns)]
    # survey_1_scplc.to_csv(client_input_files_checked + '/survey_code.csv', index=False)

    # We got to remove the freetext questions totally. (Apparently, Jep said that we will accommodate this extra SCPLC question in the JUNE audits, for which Suyash and team are working and that type of the question will have to be accomodated in the Shopmaster code, for now lets comment the freetext code).
    # sm_scplc_freetext = survey_1_scplc.copy()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('IS THE', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace(
    #     'AVAILABLE AS SECONDARY PLACEMENT', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.strip()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('     ', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('–', '-')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext.apply(
    #     lambda x: 'If {} not available as secondary placement, please mention the reason.'.format(
    #         x['Survey Questions']), axis=1)
    #
    # sm_scplc_freetext['Question Type'] = 'freetext'
    # sm_scplc_freetext['Question flag'] = 'optional'
    # sm_scplc_freetext['Answers'] = ''
    # survey_1_scplc = pd.concat([survey_1_scplc, sm_scplc_freetext])

    #########################################################################################################################
    # sm_scplc_freetext = survey_1_scplc.copy()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('Is ', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('IS ', ' ')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace(
    # #     'display allowance available (topshelves or other display type)?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.strip()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('     ', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('–', '-')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext.apply(
    # #     lambda x: 'If {} , click a photo'.format(x['Survey Questions'].replace(' ','')), axis=1)
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext.apply(
    #         lambda x: 'If {} , click a photo'.format(x['Survey Questions']), axis=1)
    #
    # sm_scplc_freetext['Question Type'] = 'phototext'
    # sm_scplc_freetext['Question flag'] = 'optional'
    # sm_scplc_freetext['Answers'] = ''
    # survey_1_scplc = pd.concat([survey_1_scplc, sm_scplc_freetext])
    #########################################################################################################################################333

    #########################################################################################################################
    # sm_scplc_freetext = survey_1_scplc.copy()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('Is', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('IS', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace(
    #     'display allowance available (topshelves or other display type)?', ' ')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.strip()
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('     ', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('–', '-')
    # # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext['Survey Questions'].str.replace('?', ' ')
    # sm_scplc_freetext['Survey Questions'] = sm_scplc_freetext.apply(
    #     lambda x: 'If {} display allowance is not available, share reason.'.format(x['Survey Questions'].replace('(topshelves or other display type)?','')), axis=1)
    #
    # sm_scplc_freetext['Question Type'] = 'single'
    # sm_scplc_freetext['Question flag'] = 'optional'
    # sm_scplc_freetext['Answers'] = 'Different BRAND Displayed, Different DISPLAY TYPE, No Area/ Space for deployment, No memo in store/ received, No placement yet (stocks), On-going deployment/No CE for store transfer (merch), Store closed, Under renovation, Others'
    # survey_1_scplc = pd.concat([survey_1_scplc, sm_scplc_freetext])
    #########################################################################################################################################333

    survey_2_psp_cta = survey_q.loc[survey_q['Store Type'] != "*"]
    survey_2_psp_cta['Store Type'] = survey_2_psp_cta['Store Type'].astype(str)
    audit_df1['STORE TYPE'] = audit_df1['STORE TYPE'].astype(str)
    audit_df3 = audit_df1.loc[audit_df1['Primary Shelf Placement (PSP)'] == 1][
        ['STORE TYPE', 'Outlet ID', 'Outlet Name', 'Reporting Category']]
    survey_2_psp = pd.merge(audit_df3, survey_2_psp_cta, left_on=['STORE TYPE', 'Reporting Category'],
                            right_on=['Store Type', 'Category'], how='inner')
    survey_2_psp = survey_2_psp.drop_duplicates()
    survey_2_psp = survey_2_psp.loc[survey_2_psp['KPI'] == 'PSP']
    if len(survey_2_psp):
        survey_2_psp.loc[survey_2_psp['KPI'] == 'PSP', 'Sections'] = 'Primary Shelf'
        # survey_2_psp.loc[survey_2_psp['KPI'] == 'CTA', 'Sections'] = 'Primary Shelf'
        survey_2_psp['Question Type'] = 'single'
        survey_2_psp['Answers'] = 'Yes,No'
        survey_2_psp['Group'] = 'NA'
        survey_2_psp['Class'] = 'NA'
        survey_2_psp['KPI'] = 'Survey'
        survey_2_psp['Question flag'] = 'mandatory'
        survey_2_psp['Store_code'] = survey_2_psp['Outlet ID'].astype(str) + month
        survey_2_psp = survey_2_psp.rename(columns={'Store_code': 'Shop ID', 'Outlet Name': 'Shop Name'})

        survey_2_psp.drop(columns=['STORE TYPE'], inplace=True)

    audit_df4 = audit_df1.loc[audit_df1['CTA'] == 1][['STORE TYPE', 'Outlet ID', 'Outlet Name', 'Reporting Category']]
    survey_2_cta = pd.merge(audit_df4, survey_2_psp_cta, left_on=['STORE TYPE', 'Reporting Category'],
                            right_on=['Store Type', 'Category'], how='inner')
    survey_2_cta = survey_2_cta.drop_duplicates()
    survey_2_cta = survey_2_cta.loc[survey_2_cta['KPI'] == 'CTA']
    # survey_2_psp.loc[survey_2_psp['KPI'] == 'PSP', 'Sections'] = 'Primary Shelf'
    if len(survey_2_cta):
        survey_2_cta.loc[survey_2_cta['KPI'] == 'CTA', 'Sections'] = 'Primary Shelf'
        survey_2_cta['Question Type'] = 'single'
        survey_2_cta['Answers'] = 'Yes,No'
        survey_2_cta['Group'] = 'NA'
        survey_2_cta['Class'] = 'NA'
        survey_2_cta['KPI'] = 'Proposition'
        survey_2_cta['Question flag'] = 'mandatory'
        survey_2_cta['Store_code'] = survey_2_cta['Outlet ID'].astype(str) + month
        survey_2_cta = survey_2_cta.rename(columns={'Store_code': 'Shop ID', 'Outlet Name': 'Shop Name'})
        survey_2_cta.drop(columns=['STORE TYPE'], inplace=True)

    if len(survey_2_psp):
        survey_1 = pd.concat([survey_1_scplc, survey_2_psp])
    else:
        survey_1 = survey_1_scplc
    if len(survey_2_cta):
        survey_1 = pd.concat([survey_1, survey_2_cta])
    else:
        survey_1 = survey_1
    # solution for We have seen that Digital shops had SOS question, which is not correct. In Survey master, when the shop type is Digital then we should have only PSP, SCPLC, and CTA question corresponding questions to that, as applicable.
    audit_df5 = audit_df1[(audit_df1['Share of Shelf (SOS)'] == 1) & (audit_df1['Digital/Manual'] == 'MANUAL')][
        ['STORE TYPE', 'Outlet ID', 'Outlet Name', 'Reporting Category']]
    survey_sos_q1 = audit_df5.copy()
    survey_sos_q2 = audit_df5.copy()
    #  new two survey que added 5-2-24
    survey_sos_q1['Store_code'] = survey_sos_q1['Outlet ID'].astype(str) + month
    survey_sos_q1['Category'] = survey_sos_q1['Reporting Category']
    survey_sos_q1['Survey Questions'] = 'Enter the ULP measurement (in cm)'
    survey_sos_q1['Question Type'] = 'number'
    survey_sos_q1['Answers'] = ""
    survey_sos_q1['Class'] = "NA"
    survey_sos_q1['KPI'] = 'SOS'
    survey_sos_q1['Question flag'] = 'mandatory'
    survey_sos_q1['Sections'] = 'Primary Shelf'
    survey_sos_q1['Group'] = 'self'
    survey_sos_q1['CATEG_CODE'] = None
    survey_sos_q1 = survey_sos_q1.drop_duplicates()
    survey_sos_q1 = survey_sos_q1.rename(
        columns={'STORE TYPE': 'Store Type', 'Store_code': 'Shop ID', 'Outlet Name': 'Shop Name'})

    survey_sos_q2['Store_code'] = survey_sos_q2['Outlet ID'].astype(str) + month
    survey_sos_q2['Category'] = survey_sos_q2['Reporting Category']
    survey_sos_q2['Survey Questions'] = 'Enter the Total Category measurement (in cm)'
    survey_sos_q2['Question Type'] = 'number'
    survey_sos_q2['Answers'] = ""
    survey_sos_q2['Class'] = "NA"
    survey_sos_q2['KPI'] = 'SOS'
    survey_sos_q2['Question flag'] = 'mandatory'
    survey_sos_q2['Sections'] = 'Primary Shelf'
    survey_sos_q2['Group'] = 'self'
    survey_sos_q2['CATEG_CODE'] = None
    survey_sos_q2 = survey_sos_q2.drop_duplicates()
    survey_sos_q2 = survey_sos_q2.rename(
        columns={'STORE TYPE': 'Store Type', 'Store_code': 'Shop ID', 'Outlet Name': 'Shop Name'})

    survey_1 = pd.concat([survey_1, survey_sos_q1,survey_sos_q2])

    survey_raw = test_survey.drop_duplicates()
    survey_raw['Shop Name'] = survey_raw['Outlet'].str.replace(month, '')
    # survey_raw_manual = survey_raw[survey_raw['Digital/Manual'] == 'MANUAL']
    survey_raw_manual = survey_raw.loc[survey_raw['Digital/Manual'] == 'MANUAL']

    survey_raw_manual_osa = survey_raw_manual.loc[survey_raw_manual['Regular OSA'] == '1'][
        ['Outlet ID', 'Outlet Name', 'Category', 'Group', 'Class', 'STORE TYPE']]
    if len(survey_raw_manual_osa):
        survey_raw_manual_osa['Sections'] = 'Primary Shelf'
        survey_raw_manual_osa['Survey Questions'] = survey_raw_manual_osa.apply(
            lambda x: 'Is {} present?'.format(x['Class']), axis=1)
        survey_raw_manual_osa['Question Type'] = 'single'
        survey_raw_manual_osa['Answers'] = 'Yes,No'
        survey_raw_manual_osa['KPI'] = 'OSA'
        survey_raw_manual_osa['Question flag'] = 'mandatory'
        survey_raw_manual_osa['Shop ID'] = survey_raw_manual_osa['Outlet ID'].astype('str') + month
        survey_raw_manual_osa = survey_raw_manual_osa.rename(columns={'Outlet Name': 'Shop Name'})
        survey_raw_manual_osa = survey_raw_manual_osa.drop_duplicates()

    survey_raw_manual_npd = survey_raw_manual.loc[survey_raw_manual['NPD Flag'] == '1'][
        ['Outlet ID', 'Outlet Name', 'Category', 'Group', 'Class', 'STORE TYPE']]
    if len(survey_raw_manual_npd):
        survey_raw_manual_npd['Sections'] = 'Primary Shelf'
        survey_raw_manual_npd['Survey Questions'] = survey_raw_manual_npd.apply(
            lambda x: 'Is {} present?'.format(x['Class']), axis=1)
        survey_raw_manual_npd['Question Type'] = 'single'
        survey_raw_manual_npd['Answers'] = 'Yes,No'
        survey_raw_manual_npd['KPI'] = 'OSA_NPD'
        survey_raw_manual_npd['Question flag'] = 'mandatory'
        survey_raw_manual_npd['Shop ID'] = survey_raw_manual_npd['Outlet ID'].astype('str') + month
        survey_raw_manual_npd = survey_raw_manual_npd.rename(columns={'Outlet Name': 'Shop Name'})
        survey_raw_manual_npd = survey_raw_manual_npd.drop_duplicates()

    survey_manual = pd.concat([survey_raw_manual_osa, survey_raw_manual_npd])
    survey_manual.rename(columns={'STORE TYPE': 'Store Type'}, inplace=True)

    survey_1 = survey_1[
        ['Shop ID', 'Shop Name', 'Category', 'Sections', 'Survey Questions', 'Question Type', 'Answers', 'Group',
         'Class', 'KPI', 'Question flag']]
    if len(survey_manual):
        survey_manual = survey_manual[
            ['Shop ID', 'Shop Name', 'Category', 'Sections', 'Survey Questions', 'Question Type', 'Answers', 'Group',
             'Class', 'KPI', 'Question flag']]

        final_survey = pd.concat([survey_1, survey_manual])
    else:
        final_survey = survey_1
    final_survey.rename(columns={'Category': 'Category Name'}, inplace=True)
    final_survey['Shop Name'] = final_survey['Shop Name'].astype('str') + month
    final_survey['Category Name'] = final_survey['Category Name'].str.title()
    final_survey.reset_index(drop=True, inplace=True)

    # added to genralized shop name of survey master with store master
    final_survey['Shop Name'] = final_survey['Shop Name'].str.strip()
    final_survey['Shop Name'] = final_survey['Shop Name'].str.replace('  ', ' ')
    final_survey['Shop Name'] = final_survey['Shop Name'].str.replace('–', '-')

    final_survey['Shop Name'] = final_survey['Shop Name'].str.normalize('NFKD').str.encode('ascii',
                                                                                           errors='ignore').str.decode(
        'utf-8')


    ##########################################################################################

    n = 700000  # chunk row size
    final_survey.sort_values(by=['Shop ID'], ascending=True, inplace=True)

    list_df = [final_survey[i:i + n] for i in range(0, final_survey.shape[0], n)]
    common_shop_id_df = pd.DataFrame({})
    last_check = len(list_df) - 1
    for i in range(len(list_df)):
        if i != last_check:
            shop_ids_set1 = set(list_df[i]['Shop ID'])
            shop_ids_set2 = set(list_df[i + 1]['Shop ID'])
            common_shop_ids = shop_ids_set1.intersection(shop_ids_set2)

            temp_common_shop_id_df_1 = list_df[i][list_df[i]['Shop ID'].isin(common_shop_ids)]
            temp_common_shop_id_df_2 = list_df[i + 1][list_df[i + 1]['Shop ID'].isin(common_shop_ids)]

            list_df[i] = list_df[i][~list_df[i]['Shop ID'].isin(common_shop_ids)]
            list_df[i + 1] = list_df[i + 1][~list_df[i + 1]['Shop ID'].isin(common_shop_ids)]
            common_shop_id_df = pd.concat([common_shop_id_df, temp_common_shop_id_df_1, temp_common_shop_id_df_2])
        list_df[i].to_csv(output_file_path + '/survey_master ' + str(i) + '.csv', index=False)
    common_shop_id_df.to_csv(output_file_path + '/survey_master ' + str(len(list_df)) + '.csv', index=False)


    ##########################################################################################

    # final_survey.to_csv(output_file_path + '/survey_master.csv', index=False)


def create_beat_plan(store_df):
    store_df['Outlet'] = store_df['Outlet'].str.strip()
    store_df['Outlet'] = store_df['Outlet'].str.replace('  ', ' ')
    store_df['Outlet'] = store_df['Outlet'].str.replace('–', '-')

    store_df['Outlet'] = store_df['Outlet'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode(
        'utf-8')

    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.strip()
    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.replace('  ', ' ')
    store_df['STORE TYPE'] = store_df['STORE TYPE'].str.replace('–', '-')

    list_col = [
        'Sales Region ID', 'Sales Region', 'Customer', 'Digital/ Manual',
        'Channel Group', 'Area/Customer Group', 'Distributor/Customer', 'Banner', 'Channel ID', 'Channel',
        'Sub Channel ID', 'Sub Channel', 'Field Execution Manager', 'CBM/ACDM', 'FEE and Store Ops/MAE',
        'Agency Code', 'User ID', 'User']

    for a in list_col:
        print(a)
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.strip()
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.replace('  ', ' ')
        store_df['{}'.format(a)] = store_df['{}'.format(a)].str.replace('–', '-')

    store_df.loc[store_df['Trade Format'] == 'MODERN TRADE', 'Trade Format'] = 'OG'
    store_df.loc[store_df['Trade Format'] == 'LOCAL MODERN TRADE', 'Trade Format'] = 'MAG'

    cols_store_beat = ['Outlet ID', 'Outlet', 'User ID', 'User']
    beat_plan = store_df[cols_store_beat]
    beat_plan.rename(
        columns={'Outlet ID': 'SHOP_ID', 'Outlet': 'SHOP_NAME', 'User ID': 'LOGIN_ID',
                 'User': 'USER_NAME'}, inplace=True)

    cols = ['LOGIN_PASSWORD', 'DAY', 'Frequency', 'Validity',
            'start_day', 'end_day', 'start_date', 'end_date', 'day_count', 'survey_validity', 'survey_start_date',
            'survey_end_date', 'survey_start_day', 'survey_end_day', 'survey_day_count', 'Applicable_Dates'
            ]

    beat_plan['DAY'] = 'ALL'
    beat_plan['Frequency'] = ''
    beat_plan['Validity'] = 'Monthly'
    beat_plan['start_day'] = ''
    beat_plan['end_day'] = ''
    beat_plan['start_date'] = 1
    beat_plan['end_date'] = 31
    beat_plan['day_count'] = ''
    beat_plan['survey_validity'] = 'Monthly'
    beat_plan['survey_start_date'] = 1
    beat_plan['survey_end_date'] = 31
    beat_plan['survey_start_day'] = ''
    beat_plan['survey_end_day'] = ''
    beat_plan['survey_day_count'] = ''
    beat_plan['Applicable_Dates'] = ''
    beat_plan['index1'] = beat_plan.index
    beat_plan['LOGIN_PASSWORD'] = beat_plan.index

    count = 2022
    for i, df in beat_plan.groupby(['LOGIN_ID']):
        beat_plan.loc[df.index, 'LOGIN_PASSWORD'] = "ulp_{}@{}".format(count, beatpla_month)
        count = count + 1
    # beat_plan['LOGIN_PASSWORD'] = beat_plan.apply(lambda x: "ulp_may@22{}".format(x.index1), axis=1)
    beat_plan['LOGIN_ID'] = beat_plan.apply(lambda x: "{}_{}".format(x.LOGIN_ID, beatpla_month), axis=1)
    beat_plan['SHOP_ID'] = beat_plan.apply(lambda x: "{}_{}".format(x.SHOP_ID, beatpla_month), axis=1)
    beat_plan['SHOP_NAME'] = beat_plan.apply(lambda x: "{}_{}".format(x.SHOP_NAME, beatpla_month), axis=1)
    colm = ['SHOP_ID', 'SHOP_NAME', 'LOGIN_ID', 'USER_NAME', 'LOGIN_PASSWORD', 'DAY', 'Frequency', 'Validity',
            'start_day', 'end_day', 'start_date', 'end_date', 'day_count', 'survey_validity', 'survey_start_date',
            'survey_end_date', 'survey_start_day', 'survey_end_day', 'survey_day_count', 'Applicable_Dates']
    beat_plan = beat_plan[colm]
    return beat_plan


def prepare_store_master_reformation_data(master_store):
    # master_store['Shop Address']=np.NAN
    try:
        master_store['Outlet ID'] = master_store['Outlet ID'].str.strip()
        master_store['Outlet ID'] = master_store['Outlet ID'].str.replace('  ', ' ')
        master_store['Outlet ID'] = master_store['Outlet ID'].str.replace('–', '-')
        # store_df['Outlet'] = store_df['Outlet'].str.replace('- ', '-')
        # store_df['Outlet'] = store_df['Outlet'].str.replace(' -', '-')
        # store_df['Outlet'] = store_df['Outlet'].str.replace(' - ', '-')
        master_store['Outlet ID'] = master_store['Outlet ID'].str.normalize('NFKD').str.encode('ascii',
                                                                                               errors='ignore').str.decode(
            'utf-8')
    except:
        pass
    master_store['Outlet'] = master_store['Outlet'].str.strip()
    master_store['Outlet'] = master_store['Outlet'].str.replace('  ', ' ')
    master_store['Outlet'] = master_store['Outlet'].str.replace('–', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace('- ', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace(' -', '-')
    # store_df['Outlet'] = store_df['Outlet'].str.replace(' - ', '-')
    master_store['Outlet'] = master_store['Outlet'].str.normalize('NFKD').str.encode('ascii',
                                                                                     errors='ignore').str.decode(
        'utf-8')
    master_store['STORE TYPE'] = master_store['STORE TYPE'].str.strip()
    master_store['STORE TYPE'] = master_store['STORE TYPE'].str.replace('  ', ' ')
    master_store['STORE TYPE'] = master_store['STORE TYPE'].str.replace('–', '-')

    list_col = [
        'Sales Region ID', 'Sales Region', 'Customer', 'Digital/ Manual',
        'Channel Group', 'Area/Customer Group', 'Distributor/Customer', 'Banner', 'Channel ID', 'Channel',
        'Sub Channel ID', 'Sub Channel', 'Field Execution Manager', 'CBM/ACDM', 'FEE and Store Ops/MAE',
        'Agency Code', 'User ID', 'User'

    ]

    for a in list_col:
        print('columns in store master ', a)
        master_store['{}'.format(a)] = master_store['{}'.format(a)].str.strip()
        master_store['{}'.format(a)] = master_store['{}'.format(a)].str.replace('  ', ' ')
        master_store['{}'.format(a)] = master_store['{}'.format(a)].str.replace('–', '-')

    master_store = master_store[['Outlet ID', 'Outlet', 'Digital/ Manual',
                                 'Banner',
                                 'STORE TYPE', 'User', 'Distributor/Customer',
                                 'Agency Code', 'Customer', 'Trade Format',
                                 'FEE and Store Ops/MAE', 'Sales Region',
                                 'Channel Group', 'Channel', 'Sub Channel',
                                 'CBM/ACDM', 'Area/Customer Group']]

    master_store.rename(
        columns={'Outlet ID': 'Shop Id', 'Outlet': 'Shop Name', 'Digital/ Manual': 'Shop Type',
                 'Banner': 'Shop Address',
                 'STORE TYPE': 'Retailer', 'User': 'Column 1', 'Distributor/Customer': 'Column 2',
                 'Agency Code': 'Column 3', 'Customer': 'Column 4', 'Trade Format': 'Column 5',
                 'FEE and Store Ops/MAE': 'Column 6', 'Sales Region': 'Column 7',
                 'Channel Group': 'Column 8', 'Channel': 'Column 9', 'Sub Channel': 'Column 10',
                 'CBM/ACDM': 'Column 11', 'Area/Customer Group': 'Column 12'}, inplace=True)

    master_store['Shop Id'] = master_store['Shop Id'].astype(str) + month
    master_store['Shop Name'] = master_store['Shop Name'] + month
    master_store['Shop Type'] = master_store['Shop Type'].str.title()

    master_store.to_csv(os.path.join(output_file_path, 'store_master_new.csv'), index=False)
    print('Store master created')
    return 'Store master created'


def master_func():
    # read all input files
    store_master = pd.read_csv(os.path.join(input_file_path, 'DPS_SEA_Store_Master.csv'), header=0)
    # osa_npd = pd.read_csv(os.path.join(input_file_path, 'DPS_PH_OSA_NPD_template_MAY_01052022_final.csv'), header=0)
    audit_check_list = pd.read_csv(os.path.join(input_file_path, 'DPS_SEA_Adt_Chklist.csv'), header=0)
    survey_master = pd.read_csv(os.path.join(input_file_path, 'DPS_SEA_Survey_Master.csv'), header=0)
    old_new_sku_mapping = pd.read_csv(input_file_path + '/old-new mapping.csv')
    old_new_sku_mapping = old_new_sku_mapping[['old_group_name', 'old_sku_name', 'new_group_name', 'new_sku_name']]

    # create shop master
    result_store_master = prepare_store_master_reformation_data(store_master)
    print(result_store_master)

    # create data frame
    store_df, store_df1 = prepare_store_master(store_master)
    audit_df, audit_df1 = prepare_audit_check_list(audit_check_list)
    prepare_survey_master(survey_master)

    # create beat plan from store_df
    # Done and tested
    beat_plan_df = create_beat_plan(store_master)
    beat_plan_df.to_csv(os.path.join(output_file_path, 'beat_plan.csv'), index=False)

    # # create sku_master
    # done and tested
    # TO CREATE SKU MASTER  UNCOMMENT  LINE NO 490 T0 499 LOOP SECTION
    test_final_4 = create_sku_master(store_df1, audit_df1, old_new_sku_mapping)

    # create  survey_master
    # Done and tested 1 issue found
    create_survey_master(survey_master, test_final_4, audit_df1)

    return 'successfully executed'


final_store_df = (master_func())
print(final_store_df)
