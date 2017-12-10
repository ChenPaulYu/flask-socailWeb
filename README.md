### Getting started

1. git clone https://github.com/ChenPaulYu/flask-socailWeb.git
2. cd flask-socialWeb
3. virtiualenv env
4. source activate env
5. pip install -r requirement.txt
6. python app.py


### Deploy to heroku

1. git push heroku master
2. heroku ps:scale web=1
3. heroku open

[Reference](https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app)