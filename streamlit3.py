## all the libraries we used for data enhancement
import streamlit as st #Create an online dashboard
import numpy as np
import pandas as pd ##data table manipulation 
import matplotlib as mpl #plot the data
import matplotlib.pyplot as plt #plot the data
from wordcloud import WordCloud, ImageColorGenerator #Generate word cloud of data
from PIL import Image #load graph images
from sqlalchemy import create_engine #establish connection with database
import cx_Oracle
import json #allow to transferring data 
import plotly.express as px #plot 
import SessionState #optimisaiton of the dashboard

#all the data stored at the start of the dashboard in order to optimize resources
session_state = SessionState.get(imageClusters=0,figPays = 0,dfAuteurPaysCount=0,createview =0,dicoPaysCode=0,start =1,a=0, b=0,c=0) 


if session_state.start ==1 : #this part is only executed when the dashboard is launched  
    engine = create_engine('oracle://....@telline.univ-tlse3.fr:1521/etupre')
    connection = engine.raw_connection() #establish connection with database
    # Check if account exists 
    try:
        cursor = connection.cursor()
        cursor.execute("select level n from dual connect by level < 10") #try a random request
        for row in cursor:
            print(row)

        cursor.close()
        connection.commit()
    finally:
        connection.close() #close connection

    def create_view(requete,colonnes=[]) :

        """ Documentation
      This function returns a Data Frame

      Parameters :
      requete : the requete SQL

      colonnes : The columns of data frame
      """
        connection = engine.raw_connection()
        cursor = connection.cursor()
        if len(colonnes) ==0 :
            return pd.DataFrame.from_records(cursor.execute(requete))
        else:
            return pd.DataFrame.from_records(cursor.execute(requete),columns=colonnes)


    with open("dictionnaireCodePays.json", 'r') as f: #load the dictionary containing the country codes
        dictPaysCode = json.load(f)
    session_state.dicoPaysCode = dictPaysCode # store this dictionary on a session variable
    session_state.createview = create_view # store create view function on a session variable

#----------------------------------------PLOT AUTHOR DISTRIBUTION--------------------------------------
    requete = 'select Nom_pays,count(*) from Auteur GROUP BY Nom_pays'
    dfAuteurPaysCount = session_state.createview(requete,['pays','count'])
    dfAuteurPaysCount['code_pays'] = [dictPaysCode[i] if i in list(dictPaysCode.keys()) else ''  for i in dfAuteurPaysCount['pays']]
    session_state.dfAuteurPaysCount = dfAuteurPaysCount

    df = px.data.gapminder().query("year==2007") #get list of countries
    session_state.figPays = px.choropleth(session_state.dfAuteurPaysCount[session_state.dfAuteurPaysCount['code_pays'].isna()==False], locations="code_pays",
                    color="count", 
                    hover_name="pays", 
                    color_continuous_scale=px.colors.sequential.Plasma)
#-------------------------------------------------------------------------------------------------------------------
session_state.start =0

st.title('PROJET DASHBOARD')

#displays the three main parts of our dashboard 
col1, col2,col3 = st.beta_columns(3)
with col1:
    bouttonAuteurs = st.button("Analyse des Auteurs")
with col2:
   bouttonMotsCles = st.button("Analyse des mots clés")
with col3:  
   bouttonAnalyses = st.button("Analyse des titres")





if (bouttonAuteurs or session_state.a) and not (bouttonMotsCles) and not(bouttonAnalyses)  : # if you click on the author part  
    session_state.b=False
    session_state.a=True
    session_state.c=False
    #------------------------------------------------------------------DISPLAY FAVORITE NETWORK FOR EACH COUNTRIES--------------------------------------------------
    requete = "select count(*),auteur.nom_pays,motscle from ecrire,auteur,article,contenir where ecrire.id_a = article.id_a and ecrire.id_auteur=auteur.id_auteur and contenir.id_a=article.id_a and contenir.motscle in ('facebook','snapchat','twitter','instagram','reddit','whatsapp','telegram','tiktok','') group by (auteur.nom_pays,motscle) order by auteur.nom_pays,count(*) desc"
    dfReseauParPays = session_state.createview(requete,['count','pays','mot']) #Queries the database 
    dfReseauParPays['code_pays'] = [session_state.dicoPaysCode[i] if i in list(session_state.dicoPaysCode.keys()) else ''  for i in dfReseauParPays['pays']]  #orders the data 
    dfReseauPays = dfReseauParPays.groupby('pays').first()
    df = px.data.gapminder().query("year==2007")
    figReseauxParPays= px.choropleth(dfReseauPays, locations="code_pays",
                    color="mot", 
                    hover_name="mot", 
                    color_continuous_scale=px.colors.sequential.Plasma)

    st.subheader('Repartition des Auteurs par Pays')
    st.plotly_chart(session_state.figPays) 
    st.subheader('Reseau le plus cité par Pays')
    st.plotly_chart(figReseauxParPays)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------


