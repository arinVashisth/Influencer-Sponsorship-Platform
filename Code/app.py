# 22f3001906 
#  xykq npqo djlb nbvy
# Importing work is here
import os
import mutagen
from mutagen import mp3,mp4,ogg
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.ogg import OggFileType
from worker import *
from tasks import *
import uuid
# audio=mutagen(file_name)
# audio.length()
import matplotlib.pyplot as plt
from io import BytesIO
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash,generate_password_hash
from flask import Flask,render_template,request,redirect,url_for,flash,session,abort,send_file,jsonify,send_from_directory
import json
import flask_excel as excel
from celery.result import AsyncResult
from modal import * # importing from modal
from sqlalchemy import func
from flask_mail import Message
from flask_mail import Mail
from cache import *
# from mail import send_email
from celery import shared_task
import flask_excel as excel
from flask_login import login_user,login_required, logout_user,current_user
from celery.schedules import crontab
from flask_security import Security,SQLAlchemyUserDatastore,auth_required, roles_required



############################################################################################################
#curr_dir = os.path.abspath(os.path.dirname(__file__))  # Directory Path
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///iescp.sqlite3" # Database connection for using database values
app.config['SECRET_KEY'] = 'mysecret' # Admin session available
app.config ['UPLOAD_FOLDER'] = 'static/uploads'

############################################################################################################

app.config["SECURITY_PASSWORD_SALT"] = "saltistasty"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"]  = False
app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Authenticated-Token"
app.config["MAIL_SERVER"]= 'smtp.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "iescpv2@gmail.com" 
app.config["MAIL_PASSWORD"] = "xykq npqo djlb nbvy"
app.config["MAIL_USE_TLS"]= True
app.config["MAIL_USE_SSL"]= False

############################################################################################################
app.config["CACHE_TYPE"]= "RedisCache"
app.config["CACHE_REDIS_HOST"]= "localhost"
app.config["CACHE_REDIS_PORT"]= 6379
app.config["CACHE_REDIS_DB"]= 3
app.config["CACHE_REDIS_TIMEOUT"]= 300
############################################################################################################
datastore = SQLAlchemyUserDatastore(db,Influencer,Role)
app.security = Security(app,datastore)
mail=Mail()

# cache.init_app(app)
app.app_context().push()
db.init_app(app)
celery_app=celery_init_app(app)
excel.init_excel(app)
mail=Mail()
mail.init_app(app)
mail.init_app(app)

############################################################################################################


##########################################   Celery Redis SECTIONS  ##############################################





@app.get('/download-csv')
def download_csv():
    task = create_camp_csv.delay()
    return jsonify({"task-id":task.id})

@app.get('/get-csv/<string:task_id>')
def get_csv(task_id):
    res = AsyncResult(task_id)
    if res.ready():
        filename = res.result
        return send_file(filename,as_attachment=True)
    else:
        return jsonify({"Message":"Task-Pending"}) , 404


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab( hour=14, minute=44),
        generate_monthly_report.s(),
    )

@celery_app.on_after_configure.connect
def setup_periodic_tasksss(sender, **kwargs):
    influencers = (db.session.query(Influencer).join(Influencer.ad_requests)
        .filter(AdRequest.status == 'pending')
        .distinct()
        .all())
    
    for influencer in influencers:
        # Schedule one-time task to send reminder
        sender.add_periodic_task(
        crontab(hour=15, minute=2, day_of_week='mon'),
        send_daily_rem.s(influencer.email,'Happy Sunday', influencer.name),
    )

##########################################   API SECTIONS  ##############################################



