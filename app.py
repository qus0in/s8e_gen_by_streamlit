import streamlit as st
import requests
import qrcode

st.set_page_config(page_title='S8l Generator', page_icon='🔗')

st.title('S8l Genaerator')

BASE_URL = 'https://s8l.me'

st.text_input('API URL', key='api_url')
st.text_input('API Key', key='api_key')

def get_headers():
    return {
        'x-api-key': st.session_state.api_key,
        'Content-Type': 'application/json',
    }

def put_data(table_name, item):
    data = {
        "TableName": table_name,
        "Item": item,
    }
    response = requests.post(
        st.session_state.api_url,
        json=data,
        headers=get_headers())
    response.raise_for_status()

def get_data(table_name, key_name, key_value):
    params = {
        "table_name": table_name,
        "key_name": key_name,
        "key_value": key_value,
    }
    response = requests.get(
        st.session_state.api_url,
        params=params,
        headers=get_headers())
    response.raise_for_status()
    return response.json()

def generate():
    if not st.session_state.get('api_url', '') and not st.session_state.get('api_key', ''):
        return ('', 'Please input API URL and API Key')
    shorten = st.session_state.shorten_url
    origin = st.session_state.origin_url
    if not shorten:
        return ('', 'Please input shorten URL')
    shorten_data = get_data('S8L_TO_URL', 'shorten', shorten)
    if shorten_data:
        return (shorten_data, 'Shorten already exists')
    if not origin:
        return ('', 'Please input origin URL')
    origin_data = get_data('URL_TO_S8L', 'origin', origin)
    if origin_data:
        return (origin_data, 'Origin already exists')
    item = {
        'origin': {'S': origin},
        'shorten': {'S': shorten},
    }
    put_data('S8L_TO_URL', item)
    put_data('URL_TO_S8L', item)
    return (item, 'Success')

def on_click():
    data, msg = generate()
    st.session_state.res_msg = msg
    st.session_state.res_data = data.get('Item', {}) if data else {}

with st.form(key='form'):
    cols = st.columns(2)
    with cols[0]:
        st.text_input('Shorten URL', key='shorten_url')
    with cols[1]:
        st.text_input('Origin URL', key='origin_url')
    st.form_submit_button('Generate',
                          on_click=on_click)

if st.session_state.get('res_msg', ''):
    st.info(st.session_state.res_msg)
cols = st.columns(2)
if st.session_state.get('res_data', {})\
    and st.session_state.get('res_msg', {}) != 'Success':
    with cols[0]:
        st.subheader('Shorten URL')
        st.write(f'{BASE_URL}/{st.session_state.res_data["shorten"]["S"]}')
        st.subheader('Origin URL')
        st.write(st.session_state.res_data['origin']['S'])
    with cols[1]:
        st.subheader('QR Code')
        st.image(qrcode.make(f'{BASE_URL}/{st.session_state.res_data["shorten"]["S"]}')._img,
                 width=200)