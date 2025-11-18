import streamlit as st
from datetime import datetime
from sqlalchemy import text

if st.session_state['username'] != 'ACE' or 'username' not in st.session_state:
    st.write('Please login on the main page.')

else:
    if 'clicked_see_activities_update' not in st.session_state or not st.session_state['clicked_see_activities_update']:
        st.session_state['clicked_see_activities_update'] = False

    def click_see_activities_update():
        st.session_state['clicked_see_activities_update'] = True

    st.title('Update an already registered activity')
    
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
                pa = st.selectbox('Which activitity do you want to revise?', df.index.tolist())
        
                st.write('Update form below, then click submit.')
                with st.form('Update_form', clear_on_submit=True):
                    title = st.text_input('Short title', value=df.loc[pa, 'title'], help='Write a short title of the activity.')
                    cid = st.text_input('CID', value=df.loc[pa, 'cid'], help='Input your Chalmers ID.')
                    name = st.text_input('Your name', value=df.loc[pa, 'name'], help='Write your name.')
                    divisionlist = ['']+st.session_state['divs']
                    try:
                        ix1 = divisionlist.index(df.loc[pa, 'division'])
                    except:
                        ix1 = 0
                    division = st.selectbox('Division(s)', divisionlist, index=ix1, help='Choose your division.')
                    catlist = ['']+st.session_state['cats']
                    try:
                        ix2 = catlist.index(df.loc[pa, 'category'])
                    except:
                        ix2 = 0
                    category = st.selectbox('Type of activity', catlist, index=ix2, help='See definitions and examples on the first page.')
                    thisy = datetime.now().year
                    time = st.slider('Year(s) the activity was done', min_value=thisy-10, max_value=thisy+4, value=[int(df.loc[pa, 'start_time']),int(df.loc[pa, 'end_time'])])
        
                    comment = st.text_area('Brief description', value=df.loc[pa, 'comment'], help='Write what you did.')
                    links = st.text_area('Links (if available)', value=df.loc[pa, 'links'], help='Provide links to webpages or articles.')
        
                    submit = st.form_submit_button('Submit')
                    if submit:
                        now = datetime.now()
                        mo = str(now.month)
                        if len(mo) == 1:
                            mo = '0'+mo
                        da = str(now.day)
                        if len(da) == 1:
                            da = '0'+da
                        ts = str(now.year)+'-'+mo+'-'+da+'-'+str(now.hour)+'-'+str(now.minute)
                        inputlist = [cid, name, category, division, title, comment, links, str(time[0]), str(time[1]), ts]
        
                        inputs = {}
                        for field, value in zip(st.session_state['headings'], inputlist):
                            inputs[field] = value
                    
                        placeholders = ", ".join([f":{field}" for field in st.session_state['headings']])
                        columns = ", ".join(st.session_state['headings'])
                        values = {field: inputs[field] for field in st.session_state['headings']}
        
                        # Fields to update (excluding the primary key)
                        update_fields = st.session_state['headings']
                        set_clause = ", ".join([f"{field} = :{field}" for field in update_fields])
                        
                        # Add the ID to the values dictionary
                        values['id'] = int(df.loc[pa, 'id'])
                        
                        # Execute the update
                        with conn.session as s:
                            s.execute(text(f'UPDATE utildb SET {set_clause} WHERE id = :id'), values)
                            s.commit()
                        st.success("Entry updated successfully!")
        except Exception as e:
            st.error(f"Database error: {e}")
