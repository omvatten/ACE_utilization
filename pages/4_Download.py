import streamlit as st
import numpy as np

if st.session_state['username'] != 'ACE' or 'username' not in st.session_state:
    st.write('Please login on the main page.')

else:
    if 'clicked_see_activities_update' not in st.session_state or not st.session_state['clicked_see_activities_update']:
        st.session_state['clicked_see_activities_update'] = False

    def click_see_activities_update():
        st.session_state['clicked_see_activities_update'] = True

    st.title('Download a text file with all your activities')
    
    cid = st.text_input('Input CID to see your registered activities', help='Input your Chalmers ID.')
    st.button('See registered activities.', on_click=click_see_activities_update)
    
    if st.session_state['clicked_see_activities_update'] and cid.strip():
        st.write('Here are registered activities for '+cid+':')

        try:
            conn = st.connection('neon', type='sql')
            query = 'SELECT * FROM utildb WHERE cid = :cid'
            df = conn.query(query, params={'cid': cid}, ttl='0m')
            if df.empty:
                st.write('Cannot find any.')
            else:
                st.dataframe(df[['title', 'category', 'reg_time']])
    
                @st.cache_data
                def convert_df(df0):
                    return df0.to_csv(sep='\t').encode('latin1')
    
                df['index'] = np.arange(len(df))+1
                df.set_index('index', inplace=True)
                cols = ['title', 'cid', 'name', 'division', 'category', 'start_time', 'end_time', 'comment', 'links', 'reg_time']
                tsv = convert_df(df[cols])
                st.download_button('Download', data=tsv, file_name=cid+'_utilization_data.txt')

        except Exception as e:
            st.error(f"Database error: {e}")
    