if (bouttonMotsCles or session_state.b) and not(bouttonAuteurs) and not(bouttonAnalyses): #if you click on the key words part  
    st.subheader('Analyse Mots clés')
    #Choice a social network for analysis
    mot = st.sidebar.selectbox(
    'Choissiez un reseau',
     ('facebook', 'twitter', 'instagram','snapchat'))
    dico = {}
    #-------------------------------------------------------------- RELATED KEY WORDS FOR EACH SOCIAL NETWORK---------------------------------------------
    requeteMotsAssociesResaux = "select  count(*),motscle from contenir where id_a in  (select id_a from contenir where motscle='"+mot+"') and motscle not in ('internet','site','use','pinterest','online','sites','network','whatsapp','social networks','twitter','snapchat','social newtork','networking','social network','social media','social','media','instagram','facebook','"+mot+"')  group by (motscle) order by (count(*)) desc"
    nuagedeMotsDf = session_state.createview(requeteMotsAssociesResaux).head(30) #Queries the database
    for i in range(nuagedeMotsDf.shape[0]) :
        dico[nuagedeMotsDf[1].iloc[i]] = nuagedeMotsDf[0].iloc[i]
    wc = WordCloud() 
    wc.generate_from_frequencies(dico) #Generate the word cloud associated with request return
    fig, ax = plt.subplots(figsize=(20,20))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    session_state.a=False
    session_state.b=True
    session_state.c=False

    bar, ax = plt.subplots( figsize=(15,10))
    names = nuagedeMotsDf[1].head(10) 
    values = nuagedeMotsDf[0].head(10) #Generate the bar plot cloud associated with request return
    plt.bar(names, values)  
    plt.show() 
    st.pyplot(fig)
    st.pyplot(bar)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------

    def word_occurrence(word, year):
        """ Documentation
      This function returns the number of times the words appear 

      Parameters :
      word : the word
      year :the year 
        """
        requete = "select MotsCle, count(MotsCle) from Contenir,Article WHERE  MotsCle LIKE '" + str(word)+ "%' and Date_publi LIKE '"+ str(year) + "%' and Contenir.ID_A = Article.ID_A GROUP BY (MotsCle)"
        return session_state.createview(requete).sum()[1]
    def word_evolution(word):
        """ Documentation
      This function returns the evolution of words according to the year

      Parameters :
      word : the word to look for
        """
        list_word_occurrence = []
        years = ['2015', '2016', '2017', '2018', '2019', '2020', '2021']

        for y in years:
            occurrence = word_occurrence(word, y)
            list_word_occurrence.append(occurrence)

        df = pd.DataFrame({
            'Yeas': years,
            'word_occurrence': list_word_occurrence
        })
        
        return df
#-------------------------------------------------------PLOT KEY WORDS EVOLUTION----------------------------------------------
    w = 'mental health'
    w = st.text_input("Affichez l'évolution du mot : ", 'mental health,communication') #Choice words to show year's evolution
    figEvolutionWords, ax = plt.subplots() 
    
    if ',' in w : # if you want to compare the evolution of several words 
        motsCles = w.split(',')
        for i in motsCles :
            df_word_evolution = word_evolution(i)
            plt.plot(df_word_evolution['Yeas'],df_word_evolution['word_occurrence'],'o-',label=i)
    else :
        df_word_evolution = word_evolution(w)
        figEvolutionWords, ax = plt.subplots() 
        plt.plot(df_word_evolution['Yeas'],df_word_evolution['word_occurrence'])
    

    plt.yticks([])
    plt.legend()
    st.pyplot(figEvolutionWords)
#----------------------------------------------------------------------------------------------------------------------------------

