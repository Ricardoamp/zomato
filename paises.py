# Bibliotecas necessarias
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_folium import folium_static
import folium

st.set_page_config( page_title='Países', page_icon='', layout = 'wide' )

# ================================
# FUNÇÕES
# ================================

# Preenchimento do nome dos países
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name( country_id ):
    return COUNTRIES[country_id]
#--------------------------------

# Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
#--------------------------------    
    
# Criação do nome das Cores
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

#--------------------------------

#===================Inicio da Estrutura lógica do código==================

#=========================================================================
# Importar dataset
#=========================================================================
# Ler arquivo
arq = pd.read_csv( 'dataset/zomato.csv' )

# Fazer uma copia
df = arq.copy()


# ================================
# LIMPEZAS E CORREÇÕES
# ================================

# nome dos países
df['Pais'] = df['Country Code'].apply(lambda x: country_name( x ) )

# Categoria de Comida
df['Categoria'] = df['Price range'].apply( lambda x: create_price_tye( x ) )

# nome das Cores
df['cores'] = df['Rating color'].apply(lambda x: color_name( x ) )

# Coluna cuisines com o primeiro como principal
df['Cuisines'] = df.loc[:, 'Cuisines'].astype(str).apply(lambda x: x.split(",")[0])


#=========================================================================
# BARRA LATERAL
#=========================================================================
#st.sidebar.markdown('# Zomato Restaurants')
#st.sidebar.markdown( """---""")
#st.sidebar.markdown('Powered By Ricardo')

#=========================================================================
# LAYOUT DO STREAMLIT
#=========================================================================
tab1, tab2, tab3 = st.tabs(['Geral','Pais','Cidade'] )

with tab1:
    col1, col2, col3, col4, col5 = st.columns(5,gap='large')

    with col1:
        paises = len( df['Pais'].unique() )
        col1.metric('Paises Registrados', paises)
        
        
    with col2:
        cidades_registradas = len( df['City'].unique() )
        col2.metric('Cidades Registradas', cidades_registradas)

    with col3:
        restaurantes_registrados = len( df['Restaurant Name'].unique() )
        col3.metric('Restaurantes Registrados', restaurantes_registrados)

    with col4:
        tipos_de_culinaria = len( df['Cuisines'].unique() )
        col4.metric('Tipos de culinaria', tipos_de_culinaria)

    with col5:
        avaliacoes_feitas = len( df['Aggregate rating'] )
        col5.metric('Avaliações Feitas', avaliacoes_feitas)
    
    
    st.markdown("""---""")

    df_aux = df.loc[:, ['Pais', 'Latitude', 'Longitude' ] ].groupby(['Pais']).median().reset_index()

    map = folium.Map(zoom_start=11)
    for index, location_info in df_aux.iterrows():
                folium.Marker( [location_info['Latitude'],
                              location_info['Longitude']],
                            popup=location_info[['Pais']] ).add_to( map )

    folium_static(map)


    
   
    

with tab2:
    a = df['Pais'].unique()
    lista = []

    for i in a:
        lista.append(i)

    options = st.multiselect( 'Qual país deseja selecionar?', lista, default=lista )
    linhas_selecionadas = df['Pais'].isin( options )
    df = df.loc[linhas_selecionadas,:]

    with st.container():

        col1, col2 = st.columns(2)

        with col1:

            cidades = df.loc[:, ['Pais','City'] ].groupby('Pais').nunique().sort_values( ['City'], ascending = False ).reset_index()
            fig = px.bar(cidades, x = 'Pais', y = 'City', title = 'Quantidade de cidadades registradas')
            st.plotly_chart(fig, use_container_widht=True)

        with col2:
            restaurantes = df.loc[:, ['Pais','Restaurant Name'] ].groupby('Pais').nunique().sort_values( ['Restaurant Name'], ascending = False ).reset_index()
            fig = px.bar(restaurantes, x = 'Pais', y = 'Restaurant Name', title = 'Quantidade de restaurantes registrados')
            st.plotly_chart(fig, use_container_widht=True)

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            culinaria = df.loc[:, ['Pais','Cuisines'] ].groupby('Pais').nunique().sort_values(['Cuisines'], ascending=False).reset_index()
            fig = px.bar(culinaria, x = 'Pais', y = 'Cuisines', title = 'Tipos de Culinaria')
            st.plotly_chart(fig, use_container_widht=True)

        with col2:
            culinaria = df.loc[:, ['Pais','Aggregate rating'] ].groupby('Pais').count().sort_values(['Aggregate rating'], ascending=False).reset_index()
            fig = px.bar(culinaria, x = 'Pais', y = 'Aggregate rating', title = 'Classificação')
            st.plotly_chart(fig, use_container_widht=True)

with tab3:
        df1 = df.loc[:, ['City','Restaurant Name'] ].groupby('City').count().reset_index().sort_values('Restaurant Name',ascending=False)
        fig = px.bar(df1, x=df1['City'], y='Restaurant Name', labels={'x': 'Cidade', 'y': 'Número de Restaurantes'})
        fig.update_layout(title_text='Número de Restaurantes por Cidade')
        st.plotly_chart(fig, use_container_width=True)
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            df1 = df.loc[:, ['City', 'Aggregate rating']].groupby('City').mean().reset_index().sort_values('Aggregate rating', ascending=False).round(2).head(10)
            fig = px.bar(df1, x=df1['City'], y='Aggregate rating', labels={'x': 'Cidade', 'y': 'Número de Restaurantes'})
            fig.update_layout(title_text='Top 10 - Melhores Médias de avaliações')
            st.plotly_chart(fig, use_container_width=True)
            
        
        with col2:
            
            df1 = df.loc[:, ['City', 'Aggregate rating']].groupby('City').mean().reset_index().sort_values('Aggregate rating', ascending=False).round(2).tail(10)
            fig = px.bar(df1, x=df1['City'], y='Aggregate rating', labels={'x': 'Cidade', 'y': 'Número de Restaurantes'})
            fig.update_layout(title_text='Top 10 - Piores Médias de avaliações')
            st.plotly_chart(fig, use_container_width=True)
        
        