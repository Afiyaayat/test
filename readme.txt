pip install -r requirements.txt


env
---
python -m venv p_env
p_env\Scripts\activate
pip install -r requirements.txt



https://covid19cu.herokuapp.com/

heroku login

git add .
git commit -am "make it better"
heroku config:set DISABLE_COLLECTSTATIC=1
git push heroku master
heroku run python manage.py migrate

heroku run 'bower install --config.interactive=false;grunt prep;python manage.py collectstatic --noinput'
heroku config:unset DISABLE_COLLECTSTATIC

heroku run python manage.py collectstatic


## Update ##
heroku login
git add .
git commit -am "make it better"
git push heroku master