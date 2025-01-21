#!/usr/bin/env python3

import os
import json
import time
import argparse
import requests
from xml.etree import ElementTree as ET
from collections import OrderedDict
from subprocess import Popen, PIPE
from tkinter import Tk
from tkinter.filedialog import askdirectory
import shutil
import urllib3
import sys

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 平台选择
PLATFORMS = {
    '1': 'winarm64',
    '2': 'win64',
    '3': 'osx10-64'
}

def select_platform():
    """让用户选择平台"""
    print("\nPlease select platform:")
    for key, value in PLATFORMS.items():
        print(f"[{key}] {value}")
    
    while True:
        choice = input("\nEnter your choice (1-3): ")
        if choice in PLATFORMS:
            return PLATFORMS[choice]
        print("Invalid choice. Please try again.")

# Adobe API URLs
def get_products_url(platform):
    return f'https://cdn-ffc.oobesaas.adobe.com/core/v5/products/all?_type=xml&channel=ccm,sti&platform={platform}&productType=Desktop'

ADOBE_APPLICATION_JSON_URL = 'https://cdn-ffc.oobesaas.adobe.com/core/v3/applications'

# Headers for Adobe requests
ADOBE_REQ_HEADERS = {
    'X-Adobe-App-Id': 'accc-hdcore-desktop',
    'User-Agent': 'Adobe Application Manager 2.0',
    'X-Api-Key': 'CC_HD_ESD_1_0'
}

# Driver XML template
def get_driver_xml(platform):
    return f'''<DriverInfo>
    <ProductInfo>
        <Name>Adobe {{name}}</Name>
        <SAPCode>{{sapCode}}</SAPCode>
        <CodexVersion>{{version}}</CodexVersion>
        <Platform>{platform}</Platform>
        <EsdDirectory>./{{sapCode}}</EsdDirectory>
        <Dependencies>
{{dependencies}}
        </Dependencies>
    </ProductInfo>
    <RequestInfo>
        <InstallDir>C:\\Program Files\\Adobe</InstallDir>
        <InstallLanguage>{{language}}</InstallLanguage>
    </RequestInfo>
</DriverInfo>
'''

DRIVER_XML_DEPENDENCY = '''            <Dependency>
                <SAPCode>{sapCode}</SAPCode>
                <BaseVersion>{version}</BaseVersion>
                <EsdDirectory>./{sapCode}</EsdDirectory>
            </Dependency>'''

# Session for requests with retry strategy
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
session.mount('http://', adapter)
session.mount('https://', adapter)

def dl(filename, url, max_retries=5, chunk_size=8192):
    """Download a file from a URL with retry and resume capability."""
    local_size = 0
    headers = ADOBE_REQ_HEADERS.copy()
    
    if os.path.exists(filename):
        local_size = os.path.getsize(filename)
        headers['Range'] = f'bytes={local_size}-'

    for attempt in range(max_retries):
        try:
            with session.get(url, headers=headers, stream=True, verify=False) as r:
                if r.status_code in [200, 206]:
                    total_size = int(r.headers.get('content-length', 0))
                    mode = 'ab' if local_size > 0 else 'wb'
                    
                    with open(filename, mode) as f:
                        downloaded = local_size
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                # 打印下载进度
                                percentage = (downloaded * 100) / (total_size + local_size)
                                print(f'\rProgress: {percentage:.1f}% [{downloaded}/{total_size + local_size}]', end='', flush=True)
                    print()  # 换行
                    return  # 下载成功，退出函数
                
            if r.status_code == 416:  # Range Not Satisfiable，说明文件已经下载完成
                return
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f'\nDownload failed, retrying ({attempt + 1}/{max_retries})...')
                time.sleep(1)  # 等待一秒后重试
            else:
                raise Exception(f'Failed to download after {max_retries} attempts: {str(e)}')

def r(url, headers=ADOBE_REQ_HEADERS):
    """Send a GET request and return the response text."""
    req = session.get(url, headers=headers, verify=False)
    req.encoding = 'utf-8'
    return req.text

def get_products_xml(platform):
    """Fetch and parse the products XML."""
    return ET.fromstring(r(get_products_url(platform)))