if (bouttonAnalyses or session_state.c) and not(bouttonMotsCles) and not(bouttonAuteurs) : #if you click on the title part  
    #load clsuter images of each topic
    imageClusters = Image.open('clusters.png')
    #load csv contenint title positivity
    art_tile = pd.read_csv('pos_art_tile_by_year.csv')
    positivitydf = art_tile.groupby('Date').mean()
    positivitydf = positivitydf[positivitydf.index!=' ']
    figpositivity, ax = plt.subplots(figsize=(4,2))
    listeIndex = positivitydf.index
    #plot evolution of positivity through years
    plt.plot(listeIndex,positivitydf['positivity'],'o-',label="positivité")
    plt.legend()

    st.pyplot(figpositivity)
    #Pick a cluster number
    cluster = st.sidebar.selectbox(
    'Choissiez un sujet',
     (0,1, 2, 3,4,5,6,7))
     
     # Display of circular diagrams for the 8 clusters
    if cluster == 0:
        labels = 'media', 'research', 'study', 'health', 'life', 'online', 'review', 'analysis', 'role', 'impact'
        sizes = [462,346,329,279,253,250,246,230,228,226]
    if cluster == 1:
        labels = 'review', 'systematic', 'meta', 'analysis', 'covid', 'pandemic', 'health', 'research', 'outcomes', 'impact'
        sizes = [154,117,44,42,30,29,28,22,15,15]
    if cluster == 2:
        labels = 'smart', 'cities', 'chapter', 'innovation', 'citizens', 'based', 'role', 'data', 'security', 'engagement'
        sizes = [18,16,4,3,2,2,2,2,2,2]
    if cluster == 3:
        labels = 'analysis', 'network', 'using', 'based', 'research', 'study', 'networks', 'case', 'media', 'health'
        sizes = [48,47,7,5,5,4,4,4,4,3]
    if cluster == 4:
        labels = 'older', 'adults', 'among', 'network', 'health', 'well', 'support', 'study', 'life','perceived'
        sizes = [46,46,9,8,7,6,6,5,5,4]
    if cluster == 5:
        labels = 'science', 'research', 'america', 'infrastructure', 'north', 'teaching', 'cooperative', 'ecosystem', 'provided', 'urban'
        sizes = [3,3,3,3,3,2,1,1,1,1]
    if cluster == 6:
        labels = 'research', 'review', 'agenda', 'tourism', 'health', 'literature', 'media', 'international', 'annals', 'curated'
        sizes = [18,11,9,6,3,3,2,2,2,2]
    if cluster == 7:
        labels = 'self', 'esteem', 'internet', 'problematic', 'among', 'media', 'mediating', 'role', 'adolescents', 'study'

        sizes = [26, 20, 15, 12,7, 7, 6, 5, 5, 5]
    figpTopicClusters, ax = plt.subplots(figsize=(4,4))
    plt.pie(sizes, labels=labels,
        autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('classe '+str(cluster))
    plt.show()


    # import data motsApresImpact
    clean_articles = pd.read_csv('motsApresImpact.csv')
    # words deletion covid, media and online in the data frame
    clean_articles.drop(clean_articles[clean_articles["social"]=="covid"].index, inplace = True)
    clean_articles.drop(clean_articles[clean_articles["social"]=="media"].index, inplace = True)
    clean_articles.drop(clean_articles[clean_articles["social"]=="online"].index, inplace = True)
    dic = clean_articles.to_dict()
    new_dic = {}
    list_keys = list(dic['social'].values())
    list_values = list(dic['83'].values())
    for i in range(len(list_keys)):
        new_dic[list_keys[i]] = list_values[i]
    wc = WordCloud()
    #generate word cloud
    wc.generate_from_frequencies(new_dic)
    figNuage, ax = plt.subplots(figsize=(20,20))
    plt.imshow(wc, interpolation="bilinear")


    
    
    
    

    st.pyplot(figpTopicClusters)
    st.image(imageClusters, caption='représentation des 8 différents sujets',width =800)


    
    st.pyplot(figNuage)
    def get_year(date):
        """ Documentation
      This function returns the year

      Parameters :
      date : the date
      """
        return ((date[:4]))
    requete = "SELECT Date_publi, Titre_art FROM Article"
    df_contain_title = session_state.createview(requete)
    df_contain_title.columns = ['date', 'art_title']
    df_contain_title.drop(df_contain_title[df_contain_title['date'] == ' '].index, inplace = True)
    # Kepping the year of a date 
    df_contain_title['date'] = df_contain_title['date'].apply(get_year)
    def word_occur_title(word, df, col_nam):
        """ Documentation
      This function returns the number of times the words appear in the title 

      Parameters :
      requete : the requete SQL
      word : the word
      df : The data frame
      col_nam : the name of the column
        """
        n = len(df)
        list_count = []
        for i in range(n):
            w_count = df[str(col_nam)].iloc[i].count(word)
            list_count.append(w_count)
            
        return list_count
    #pick a word to see his occurence's evolution through years
    w = st.text_input("Affichez l'évolution du mot : ", 'mental health,communication')

    figEvolutiontitle, ax = plt.subplots() 
    df_contain_title['word'] = word_occur_title(w, df_contain_title,'art_title')
    df_word_count = df_contain_title.groupby('date').sum()
    
    #plot all words'evolution to compare them 
    if ',' in w :
        motsCles = w.split(',')
        for i in motsCles :
            df_contain_title['word'] = word_occur_title(i, df_contain_title,'art_title')
            df_word_count = df_contain_title.groupby('date').sum()

            plt.plot(df_word_count.index,df_word_count['word'],'o-',label=i)
    else :
        df_contain_title['word'] = word_occur_title(w, df_contain_title,'art_title')
        df_word_count = df_contain_title.groupby('date').sum()
        plt.plot(df_word_count.index,df_word_count['word'],'o-',label=w)
    

    plt.legend()

    st.pyplot(figEvolutiontitle)
    session_state.a=False
    session_state.b=False
    session_state.c=True

       



#st.subheader('Repartion des auteurs')
#st.plotly_chart(fig2)
