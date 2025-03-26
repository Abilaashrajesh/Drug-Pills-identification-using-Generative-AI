# Drug-Pills-identification-using-Generative-AI

Steps to run the Project
step1 :
 Download the project file .

 step 2:
   Install all required packages
   pip install -r requirements.txt
   
Step 3:
    Go to google makerspace website and create a API key and also create a api key in Groq to interact with llama. If already created a API key use the same key.
    Create a new file named .env and do the following

    GOOGLE_API_KEY="abcd....."  //Your API key here
    GROQ_API_KEY='abc...'
   Run Both file seperately
    
step 4
    Run the command 
    streamlit run gemini_main.py
    streamlit run llama_main.py

