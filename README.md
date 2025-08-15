# Annotation app


## Development
1. Enviroment variables
    - To get started you want to add a `.env` file containg `DB_URL` and `TEST_DB_URL` inside of the `/backend` folder which are used to connect to the database and test database respectively.
2. Installing libraries
    - In the `/frontend` folder run the command `pip install -r requirements.txt` to install the libraries for the (streamlit) frontend
    - Then in the `/backend` folder run `npm i` to install the packages for the (express) backend
3. Running the app
    - To run the streamlit frontend run `streamlit run login.py` in the `/frontend` folder
    - To run the backend run `npm start` in the `/backend` folder
    
4. Testing the app
    - To run the automated tests for the backend run `npm test` in the `/backend` folder
    - You can also use the `test.rest` file inside of the `/backend/rest` folder to send requests to the backend while its running locally. You must install the vscode REST client before doing so: https://marketplace.visualstudio.com/items?itemName=humao.rest-client