###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError# Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy

## App setup code
app = Flask(__name__)

app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY']= 'This is probably the most secure it gets rn'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost/mattramMidterm"

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################




##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

##while tweets:hashtags would typically have a many:many relationship, since a many:one relationship is required for the midterm I am treating them as such, and tweets will only reference the hashtag that is searched rather than any other hashtags a tweet might have.
class Tweet(db.Model):
    __tablename__= "tweets"
    id =db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280))
    username= db.Column(db.String(64))
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.id'))
    def __repr__(self):
        return "{} posted by {} (#ID: {})".format(self.content, self.username, self.hashtag_id)

class Hashtag(db.Model):
    __tablename__= "hashtags"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), unique=True)
    tweets= db.relationship('Tweet', backref='Hashtag')
    def __repr__(self):
        return "#{} (ID: {})".format(self.content, self.id)



###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

class indexForm(FlaskForm):
    content = StringField("Please submit a tweet(280 character max):", validators=[Required()])
    username = StringField("Enter username:", validators=[Required()])
    hashtag = StringField("Please enter a hashtag for your tweet(no spaces)!:", validators=[Required()])
    def validate_hashtag(form, field):
        invalid = [' ']
        for ch in field.data:
            if ch in invalid:
                raise ValidationError("Please do not include spaces.")
    submit = SubmitField('Submit')

class hashtagForm(FlaskForm):
    hashtag = StringField("Please enter the hashtag you'd like to search(no spaces!):", validators=[Required()])
    def validate_hashtag(form, field):
        invalid = [' ']
        for ch in field.data:
            if ch in invalid:
                raise ValidationError("Please do not include spaces.")
    submit = SubmitField('Submit')

#######################
###### VIEW FXNS ######
#######################

@app.route('/', methods=['GET','POST'])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        name = form.name.data
        newname = Name()
        newname.name = name
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)

@app.route('/index', methods=['GET', 'POST'])
def index():
    form = indexForm()
    if form.validate_on_submit():
        tweetHashtag = form.hashtag.data
        tweetContent = form.content.data
        tweetUsername = form.username.data
        hashtag = Hashtag.query.filter_by(content=tweetHashtag).first()
        if not hashtag:
            hashtag = Hashtag(content=tweetHashtag)
            db.session.add(hashtag)
            db.session.commit()
            flash("New hashtag added")
        newtweet = Tweet(content=tweetContent, username=tweetUsername, hashtag_id=hashtag.id)
        db.session.add(newtweet)
        db.session.commit()
        flash("Tweet added")
        return redirect(url_for('index'))
    return render_template('index.html',form=form)

@app.route('/tweetlist')
def alltweets():
    tweets=Tweet.query.all()
    return render_template('tweets.html', tweets = tweets)

@app.route('/hashtaglist')
def allhashtags():
    hashtags=Hashtag.query.all()
    return render_template('hashtags.html', hashtags = hashtags)

@app.route('/search/<hashtag>', methods=['GET','POST'])
def search(hashtag):
    baseurl = "https://api.twitter.com/1.1/statuses/update.json"
    params ={}
    params["q"] = hashtag
    obj = requests.get(baseurl, params = params)
    dic = json.loads(o.text)

    statuses = dic['statuses']

    return render_template('search.html', statuses=statuses)


## Error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



## Code to run the application...
if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True, debug=True)
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
