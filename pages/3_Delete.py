import streamlit as st
from sqlalchemy import text


if st.session_state['username'] != 'ACE' or 'username' not in st.session_state:
    st.write('Please login on the main page.')

else:
    if 'clicked_see_activities_update' not in st.session_state or not st.session_state['clicked_see_activities_update']:
        st.session_state['clicked_see_activities_update'] = False

    def click_see_activities_update():
        st.session_state['clicked_see_activities_update'] = True

    st.title('Delete a registered activity')
    
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
                pa = st.selectbox('Which activitity do you want to delete?', df.index.tolist())
                
                selected_id = int(df.loc[pa, 'id'])
    
                if st.button('Delete this entry'):
                    with conn.session as s:
                        s.execute(text('DELETE FROM utildb WHERE id = :id'), {'id': selected_id})
                        s.commit()
                    st.success('Entry was deleted.')
    
        except Exception as e:
            st.error(f"Database error: {e}")
