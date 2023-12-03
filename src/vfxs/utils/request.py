#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8

def paras_disposition_form_headers(headers):
    content_disposition = None
    for header_key, header_value in headers.raw:
        if header_key == b'content-disposition':
            content_disposition = header_value.decode()
    if not content_disposition:
        raise ValueError(f'请求头中不含有content-disposition信息')

    result = dict()
    for item in content_disposition.split(';'):
        if '=' not in item:
            continue
        item = item.strip()
        k, v = item.split('=')
        result[k] = v.strip('"')
    return result
