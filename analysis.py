from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langdetect import detect
import re
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.stem import WordNetLemmatizer
import warnings
import plotly.graph_objects as go
warnings.filterwarnings(action='ignore')

# df_reviews = pd.read_csv('data_files/apple_iphone_14_reviews.csv')
def generate_visualizations(df_reviews):
    df_reviews['reviews']=df_reviews['reviews'].astype('str')
    df_reviews_eng = df_reviews[df_reviews['reviews'].apply(detect)=='en']
    stop_words = set(stopwords.words('english'))
    stop_words.discard('not')
    lemmatizer = WordNetLemmatizer()

    df_reviews_eng['reviews']=df_reviews_eng['reviews'].apply(lambda text:re.sub('[^a-zA-Z0-9]',' ',text))

    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token not in stop_words]
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        preprocessed_text = ' '.join(lemmatized_tokens)
        return preprocessed_text
    df_reviews_eng['preprocessed_reviews'] = df_reviews_eng['reviews'].apply(preprocess_text)
    df_reviews_eng['titles'] = df_reviews_eng['titles'].apply(preprocess_text)
    df_reviews_eng['text_data'] = df_reviews_eng['titles']+df_reviews_eng['preprocessed_reviews']

    sid = SentimentIntensityAnalyzer()
    def get_sentiment(text):
        sentiment_scores = sid.polarity_scores(text)
        return sentiment_scores['compound']
    df_reviews_eng['sentiment_score'] = df_reviews_eng['text_data'].apply(get_sentiment)
    def get_sentiment_label(score):
        if score > 0.1:
            return 'Positive'
        elif score <0:
            return 'Negative'
        else:
            return 'Neutral'
        
    df_reviews_eng['sentiment_label'] = df_reviews_eng['sentiment_score'].apply(get_sentiment_label)
    rating_counts = df_reviews['ratings'].value_counts()
    fig_bar = go.Figure(data=[go.Bar(x=rating_counts.index, y=rating_counts.values)])
    fig_bar.update_layout(
        xaxis=dict(title='Rating'),
        yaxis=dict(title='Count'),
        title='Distribution of Review Ratings',
        plot_bgcolor='rgb(17, 17, 17)',  # Set the plot background color to dark
        paper_bgcolor='rgb(17, 17, 17)',  # Set the paper background color to dark
        font=dict(color='white'),  # Set the font color to white
    )

    # # Show the plot
    # fig_bar.show()

    sentiment_counts=df_reviews_eng['sentiment_label'].value_counts()
    labels = sentiment_counts.index.tolist()
    colors = ['green', 'red', 'gray']
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=sentiment_counts, hole=0.5, marker=dict(colors=colors))])
    fig_pie.update_layout(
        title='Sentiment Distribution',
        font=dict(size=14, color='white'),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgb(17, 17, 17)',  # Set the plot background color to dark
        paper_bgcolor='rgb(17, 17, 17)',  # Set the paper background color to dark
    )
    # fig_pie.show()

    text= ' '.join(df_reviews_eng['text_data'].values.tolist())
    wordcloud =WordCloud( width=800, height=400, background_color='black', colormap='viridis', max_words=200).generate(text)
    # plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis('off')  # Remove axis ticks and labels
    # plt.show()
    return fig_bar,fig_pie,wordcloud