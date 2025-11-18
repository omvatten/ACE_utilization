import streamlit as st
from datetime import datetime
from sqlalchemy import text

if st.session_state['username'] != 'ACE' or 'username' not in st.session_state:
    st.write('Please login on the main page.')

else:
    st.title('Register a utilization activity')
    st.markdown('Fill out the fields below.')
    
    with st.form('Reg_form', clear_on_submit=True):
    
        title = st.text_input('Short title', help='Write a short title of the activity.')
        cid = st.text_input('CID', help='Input your Chalmers ID.')
        name = st.text_input('Your name', help='Write your name.')
    
        divisionlist = ['']+st.session_state['divs']
        division = st.selectbox('Division', divisionlist, help='Choose your division.')
    
        catlist = ['']+st.session_state['cats']
        category = st.selectbox('Type of activity', catlist, help='See definitions and examples on the first page.')

        thisy = datetime.now().year
        time = st.slider('Year(s) the activity was done', min_value=thisy-10, max_value=thisy+4, value=[thisy-1,thisy])
        start_time = time[0]
        end_time = time[1]

        comment = st.text_area('Brief description of the activity', help='Write what you did.')
    
        links = st.text_area('Links (if available)', help='Provide links to webpages or articles.')

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
            inputlist = [cid, name, category, division, title, comment, links, str(start_time), str(end_time), ts]

            inputs = {}
            for field, value in zip(st.session_state['headings'], inputlist):
                inputs[field] = value
        
            placeholders = ", ".join([f":{field}" for field in st.session_state['headings']])
            columns = ", ".join(st.session_state['headings'])
            values = {field: inputs[field] for field in st.session_state['headings']}
        
            try:
                conn = st.connection('neon', type='sql')
                with conn.session as s:
                    s.execute(text(f"INSERT INTO utildb ({columns}) VALUES ({placeholders})"), values)
                    s.commit()
                st.write('Added entry to database')
            except Exception as e:
                st.error(f"Database error: {e}")

    st.subheader('We categorize utilization activities as follows:')
    st.markdown("""
                - **Research collaboration**. For example, you collaborate with actors from industry or other societal sectors in a research project.
                - **Competence development**. For example, you provide a course to people from the industry or support people's competence development in some other way. (Note this does not include our regular education of Chalmers students)
                - **Technical services**. For example, you provide expert services such as laboratory analyses for people outside of the university.
                - **Design and development**. For example, you contribute to the development of an urban area.
                - **Commercialization and startups**. For example, you startup a company based on your innovation.
                - **Expert advise**. For example, you provide advise to the government, contribute to international reports such as IPCC, contribute to development of new industry standards, etc.
                - **Information dissemination**. For example, you participate in the public debate, present your research to the public, or give a presentation targeting a specific societal sector.
                - **Engagement in networks**. You are part of a network or organization that brings together different researchers and, possibly, stakeholders from society.
                - **Other**. This is for utilization activities that you don't think fit into the categories above.
                """)

