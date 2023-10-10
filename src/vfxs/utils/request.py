#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8

def paras_content_disposition(content: str):
    # form-data; name="b"; filename="b.mp4"
    result = dict()
    for item in content.split(';'):
        if '=' not in item:
            continue
        item = item.strip()
        k, v = item.split('=')
        result[k] = v.strip('"')
    return result


if __name__ == '__main__':
    print(paras_content_disposition('form-data; name="b"; filename="b.mp4"'))