def parse_products_xml(products_xml, selected_platform):
    """Parse the products XML to extract product information."""
    cdn = products_xml.find('channel/cdn/secure').text
    products = {}
    parent_map = {c: p for p in products_xml.iter() for c in p}
    for p in products_xml.findall('channel/products/product'):
        displayName = p.find('displayName').text
        sap = p.get('id')
        version = p.get('version')
        dependencies = list(p.find('platforms/platform/languageSet/dependencies'))

        if not products.get(sap):
            products[sap] = {
                'hidden': p.find('platforms/platform').get('id') != selected_platform or parent_map[parent_map[p]].get('name') != 'ccm',
                'displayName': displayName,
                'sapCode': sap,
                'versions': OrderedDict()
            }

        products[sap]['versions'][version] = {
            'sapCode': sap,
            'version': version,
            'dependencies': [{
                'sapCode': d.find('sapCode').text, 'version': d.find('baseVersion').text
            } for d in dependencies],
            'buildGuid': p.find('platforms/platform/languageSet').get('buildGuid')
        }

    return products, cdn

def get_application_json(buildGuid):
    """Fetch the application JSON for a specific build."""
    headers = ADOBE_REQ_HEADERS.copy()
    headers['x-adobe-build-guid'] = buildGuid
    return json.loads(r(ADOBE_APPLICATION_JSON_URL, headers))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--installLanguage', help='Language code (eg. en_US)', action='store')
    parser.add_argument('-s', '--sapCode', help='SAP code for desired product (eg. PHSP)', action='store')
    parser.add_argument('-v', '--version', help='Version of desired product (eg. 21.0.3)', action='store')
    parser.add_argument('-d', '--destination', help='Directory to download installation files to', action='store')
    parser.add_argument('-p', '--platform', help='Platform (winarm64, win64, osx10-64)', action='store')
    args = parser.parse_args()

    print('=================================')
    print('= Adobe Package Generator =')
    print('=================================\n')

    # 选择平台
    selected_platform = args.platform if args.platform in PLATFORMS.values() else select_platform()
    print(f'\nSelected platform: {selected_platform}')

    print('\nDownloading products.xml\n')
    products_xml = get_products_xml(selected_platform)

    print('Parsing products.xml')
    products, cdn = parse_products_xml(products_xml, selected_platform)

    print('CDN: ' + cdn)
    print(str(len([p for p in products if not products[p]['hidden']])) + ' products found:')
    
    sapCode = None
    if args.sapCode:
        if products.get(args.sapCode):
            print('\nUsing provided SAP Code: ' + args.sapCode)
            sapCode = args.sapCode
        else:
            print('\nProvided SAP Code not found in products: ' + args.sapCode)

    print('')

    if not sapCode:
        for p in products.values():
            if not p['hidden']:
                print('[{}] {}'.format(p['sapCode'], p['displayName']))

        while sapCode is None:
            val = input('\nPlease enter the SAP Code of the desired product (eg. PHSP for Photoshop): ')
            if products.get(val):
                sapCode = val
            else:
                print('{} is not a valid SAP Code. Please use a value from the list above.'.format(val))

    product = products.get(sapCode)
    versions = product['versions']
    version = None
    if args.version:
        if versions.get(args.version):
            print('\nUsing provided version: ' + args.version)
            version = args.version
        else:
            print('\nProvided version not found: ' + args.version)

    print('')

    if not version:
        for v in reversed(versions.values()):
            print('{} {}'.format(product['displayName'], v['version']))

        while version is None:
            val = input('\nPlease enter the desired version (eg. 21.2.3): ')
            if versions.get(val):
                version = val
            else:
                print('{} is not a valid version. Please use a value from the list above.'.format(val))

    print('')

    langs = [ 'en_US', 'en_GB', 'en_IL', 'en_AE', 'es_ES', 'es_MX', 'pt_BR', 'fr_FR', 'fr_CA', 'fr_MA', 'it_IT', 'de_DE', 'nl_NL', 'ru_RU', 'uk_UA', 'zh_TW', 'zh_CN', 'ja_JP', 'ko_KR', 'pl_PL', 'hu_HU', 'cs_CZ', 'tr_TR', 'sv_SE', 'nb_NO', 'fi_FI', 'da_DK' ]
    installLanguage = None
    if args.installLanguage:
        if args.installLanguage in langs:
            print('\nUsing provided language: ' + args.installLanguage)
            installLanguage = args.installLanguage
        else:
            print('\nProvided language not available: ' + args.installLanguage)

    if not installLanguage:
        print('Available languages: {}'.format(', '.join(langs)))
        while installLanguage is None:
            val = input('\nPlease enter the desired install language, or nothing for [en_US]: ') or 'en_US'
            if val in langs:
                installLanguage = val
            else:
                print('{} is not available. Please use a value from the list above.'.format(val))

    dest = None
    if args.destination:
        print('\nUsing provided destination: ' + args.destination)
        dest = args.destination
    else:
        print('\nPlease choose the desired downloads folder.')
        Tk().withdraw()  # Hide the root tkinter window
        dest = askdirectory(title="Select Download Folder")
        if not dest:
            print('No folder selected. Exiting...')
            exit()

    print('')

    install_folder = os.path.join(dest, '{}_{}_{}'.format(sapCode, version, installLanguage))
    os.makedirs(install_folder, exist_ok=True)

    print('sapCode: ' + sapCode)
    print('version: ' + version)
    print('installLanguage: ' + installLanguage)
    print('dest: ' + install_folder)

    prodInfo = versions[version]
    prods_to_download = []
    for d in prodInfo['dependencies']:
        sap_code = d['sapCode']
        version = d['version']
        if sap_code in products and version in products[sap_code]['versions']:
            build_guid = products[sap_code]['versions'][version]['buildGuid']
            prods_to_download.append({
                'sapCode': sap_code,
                'version': version,
                'buildGuid': build_guid
            })
        else:
            print(f"Warning: Dependency '{sap_code}' with version '{version}' not found in products. Skipping.")

    prods_to_download.insert(0, { 'sapCode': prodInfo['sapCode'], 'version': prodInfo['version'], 'buildGuid': prodInfo['buildGuid'] })
    print(prods_to_download)

    print('\nPreparing...\n')

    for p in prods_to_download:
        s, v = p['sapCode'], p['version']
        product_dir = os.path.join(install_folder, s)
        app_json_path = os.path.join(product_dir, 'application.json')

        print('[{}_{}] Downloading application.json'.format(s, v))
        app_json = get_application_json(p['buildGuid'])
        p['application_json'] = app_json

        print('[{}_{}] Creating folder for product'.format(s, v))
        os.makedirs(product_dir, exist_ok=True)

        print('[{}_{}] Saving application.json'.format(s, v))
        with open(app_json_path, 'w') as file:
            json.dump(app_json, file, separators=(',', ':'))

        print('')

    print ('Downloading...\n')

    for p in prods_to_download:
        s, v = p['sapCode'], p['version']
        app_json = p['application_json']
        product_dir = os.path.join(install_folder, s)

        print('[{}_{}] Parsing available packages'.format(s, v))
        core_pkg_count = 0
        noncore_pkg_count = 0
        packages = app_json['Packages']['Package']
        download_urls = []
        for pkg in packages:
            if pkg.get('Type') and pkg['Type'] == 'core':
                core_pkg_count += 1
                download_urls.append(cdn + pkg['Path'])
            else:
                if ((not pkg.get('Condition')) or installLanguage in pkg['Condition']):
                    noncore_pkg_count += 1
                    download_urls.append(cdn + pkg['Path'])

        print('[{}_{}] Selected {} core packages and {} non-core packages'.format(s, v, core_pkg_count, noncore_pkg_count))

        for url in download_urls:
            name = url.split('/')[-1].split('?')[0]
            print('[{}_{}] Downloading {}'.format(s, v, name))
            dl(os.path.join(product_dir, name), url)

    print('\nGenerating driver.xml')

    driver = get_driver_xml(selected_platform).format(
        name=product['displayName'],
        sapCode=prodInfo['sapCode'],
        version=prodInfo['version'],
        dependencies='\n'.join([DRIVER_XML_DEPENDENCY.format(
            sapCode=d['sapCode'],
            version=d['version']
        ) for d in prodInfo['dependencies']]),
        language=installLanguage
    )

    with open(os.path.join(install_folder, 'driver.xml'), 'w') as f:
        f.write(driver)

    print('\nPackage successfully created in {}.'.format(install_folder))