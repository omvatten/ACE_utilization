import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import plotly.express as px


st.title('Statistics on the ACE utilization database')

try:
    conn = st.connection('neon', type='sql')
    st.cache_data.clear()
    df = conn.query('SELECT * FROM utildb;', ttl='0m')
    if df.empty:
        st.write('There are no entries in the database.')
    else:
        st.write('There are '+str(len(df))+' entries in the database.')
        st.markdown('- '+str(len(df['cid'].unique()))+' people have made entries.')
        st.markdown('- '+str(len(df.loc[df['division'].notna(), 'division'].unique()))+' divisions are represented.')
        st.markdown('- '+str(len(df['category'].unique()))+' utilization categories are included.')

        df['date'] = df['reg_time'].str[:10]
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        
        cont1 = st.container()
        with cont1:
            st.subheader('When were items entered into the database?')
            start = datetime(2024, 1, 1)
            now = datetime.now()
            mo_diff = relativedelta(now, start).months + 12*relativedelta(now, start).years
            if relativedelta(now, start).days > 0:
                mo_diff += 1
            dfp = pd.DataFrame(pd.NA, index=range(mo_diff), columns=['Month', 'New entries'])
            for i in range(mo_diff):
                this_month = start + relativedelta(months=i)
                dfp.loc[i, 'Month'] = this_month
                antal = len(df[(df['date']>=this_month)&(df['date']<this_month+relativedelta(months=1))].index)
                dfp.loc[i, 'New entries'] = antal
    
            fig = px.bar(dfp, x='Month', y='New entries')
            fig.update_layout(xaxis_tickformat = '%b %Y')
            fig.update_xaxes(nticks = len(dfp))
            st.plotly_chart(fig)
    
        cont2 = st.container()
        with cont2:
            st.subheader('When were the activities carried out?')

            expanded_rows = []
            for _, row in df.iterrows():
                start = int(row['start_time'])
                end = int(row['end_time'])
                for year in range(start, end + 1):
                    new_row = row.copy()
                    new_row['year'] = year
                    expanded_rows.append(new_row)
            dfe = pd.DataFrame(expanded_rows)

            dfe.loc[~dfe['category'].isin(st.session_state['cats']), 'category'] = 'Unknown'
            dfe.loc[~dfe['division'].isin(st.session_state['divs']), 'division'] = 'Unknown'
            dfe['cy'] = dfe['category']+dfe['year'].astype(int).astype(str)
            dfe1 = dfe[['cy', 'division']].groupby('cy').count()
            dfe1.columns = ['Count']
            dfe1[['Year', 'Category']] = dfe[['year', 'category', 'cy']].groupby('cy').first()
            fig = px.bar(dfe1, x='Year', y='Count', color='Category', category_orders={'Category':st.session_state['cats']})
            st.plotly_chart(fig)
        
        cont3 = st.container()
        with cont3:
            st.subheader('In which divisions were the activities carried out?')
            dfp = df[['division', 'category', 'cid']]
            dfp.loc[~dfp['category'].isin(st.session_state['cats']), 'category'] = 'Unknown'
            dfp.loc[~dfp['division'].isin(st.session_state['divs']), 'division'] = 'Unknown'
            dfp['dc'] = dfp['division'] + dfp['category']
            dfp2 = dfp.groupby('dc').count()
            dfp2[['division', 'category']] = dfp[['division', 'category', 'dc']].groupby('dc').first()
            dfp2[['Count', 'Division', 'Category']] = dfp2[['cid', 'division', 'category']]
            fig = px.bar(dfp2, x='Division', y='Count', color='Category', category_orders={'Category':st.session_state['cats']})
            st.plotly_chart(fig)

        cont4 = st.container()
        with cont4:
            st.subheader('Click to show a random entry in the database.')
            showentry = st.button('Show an entry')
            if showentry:
                key = random.choice(df.index.tolist())
                for c in ['name', 'title', 'division', 'category', 'comment', 'links']:
                    if isinstance(df.loc[key, c], str):
                        st.write(c.upper()+ ': '+df.loc[key, c])

except Exception as e:
    st.error(f"Database error: {e}")

