import streamlit as st
import bcrypt
from sqlalchemy import text
import numpy as np

def verify_user(username, password):
    try:
        conn = st.connection('neon', type='sql')

        query = text('SELECT password FROM users WHERE username = :username')
        with conn.session as s:
            result = s.execute(query, {'username': username}).fetchone()
            if result:
                stored_hash = result[0]
                return bcrypt.checkpw(password.encode(), stored_hash.encode())
    except Exception as e:
        st.error(f"Database error during login: {e}")

    return False


# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

#Lists used throughout session
st.session_state['divs'] = ['Applied Acoustics', 'Architectural Theory and Methods', 'Building Design',
                'Building Services Engineering', 'Building Technology', 'Construction Management',
                'Geology and Geotechnics', 'Structural Engineering', 
                'Urban Design and Planning', 'Water Environment Technology']
st.session_state['cats'] = ['Research collaboration', 'Competence development', 'Technical services', 'Design and development',
                'Commercialization and startups', 'Expert advise', 'Information dissemination', 'Engagement in networks', 'Other']
st.session_state['headings'] = ['cid', 'name', 'category', 'division', 
                                  'title', 'comment', 'links', 'start_time', 'end_time', 'reg_time']

#Front page
#emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Utilization at ACE', page_icon=':boomerang:', layout='centered')
st.title('Welcome to the utilization database of ACE!')

# Login form
if not st.session_state['authenticated']:
    st.title('Login')
    username_input = st.text_input('Username')
    password_input = st.text_input('Password', type='password')
    if st.button('Log in'):
        if verify_user(username_input, password_input):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username_input
            st.rerun()
        else:
            st.error('Invalid username or password')

# Main app
elif st.session_state['username'] == 'ACE':
    st.title('Welcome ACE user')

    with st.sidebar:
        st.write('Logged in as ACE user')
        if st.button('Log out'):
            st.session_state['authenticated'] = False
            st.session_state['username'] = ''
            st.rerun()

    st.markdown('Here you can:')
    st.markdown('- **Register** a utilization activity')
    st.markdown('- **Update** information about a previously registered activity')
    st.markdown('- **Delete** a previously registered entry')
    st.markdown('- **Download** a table with your utilization activities')
    st.markdown('- **View** statistics for ACE')
    st.markdown('Choose what you want to do in the sidebar menu.')

    st.subheader('We categorize utilization activities as follows:')
    st.markdown('''
                - **Research collaboration**. For example, you collaborate with actors from industry or other societal sectors in a research project.
                - **Competence development**. For example, you provide a course to people from the industry or support people's competence development in some other way. (Note this does not include our regular education of Chalmers students)
                - **Technical services**. For example, you provide expert services such as laboratory analyses for people outside of the university.
                - **Design and development**. For example, you contribute to the development of an urban area.
                - **Commercialization and startups**. For example, you startup a company based on your innovation.
                - **Expert advise**. For example, you provide advise to the government, contribute to international reports such as IPCC, contribute to development of new industry standards, etc.
                - **Information dissemination**. For example, you participate in the public debate, present your research to the public, or give a presentation targeting a specific societal sector.
                - **Engagement in networks**. You are part of a network or organization that brings together different researchers and, possibly, stakeholders from society.
                - **Other**. This is for utilization activities that you don't think fit into the categories above.
                ''')
    
elif st.session_state['username'] == 'admin':
    with st.sidebar:
        st.write('Logged in as admin')
        if st.button('Log out'):
            st.session_state['authenticated'] = False
            st.session_state['username'] = ''
            st.rerun()

    try:
        conn = st.connection('neon', type='sql')
        df = conn.query('SELECT * FROM utildb;', ttl='0m')

        if df.empty:
            st.write('There are no entries in the database.')
        else:
            st.write(f'There are {len(df)} entries in the database.')
            st.dataframe(df[['cid', 'title', 'category', 'reg_time']])

            @st.cache_data
            def convert_df(df0):
                return df0.to_csv(sep='\t').encode('latin1')

            df['index'] = np.arange(len(df)) + 1
            df.set_index('index', inplace=True)
            tsv = convert_df(df[st.session_state['headings']])
            st.download_button('Download', data=tsv, file_name='Entire_utilisation_database.txt')
    except Exception as e:
        st.error(f"Database error: {e}")
