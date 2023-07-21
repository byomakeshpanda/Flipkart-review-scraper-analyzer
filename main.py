import streamlit as st
import base64
import scraper
import analysis
import matplotlib.pyplot as plt
# Page layout customization
st.set_page_config(page_title='Flipkart Review Scraper', layout="wide")

# App header
header_html = """
    <style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .header-title {
        margin: 0;
        font-size: 32px;
        text-align: center;
    }
    .upload-button {
        margin-top: 20px;
        width: 200px;
        height: 50px;
    }
    </style>
    <div class="header-container">
        <h1 class="header-title">Flipkart Review Scraper and Analyzer</h1>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data = None

# Input form
product_url = st.text_input("Enter the URL", value='', max_chars=None, key=None, type='default', help=None, placeholder="Enter the URL")
submit_button = st.button("Submit")
st.markdown("Select your product: &nbsp; <a href='https://www.flipkart.com/' target='_blank'>Flipkart Homepage</a>", unsafe_allow_html=True)

#Submit button clicked
if submit_button:
    if not product_url:
        st.warning("Please enter a product URL.") #If product URL is empty
    else:
        if st.session_state.data_loaded == False:
            st.info("Loading data...")
        data, filename = scraper.get_data(product_url)
        # Update session state
        st.session_state.data_loaded = True
        st.session_state.data = data
        st.session_state.filename = filename
        st.success("Data loaded!")

# Download data option
if st.session_state.data_loaded:
    data = st.session_state.data
    csv_string = data.to_csv(index=False)

    b64_encoded = base64.b64encode(csv_string.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64_encoded}" download="{st.session_state.filename}_reviews.csv">Download Data</a>'
    st.markdown(href, unsafe_allow_html=True)

    if st.button("Check Analysis"):
        # Call the function from the analysis file to get the visualizations
        fig_bar, fig_pie, wordcloud = analysis.generate_visualizations(data)
        plt.figure(figsize=(8, 4)) 
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        # Display the visualizations
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)
        st.pyplot(plt)