@app.route('/api/campaigns/<int:id>/inappropriate', methods=['POST'])
@cache.cached(timeout=50)
def mark_campaign_inappropriate(id):
    try:
        campaign = Campaign.query.get(id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404

        # Mark the campaign as inappropriate
        campaign.inappropriate = True  # Add this field to your Campaign model if it doesn't exist
        db.session.commit()

        return jsonify({'message': 'Campaign marked as inappropriate'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/posts/<int:id>/inappropriate', methods=['POST'])
def mark_post_inappropriate(id):
    try:
        post = Post.query.get(id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        # Mark the campaign as inappropriate
        post.inappropriate = True  # Add this field to your Campaign model if it doesn't exist
        db.session.commit()

        return jsonify({'message': 'Post marked as inappropriate'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/notify/<string:name>',methods=["POST","GET"])
def notify(name):
    spon=Sponsor.query.filter_by(company_name=name).first()

    camps=Campaign.query.filter_by(sponsor_id=spon.id,inappropriate=1).all()
    return render_template('sponsor_notif.html',camps=camps,spon=spon)

@app.route('/influ_notify/<int:n>',methods=["POST","GET"])
def influ_notify(n):
    influ=Influencer.query.filter_by(id=n).first()

    posts=Post.query.filter_by(influencer_id=influ.id,inappropriate=1).all()
    return render_template('influ_notify.html',posts=posts,influ=influ)

@app.route('/fixpost/<int:n>/<int:id>',methods=["GET","POST"])
def fixpost(n,id):
    influ=Influencer.query.filter_by(id=n).first()
    post=Post.query.filter_by(id=id).first()
    check_desc=post.description
    check_media=post.media_url
    count1=2
    if request.method == "POST":
        count2=0
        Cover_art = request.files['media']
        if Cover_art:
            filename2 = secure_filename(Cover_art.filename)
            file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            Cover_art.save(file_path2)
            if file_path2==check_media:
                count2+=1
            post.profile = file_path2
        desc=request.form.get('description')
        if desc:
            if desc == check_desc:
                count2+=1
            post.description=desc
        if count2==count1:
            pass
        else:
            post.inappropriate=False
        db.session.commit()
        return redirect(url_for('influ_notify',n=influ.id))
    return render_template('/fix/fixinflu.html',n=influ,post=post)

@app.route('/fixcamp/<string:name>/<int:id>',methods=["GET","POST"])
def fixcamp(name,id):
    spon=Sponsor.query.filter_by(company_name=name).first()
    camp=Campaign.query.filter_by(id=id).first()
    check_name=camp.name
    check_desc=camp.description
    check_goal=camp.goals
    count1=3
    if request.method == "POST":
        count2=0
        name=request.form.get('name')
        if name:
            if name==check_name:
                count2+=1
            camp.name=name
        description=request.form.get('description')
        if description:
            if description==check_desc:
                count2+=1
            camp.description=description
        goals=request.form.get('goals')
        if goals:
            if goals==check_goal:
                count2+=1
            camp.goals=goals
        if count2==count1:
            pass
        else:
            camp.inappropriate=False
        db.session.commit()
        return redirect(url_for('notify',name=spon.company_name))
    return render_template('/fix/fixspon.html',sname=spon.company_name,campaign=camp)



@app.route('/api/admin/statistics', methods=['GET'])
def admin_statistics():
    try:
        total_influencers = Influencer.query.count()
        total_sponsors = Sponsor.query.count()
        total_active_campaigns = len(Campaign.query.filter_by(visibility=1).all())
        total_inactive_campaigns = len(Campaign.query.filter_by(visibility=0).all())
        total_campaigns = Campaign.query.count()
        total_adreqeusts = AdRequest.query.count()
        total_posts = Post.query.count()
        total_earnings = db.session.query(db.func.sum(AdRequest.payment_amount)).filter(AdRequest.status == "Completed").scalar()
        media_types = db.session.query(Post.media_type).distinct().all()
        media_types = [media[0] for media in media_types]
        media_counts = [Post.query.filter(Post.media_type == media_type).count() for media_type in media_types]

        plt.figure(figsize=(8, 8))
        plt.pie(media_counts, labels=media_types, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Media Types')

        pie_chart_stream = BytesIO()
        plt.savefig(pie_chart_stream, format='png')
        pie_chart_stream.seek(0)
        plt.clf()

        pie_chart_filename = 'pie_chart.png'
        with open(f'./static/{pie_chart_filename}', 'wb') as f:
            f.write(pie_chart_stream.getvalue())

        influencers = db.session.query(Influencer).all()
        influencer_names = [influencer.name for influencer in influencers]
        influencer_post_counts = [len(influencer.posts) for influencer in influencers]

        plt.figure(figsize=(12, 8))
        plt.bar(influencer_names, influencer_post_counts, color='lightcoral')
        plt.title('Total Posts per Influencer')
        plt.xlabel('Influencer')
        plt.ylabel('Number of Posts')
        plt.xticks(rotation=45, ha='right')

        influencer_posts_stream = BytesIO()
        plt.savefig(influencer_posts_stream, format='png')
        influencer_posts_stream.seek(0)
        plt.clf()

        influencer_posts_filename = 'influencer_posts.png'
        with open(f'./static/{influencer_posts_filename}', 'wb') as f:
            f.write(influencer_posts_stream.getvalue())

        top_influencers = db.session.query(Influencer).order_by(Influencer.reach.desc()).limit(5).all()
        top_influencer_names = [influencer.name for influencer in top_influencers]
        top_influencer_reach = [influencer.reach for influencer in top_influencers]

        plt.figure(figsize=(10, 6))
        plt.bar(top_influencer_names, top_influencer_reach, color='mediumseagreen')
        plt.title('Top 5 Influencers by Reach')
        plt.xlabel('Influencer')
        plt.ylabel('Reach')
        plt.xticks(rotation=45, ha='right')

        reach_stream = BytesIO()
        plt.savefig(reach_stream, format='png')
        reach_stream.seek(0)
        plt.clf()

        reach_filename = 'top_influencers_reach.png'
        with open(f'./static/{reach_filename}', 'wb') as f:
            f.write(reach_stream.getvalue())

        ad_request_statuses = ['Pending', 'Approved', 'Rejected']
        ad_request_counts = [AdRequest.query.filter(AdRequest.status == status).count() for status in ad_request_statuses]

        plt.figure(figsize=(8, 8))
        plt.pie(ad_request_counts, labels=ad_request_statuses, autopct='%1.1f%%', startangle=140)
        plt.title('Ad Requests by Status')

        ad_requests_stream = BytesIO()
        plt.savefig(ad_requests_stream, format='png')
        ad_requests_stream.seek(0)
        plt.clf()

        ad_requests_filename = 'ad_requests_status.png'
        with open(f'./static/{ad_requests_filename}', 'wb') as f:
            f.write(ad_requests_stream.getvalue())

        sponsors = db.session.query(Sponsor).all()
        sponsor_names = [sponsor.company_name for sponsor in sponsors]
        sponsor_budgets = [sponsor.budget for sponsor in sponsors]

        plt.figure(figsize=(10, 8))
        plt.pie(sponsor_budgets, labels=sponsor_names, autopct='%1.1f%%', startangle=140)
        plt.title('Budget Allocation per Sponsor')

        budget_stream = BytesIO()
        plt.savefig(budget_stream, format='png')
        budget_stream.seek(0)
        plt.clf()

        budget_filename = 'budget_allocation.png'
        with open(f'./static/{budget_filename}', 'wb') as f:
            f.write(budget_stream.getvalue())
        return jsonify({
            'pie_chart_url': url_for('static', filename=pie_chart_filename),
            'influencer_posts_url': url_for('static', filename=influencer_posts_filename),
            'top_influencers_reach_url': url_for('static', filename=reach_filename),
            'ad_requests_status_url': url_for('static', filename=ad_requests_filename),
            'budget_allocation_url': url_for('static', filename=budget_filename),
            'total_influencers': total_influencers,
            'total_sponsors': total_sponsors,
            'total_campaigns': total_campaigns,
            'total_posts': total_posts,
            'total_earnings': total_earnings,
            'total_active_campaigns': total_active_campaigns,
            'total_inactive_campaigns': total_inactive_campaigns,
            'total_adreqeusts': total_adreqeusts
        })

    except Exception as e:
        print(1)
        return jsonify({"error": str(e)}), 500


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/influencers')
def get_influencers():
    influencers = Influencer.query.all()
    return jsonify([{
        'id': i.id,
        'name': i.name,
        'category': i.category,
        'niche': i.niche,
        'reach': i.reach
    } for i in influencers])

@app.route('/api/sponsors')
def get_sponsors():
    sponsors = Sponsor.query.all()
    return jsonify([{
        'id': s.id,
        'company_name': s.company_name,
        'industry': s.industry,
        'budget': s.budget,
        'approval' : s.approval
    } for s in sponsors])

@app.route('/api/campaigns')
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'start_date': c.start_date,
        'end_date': c.end_date,
        'budget': c.budget,
        'goals': c.goals,
        'inappropriate' : c.inappropriate
    } for c in campaigns])

@app.route('/api/posts')
@cache.cached(timeout=50)
def get_posts():
    posts = Post.query.all()
    return jsonify([{
        'id': p.id,
        'description': p.description,
        'likes': p.likes,
        'comments': p.comments,
        'media_type': p.media_type,
        'inappropriate': p.inappropriate
    } for p in posts])



############################################################################################################
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

############################################################################################################
# Genres=['Pop','Rock','Hip&Hop','Rap','Country','R & B','Folk','Jazz','Heavy Metal','EDM','Soul','Funk','Raggae','Disco','Punk Rock','Classical','House','Techno','Indie Rock']
Languages=['Hindi','English','Punjabi','Marathi','Bengali']
Ratings = [1,2,3,4,5]
status=["Pending","Approved","Rejected"]
Category=["Choose","Lifestyle","Food and Drink","Travel","Fitness and Health","Beauty","Technology","Finance and Business","Parenting","Entertainment","Education and Learning"]
Niche=["Choose","Eco-Friendly Living","Tech for Seniors","Urban Gardening","Historical Reenactment","Niche Fitness"]
ALLOWED_EXTENSIONS = {'.png','.jpg','.jpeg','.ogg','.mp3'}

def verify_user(list1,email_address,password):
    for i in list1:
        if i.email_address == email_address and i.password==password:
            return 1
    return 0

############################################################################################################
# WEBPAGE Functions start from here
""" HOME PAGE"""
def login_user(user):
    session['user_id'] = user.id

def logout_user():
    session.pop('user_id', None)

def is_authenticated_user():
    return 'user_id' in session



def is_authenticated_user():
    # Check if the user is authenticated by checking if their ID is stored in the session
    return 'user_id' in session
#######################################################  Admin PARTS HERE ##########################################################
@app.route('/admin/dashboard')
def Admin():
    return send_from_directory('static', 'admin_daashboard.html')

@app.route('/alogin',methods=["GET","POST"])
def ALogin():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        if email and password:
            if email=="admin@gmail.com" and password=="2004":
                return redirect(url_for('Admin'))
            else:
                return render_template('/admin/admin_login.html')
        else:
            return render_template('/admin/admin_login.html')
    return render_template("/admin/admin_login.html")

#######################################################  EDITING PARTS HERE ##########################################################

@app.route('/edit_camp/<int:id>/<string:sname>', methods=['GET'])
def edit_camp(id,sname):
    campaign = Campaign.query.get_or_404(id)
    return render_template('/edit/edit_campaign.html', campaign=campaign , sname=sname)

@app.route('/update_campaign/<int:campaign_id>/<string:sname>', methods=['POST'])
def update_campaign(campaign_id,sname):
    campaign = Campaign.query.get_or_404(campaign_id)
    visibility = request.form.get('visibility')
    campaign.visibility = int(visibility)
    campaign.name = request.form.get('name')
    campaign.description = request.form.get('description')
    campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    campaign.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    campaign.budget = float(request.form.get('budget'))
    campaign.goals = request.form.get('goals')
    
    db.session.commit()
    
    flash('Campaign updated successfully!')
    return redirect(url_for('campaigns',n=sname))

@app.route('/editInflu/<int:id>', methods=['GET', 'POST'])
def edit_influ(id):
    influencer = Influencer.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cate = request.form.get('category')
        niche = request.form.get('niche')
        gender = request.form.get('gender')
        
        if 'profile' in request.files:
            Cover_art = request.files['profile']
            if Cover_art:
                filename2 = secure_filename(Cover_art.filename)
                file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
                Cover_art.save(file_path2)
                influencer.profile = file_path2

        # Update fields if provided
        if name:
            influencer.name = name
        if email:
            influencer.email = email
        if password:
            influencer.password = password
        if cate:
            influencer.category = cate
        if niche:
            influencer.niche = niche
        if gender:
            influencer.gender = gender
        
        db.session.commit()
        return redirect(url_for('infu_profile', n=influencer.id))

    return render_template('/edit/edit_profile.html', influencer=influencer, Category=Category, Niche=Niche)

@app.route('/epost/<int:n>/<int:pos>',methods=["GET","POST"])
def Epost(n,pos):
    post=Post.query.filter_by(id=pos).first()
    if request.method=="POST":
        Cover_art = request.files['media']
        if Cover_art:
            filename2 = secure_filename(Cover_art.filename)
            file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
            Cover_art.save(file_path2)
            if file_path2:
                post.media_url=file_path2
        description=request.form.get('description')
        media_type=request.form.get('type')
        if description:
            post.description=description
        if media_type:
            post.media_type=media_type
        
        db.session.commit()
        return redirect(url_for('infu_profile',n=n))
    return render_template('/edit/epost.html',post=post,n=n)

@app.route('/edit_ad_request/<int:ad_request_id>/<string:sname>', methods=['GET'])
def edit_ad_request(ad_request_id,sname):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('/edit/edit_adrequest.html', ad_request=ad_request, spon=ad_request.campaign.sponsor,sname=sname)

@app.route('/update_ad_request/<int:ad_request_id>/<string:sname>', methods=['POST'])
def update_ad_request(ad_request_id,sname):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.requirements = request.form.get('requirements')
    ad_request.payment_amount = float(request.form.get('payment_amount'))
    ad_request.status = request.form.get('status')
    ad_request.conversation = request.form.get('conversation')
    db.session.commit()
    flash('Ad request updated successfully!')
    return redirect(url_for('influencer',n=sname))

#######################################################  ADDING PARTS HERE ##########################################################
@app.route('/add_post/<int:n>',methods=["GET","POST"])
def Add_post(n):
    influ=Influencer.query.filter_by(id=n).first()
    if request.method=="POST":
        Cover_art = request.files['media']
        filename2 = secure_filename(Cover_art.filename)
        file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
        Cover_art.save(file_path2)
        description=request.form.get('description')
        media_type=request.form.get('type')
        new_Post = Post(description=description, media_url=file_path2,influencer_id=n,media_type=media_type)
        db.session.add(new_Post)
        db.session.commit()
        return redirect(url_for('infu_profile',n=n))
    return render_template('/add/add_post.html',influ=influ)


@app.route('/add_campaign/<string:n>',methods=["GET","POST"])
def Add_campaign(n):
    spon=Sponsor.query.filter_by(company_name=n).first()
    if request.method=="POST":
        id=spon.id
        name=request.form.get('name')
        description=request.form.get('description')
        sdate_str=request.form.get('sdate')
        edate_str=request.form.get('edate')
        budget=request.form.get('budget')
        goals=request.form.get('goal')
        sdate = datetime.strptime(sdate_str, '%Y-%m-%d').date()
        edate = datetime.strptime(edate_str, '%Y-%m-%d').date()
        new_Camp = Campaign(name=name,description=description,start_date=sdate,end_date=edate,budget=budget,goals=goals,sponsor_id=id)
        db.session.add(new_Camp)
        db.session.commit()
        return redirect(url_for('campaigns',n=n))

    return render_template('/add/add_campaign.html',spon=spon)

@app.route('/addreq/<int:n>/<string:name>', methods=['GET', 'POST'])
def addreq(n, name):
    no = Influencer.query.filter_by(id=n).first()
    spon = Sponsor.query.filter_by(company_name=name).first()
    camp = Campaign.query.all()
    if request.method == 'POST':
        requirements = request.form.get('require')
        payment_amount = request.form.get('payment_amount')
        campaign = request.form.get('campaign')
        message = request.form.get('message')
        campaign_obj = Campaign.query.filter_by(name=campaign).first()
        new_ad_request = AdRequest(
            requirements=requirements,
            payment_amount=payment_amount,
            campaign_id=campaign_obj.id,
            influencer_id=no.id,
            conversation=json.dumps([{"user": "Sponsor", "message": message}])
        )
        db.session.add(new_ad_request)
        db.session.commit()
        return redirect(url_for('influencer', n=spon.company_name))
    conversation = []
    return render_template('/add/add_reqeust.html', n=spon, no=no, camp=camp, conversation=conversation, ad_request_id=0,m=0)

@app.route('/ad_request/<int:ad_request_id>/<int:m>', methods=['GET', 'POST'])
def ad_request(ad_request_id,m):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    camp_id=ad_request.campaign_id
    camp=Campaign.query.filter_by(id=camp_id).first()
    spon_id=camp.sponsor_id
    spons=Sponsor.query.filter_by(id=spon_id).first()
    spon_name=spons.company_name
    if m!=1:
        m=0
    if request.method == 'POST':
        new_message = request.form.get('message')
        user_type = request.form.get('user_type')
        
        if ad_request.conversation:
            conversation = json.loads(ad_request.conversation)
        else:
            conversation = []
        if user_type == "Influencer":
            m=0
        else:
            m=1
        conversation.append({"user": user_type, "message": new_message})
        ad_request.conversation = json.dumps(conversation)
        db.session.commit()
        return redirect(url_for('ad_request', ad_request_id=ad_request.id,m=m))
    influ=Influencer.query.filter_by(id=ad_request.influencer_id).first()
    if influ:
        l=1
    conversation = json.loads(ad_request.conversation) if ad_request.conversation else []
    return render_template('/add/add_reqeust.html', ad_request=ad_request, conversation=conversation,l=l,influ=influ,m=m,spon=spon_name)

@app.route('/add_comment/<int:post_id>/<int:previnflu>', methods=['POST'])
def add_comment(post_id, previnflu):
    post = Post.query.get_or_404(post_id)
    influencer_id = post.influencer_id
    comment_text = request.form.get('comment')
    if not comment_text or not influencer_id:
        flash('Comment or influencer information missing!')
        return redirect(url_for('profile', n=influencer_id, previnflu=previnflu))
    if post.comments:
        comments = json.loads(post.comments)
    else:
        comments = []
    previnflu_name = Influencer.query.filter_by(id=previnflu).first()
    if previnflu_name is None:
        flash('Influencer not found!')
        return redirect(url_for('profile', n=influencer_id, previnflu=previnflu))
    comments.append({
        "influencer_name": previnflu_name.name,
        "comment": comment_text
    })

    # Convert comments back to JSON and update the post
    post.comments = json.dumps(comments)
    db.session.commit()

    flash('Comment added successfully!')
    return redirect(url_for('profile', n=influencer_id, previnflu=previnflu))



#######################################################  Deleting PARTS HERE ##########################################################

@app.route('/delpost/<int:n>/<int:po>',methods=["GET","POST"])
@cache.cached(timeout=50)
def delpost(n,po):
    pos=Post.query.filter_by(id=po).first()
    db.session.delete(pos)
    db.session.commit()
    return redirect(url_for('infu_profile',n=n))

@app.route('/delcamp/<int:n>/<string:na>',methods=['GET','POST'])
@cache.cached(timeout=50)
def delcamp(n,na):
    spon=Campaign.query.filter_by(id=n).first()
    for i in spon.ad_requests :
        db.session.delete(i)
    db.session.delete(spon)
    db.session.commit()
    return redirect(url_for('campaigns',n=na))


@app.route('/delete_comment/<int:post_id>/<int:comment_id>', methods=['POST'])
@cache.cached(timeout=50)
def delete_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    print(comment_id)
    
    # Check if the post has comments
    if post.comments:
        comments = json.loads(post.comments)
        
        # Delete the comment based on index
        if 0 <= comment_id < len(comments):
            print(comments)
            influ=comments[comment_id]['influencer_name']
            comments.pop(comment_id)
            influe=Influencer.query.filter_by(name=influ).first()
            post.comments = json.dumps(comments)
            db.session.commit()
            flash('Comment deleted successfully!')
        else:
            flash('Comment not found!')
    else:
        flash('No comments to delete!')

    return redirect(url_for('profile', n=post.influencer_id, previnflu=influe.id))

#######################################################  Authentication PARTS HERE ##########################################################
@app.route('/',methods=["GET","POST"])
def Login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        influ=Influencer.query.filter_by(email=email,password=password).first()
        spon=Sponsor.query.filter_by(company_name=email,password=password).first()
        try:
            if influ:
                fo=Follower.query.filter_by(follower_id=influ.id).all()
                fl=Follower.query.filter_by(following_id=influ.id).all()
                posts=influ.posts
                adr=AdRequest.query.all()
                return render_template('influ_after_login.html',influ=influ,posts=posts,fo=fo,fl=fl,adr=adr)
            elif spon:
                camp=spon.campaigns
                if spon.approval==0:
                    return render_template('login.html')
                adr=AdRequest.query.all()
                return render_template('spon_after_login.html',spon=spon,camp=camp,adr=adr)
            else:
                return render_template('login.html')
        except:
            abort(404)
    errors=[]
    return render_template("login.html")


@app.route('/signupInflu', methods=['GET', 'POST'])
def signup_influ():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cate = request.form.get('category')
        niche = request.form.get('niche')
        gender = request.form.get('gender')
        Cover_art = request.files['profile']
        filename2 = secure_filename(Cover_art.filename)
        file_path2 = os.path.join(app.config['UPLOAD_FOLDER'],filename2)
        Cover_art.save(file_path2)
        # Check if the username or email already exists in the database
        existing_user = Influencer.query.filter_by(name=name).first()
        existing_email = Influencer.query.filter_by(email=email).first()
        if existing_user:
            return 'Username already exists!'
        elif existing_email:
            return 'Email already exists!'
        else:
            # Create a new user and add it to the database
            new_influencer = Influencer(name=name, email=email, password=password,profile=file_path2,category=cate,niche=niche,gender=gender)
            db.session.add(new_influencer)
            db.session.commit()
            return redirect(url_for('Login'))

    return render_template('signup_infu.html',Category=Category,Niche=Niche)

@app.route('/signupSpon', methods=['GET', 'POST'])
def signup_Spon():
    if request.method == 'POST':
        company_name = request.form.get('comp_name')
        industry = request.form.get('industry')
        email = request.form.get('email')
        password = request.form.get('password')
        budget = request.form.get('budget')
        existing_user = Sponsor.query.filter_by(company_name=company_name).first()
        if existing_user:
            return 'Username already exists!'
        else:
            # Create a new user and add it to the database
            new_sponsor = Sponsor(company_name=company_name,email=email, industry=industry, password=password,budget=budget)
            db.session.add(new_sponsor)
            db.session.commit()
            message="You will be notified When Your login is approved It will take 1 hour Maximum."
            print("MAIL_USERNAME:", app.config["MAIL_USERNAME"])
            send_email(user=new_sponsor,subject="Approval Pending!!",body=message)
            return redirect(url_for('Login'))

    return render_template('signup_spo.html')

#######################################################  SEARCHING PARTS HERE ##########################################################

@app.route('/search_influencers/<int:n>', methods=['GET'])
def search_influencers(n):

    query = request.args.get('query', '')
    influencers = Influencer.query.filter(
        (Influencer.name.ilike(f'%{query}%')) |
        (Influencer.category.ilike(f'%{query}%'))
    ).all()
    influ=Influencer.query.filter_by(id=n).first()
    fo=Follower.query.filter_by(follower_id=influ.id).all()
    return render_template('influs.html',influencers=influencers,n=n,influ=influ,fo=fo)

@app.route('/search_campaigns/<int:influ>', methods=['GET'])
def search_campaigns(influ):
    search_query = request.args.get('search_query', '')
    influ=Influencer.query.filter_by(id=influ).first()
    campaigns = Campaign.query.filter(
        Campaign.name.ilike(f'%{search_query}%') |
        Campaign.description.ilike(f'%{search_query}%')
    ).all()
    return render_template('campiagn.html', campai=campaigns, influ=influ)

@app.route('/influencer/<company_name>', methods=['GET'])
def influencer_page(company_name):
    search_term = request.args.get('search', '')
    list1=[]
    spon = Sponsor.query.filter_by(company_name=company_name).first_or_404()
    if search_term:
        filtered_influencers = Influencer.query.filter(
            (Influencer.name.ilike(f'%{search_term}%')) |
            (Influencer.category.ilike(f'%{search_term}%')) |
            (Influencer.niche.ilike(f'%{search_term}%'))
        ).all()
    else:
        filtered_influencers = Influencer.query.all()
    flue=filtered_influencers
    for i in flue:
        list1.append(i.ad_requests)
    return render_template('influ1234.html', spon=spon, flue=filtered_influencers, list1=list1)
#######################################################  MAIN PARTS HERE ##########################################################


@app.route('/influencer/<string:n>',methods=['GET','POST'])
def influencer(n):
    flue=Influencer.query.all()
    list1=[]
    for i in flue:
        list1.append(i.ad_requests)
    print(list1)
    spon=Sponsor.query.filter_by(company_name=n).first()
    return render_template('influ1234.html',flue=flue,spon=spon,list1=list1)

@app.route('/infuPro/<int:n>',methods=["POST","GET"])
def infu_profile(n):
    influ=Influencer.query.filter_by(id=n).first()
    posts=influ.posts
    fo=Follower.query.filter_by(follower_id=influ.id).all()
    fl=Follower.query.filter_by(following_id=influ.id).all()
    adr=AdRequest.query.all()
    return render_template('influ_after_login.html',influ=influ,posts=posts,fo=fo,fl=fl,adr=adr)

@app.route('/sponPro/<string:n>',methods=["POST","GET"])
def spon_profile(n):
    spon=Sponsor.query.filter_by(company_name=n).first()
    camp=spon.campaigns
    adr=AdRequest.query.all()
    return render_template('spon_after_login.html',spon=spon,camp=camp,adr=adr)


@app.route('/campaigns/<string:n>',methods=["GET","POST"])
def campaigns(n):
    spon=Sponsor.query.filter_by(company_name=n).first()
    camp=spon.campaigns
    return render_template('my_campaigns.html',camp=camp,spon=spon)

@app.route('/campaingsss/<int:n>',methods=["GET","POST"])
def camp(n):
    influ=Influencer.query.filter_by(id=n).first()
    campai=Campaign.query.all()
    return render_template('campiagn.html',influ=influ,campai=campai)

@app.route('/pubpri/<string:n>/<int:m>',methods=["GET","POST"])
def Pubpri(n,m):
    camp=Campaign.query.filter_by(id=m).first()
    if(camp.visibility==0):
        camp.visibility=1
    else:
        camp.visibility=0
    db.session.commit()
    return redirect(url_for('campaigns',n=n))

@app.route('/influsearch/<int:n>',methods=["POST","GET"])
def influencerssearch(n):
    influencers=Influencer.query.all()
    influ=Influencer.query.filter_by(id=n).first()
    print(influencers[0])
    fo=Follower.query.filter_by(follower_id=influ.id).all()
    return render_template('influs.html',influencers=influencers,n=n,influ=influ,fo=fo)



@app.route('/profile/<int:n>/<int:previnflu>',methods=["GET","POST"])
def profile(n,previnflu):
    previnfluInflu=Influencer.query.filter_by(id=previnflu).first()
    influ=Influencer.query.filter_by(id=n).first()
    posts=influ.posts
    folwrid=Follower.query.filter_by(follower_id=previnflu,following_id=influ.id).first()
    if folwrid:
        l=1
    else:
        l=0
    fo=Follower.query.filter_by(follower_id=influ.id).all()
    fl=Follower.query.filter_by(following_id=influ.id).all()
    for post in posts:
        if post.comments:
            post.comments = json.loads(post.comments)
    return render_template('influencer.html',influ=influ,previnflu=previnflu,previnfluInflu=previnfluInflu,posts=posts,l=l,fo=fo,fl=fl)


@app.route('/follow/<int:folw>/<int:folr>',methods=["GET","POST"])
def follow(folw,folr):
    influ=Influencer.query.filter_by(id=folw).first()
    new_follower = Follower(follower_id=folr,following_id=folw)
    db.session.add(new_follower)
    inf=Influencer.query.filter_by(id=folw).first()
    inf.reach+=1
    db.session.commit()
    return redirect(url_for('profile',n=influ.id,previnflu=folr))

@app.route('/unfollow/<int:folw>/<int:folr>',methods=["GET","POST"])
def Unfollow(folw,folr):
    influ=Influencer.query.filter_by(id=folw).first()

    new_follower = Follower.query.filter_by(follower_id=folr,following_id=influ.id).first()
    db.session.delete(new_follower)
    inf=Influencer.query.filter_by(id=folw).first()
    inf.reach-=1
    db.session.commit()
    return redirect(url_for('profile',n=influ.id,previnflu=folr))


@app.route('/like/<int:like>/<int:n>/<int:prev>',methods=["GET","POST"])
def like(like,n,prev):
    influe=Influencer.query.filter_by(id=prev).first()
    pos=Post.query.filter_by(id=like).first()
    pos.likes+=1
    db.session.commit()
    return redirect(url_for('profile',n=n,previnflu=prev))

@app.route('/accrej/<int:id>/<int:n>')
def Accrej(id,n):
    if n==0:
        string="Rejected"
    elif n==1:
        string="Approved"
    adr=AdRequest.query.filter_by(id=id).first()
    influ=adr.influencer_id
    adr.status=string
    db.session.commit()
    return redirect(url_for('infu_profile',n=influ))


@app.route('/infustats/<int:influ_id>')
def infu_stats(influ_id):
    influencer = Influencer.query.get(influ_id)
    count=0
    for i in influencer.followers:
        count+=1
    total_followers = count
    total_posts = len(influencer.posts)
    average_likes = db.session.query(db.func.avg(Post.likes)).filter(Post.influencer_id == influ_id).scalar()
    average_comments = db.session.query(db.func.avg(Post.comments)).filter(Post.influencer_id == influ_id).scalar()
    total_earnings = db.session.query(db.func.sum(AdRequest.payment_amount)).filter(AdRequest.influencer_id == influ_id, AdRequest.status == "Completed").scalar()

    return render_template('influencer_stat.html', 
                           influ=influencer, 
                           total_followers=total_followers, 
                           total_posts=total_posts, 
                           average_likes=average_likes, 
                           average_comments=average_comments, 
                           total_earnings=total_earnings)


@app.route('/sponstats/<string:company_name>')
def spon_stats(company_name):
    sponsor = Sponsor.query.filter_by(company_name=company_name).first()
    
    if not sponsor:
        return "Sponsor not found", 404

    total_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).count()
    total_budget = sponsor.budget

    total_spent = db.session.query(func.sum(AdRequest.payment_amount))\
        .join(Campaign, AdRequest.campaign_id == Campaign.id)\
        .filter(Campaign.sponsor_id == sponsor.id, AdRequest.status == "Completed")\
        .scalar() or 0.0
    
    average_campaign_budget = db.session.query(func.avg(Campaign.budget))\
        .filter(Campaign.sponsor_id == sponsor.id)\
        .scalar() or 0.0

    total_influencers_engaged = db.session.query(func.count(func.distinct(AdRequest.influencer_id)))\
        .join(Campaign, AdRequest.campaign_id == Campaign.id)\
        .filter(Campaign.sponsor_id == sponsor.id)\
        .scalar() or 0

    return render_template(
        'sponsor_stat.html',
        spon=sponsor,
        total_campaigns=total_campaigns,
        total_budget=total_budget,
        total_spent=total_spent,
        average_campaign_budget=average_campaign_budget,
        total_influencers_engaged=total_influencers_engaged
    )


@app.route('/approve/<int:n>')
def approve(n):
    Spon=Sponsor.query.filter_by(id=n).first()
    name=Spon.company_name
    Spon.approval=1
    db.session.commit()
    text="""Dear"""+ name+ """, We are pleased to inform you that your sponsorship application has been approved!\n
            
            Thank you for choosing IESCVP as your partner. We are excited to work with you and support your initiatives.\n
            
            Next Steps:\n
            
            1. Login: You can now log in to your account using your registered credentials.\n
            2. Dashboard: Explore your dashboard to manage campaigns, view performance metrics, and more.\n
            3. Support: If you have any questions or need assistance, our support team is here to help. Feel free to reach out to us at iescpv2@gmail.com.\n
            4. Reminder: Please keep an eye on your Gmail for upcoming opportunities and updates. We look forward to a successful partnership.\n
            
            Thank you once again for joining IESCVP. We are thrilled to have you on board!\n
            
            Best regards,\n
            IESCVP\n
            ADMIN\n
            ADMIN\n
            iescpv2@gmail.com"""
    send_email(user=Spon,subject="Approved!!!",body=text)
    return redirect(url_for('Admin'))


def send_email(user, subject, body):
    global mail
    msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[user.email])
    msg.body = body
    mail.send(msg)


if __name__ == "__main__":
    app.run(debug = True)
    app.app_context().push()
