import yaml
import streamlit as st
import streamlit_authenticator as stauth
from database_functions import get_users_products, get_price_history

st.set_page_config(page_title="Discount Tracker", layout='wide')

st.markdown(
    """
<style>
.css-vcxpl8 {
background-color: #093472;
border-radius: 12px;
border: #093472;


}

.css-vcxpl8:hover {
    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
    background-color: #256BD1;
}

button {
    height: auto;
    padding-top: 10px !important;
    padding-bottom: 10px !important;

}


</style>
""",
    unsafe_allow_html=True,
)

with open('login_config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

st.title("Discount Tracker")

name, authentication_status, user_name = authenticator.login('Login', 'main')


def convert_price_history_to_df(price_history):
    """
    Function converts price history to the dataframe fot graphs using.
    :param price_history: price history of some product.
    :return: dataframe with data.
    """
    df = {}
    for price in price_history:
        df[price[0]] = price[1]
    return df


def draw_graph(tg_id, product_name, column):
    """
    Function draws graph of prices for curtain product.
    :param tg_id: telegram id of the user.
    :param product_name: name of the product.
    :param column: columns in streamlit site.
    :return:
    """
    price_history = get_price_history(tg_id, product_name)
    for site in price_history.keys():
        column.subheader(price_history[site]['shop'])
        if len(price_history[site]['price_history']) == 0:
            column.error('No date of price fot this product yet :<')
        else:
            df = convert_price_history_to_df(price_history[site]['price_history'])
            column.bar_chart(df)


if authentication_status:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.divider()
    st.subheader('Products prices history')
    st.text('Choose one of your products:')

    col1, col2 = st.columns(2)
    products = sorted(list(set(get_users_products(user_name))))
    for product in products:
        col1.button(product , on_click=draw_graph, args=(user_name, product, col2), type='primary',
                    use_container_width=True)
        

elif authentication_status is False:
    st.error('Username/password is incorrect')

elif authentication_status is None:
    st.warning('Please enter your username and password')
